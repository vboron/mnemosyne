"""Stateful audio player that can drive the Now Playing screen.

The old ``play_track`` shelled out to ``cvlc --play-and-exit`` and blocked with no
way to observe or control it. This engine keeps a queue and live transport state
(position, duration, play/pause, next/prev) that the web layer streams over a
WebSocket.

Two backends:

* ``VlcBackend``      — real audio via ``python-vlc`` (used on the Pi).
* ``SimulatedBackend`` — no audio; advances a clock so the whole UI + WebSocket
  loop is testable on a dev machine with no VLC installed.

Backend is chosen by ``MNEMOSYNE_PLAYER_BACKEND`` = ``vlc`` | ``simulated`` |
``auto`` (default). ``auto`` uses VLC when importable, else simulated.
"""

import os
import threading
import time

from memory.session import create_session, end_session
from playback.library import find_track, get_album_tracks, get_track, resolve_media_path


# --------------------------------------------------------------------------- #
# Backends
# --------------------------------------------------------------------------- #

class SimulatedBackend:
    """A silent stand-in that advances position by wall-clock time."""

    name = "simulated"

    def __init__(self):
        self._duration = 0.0
        self._pos_base = 0.0        # position captured at last play/seek
        self._t0 = None             # monotonic time when play/seek happened
        self._playing = False

    def _now(self):
        if self._playing and self._t0 is not None:
            return min(self._duration, self._pos_base + (time.monotonic() - self._t0))
        return self._pos_base

    def load(self, path, duration_seconds):
        self._duration = float(duration_seconds or 180)
        self._pos_base = 0.0
        self._t0 = None
        self._playing = False

    def play(self):
        if not self._playing:
            self._pos_base = self._now()
            self._t0 = time.monotonic()
            self._playing = True

    def pause(self):
        self._pos_base = self._now()
        self._playing = False
        self._t0 = None

    def stop(self):
        self._pos_base = 0.0
        self._playing = False
        self._t0 = None

    def seek(self, seconds):
        self._pos_base = max(0.0, min(self._duration, float(seconds)))
        self._t0 = time.monotonic() if self._playing else None

    @property
    def position_seconds(self):
        return self._now()

    @property
    def duration_seconds(self):
        return self._duration

    @property
    def is_playing(self):
        return self._playing

    @property
    def finished(self):
        return self._duration > 0 and self._now() >= self._duration


class VlcBackend:
    """Real playback via python-vlc. Imported lazily so this module loads anywhere."""

    name = "vlc"

    def __init__(self):
        import vlc  # noqa: F401  (raises ImportError if unavailable -> auto fallback)

        self._vlc = vlc
        self._instance = vlc.Instance("--no-video")
        self._player = self._instance.media_player_new()
        self._fallback_duration = 0.0

    def load(self, path, duration_seconds):
        media = self._instance.media_new_path(path)
        self._player.set_media(media)
        self._fallback_duration = float(duration_seconds or 0)

    def play(self):
        self._player.play()

    def pause(self):
        # set_pause(1) pauses without toggling; avoids play->pause race.
        self._player.set_pause(1)

    def stop(self):
        self._player.stop()

    def seek(self, seconds):
        self._player.set_time(int(seconds * 1000))

    @property
    def position_seconds(self):
        ms = self._player.get_time()
        return ms / 1000.0 if ms and ms > 0 else 0.0

    @property
    def duration_seconds(self):
        ms = self._player.get_length()
        if ms and ms > 0:
            return ms / 1000.0
        return self._fallback_duration

    @property
    def is_playing(self):
        return bool(self._player.is_playing())

    @property
    def finished(self):
        return self._player.get_state() == self._vlc.State.Ended


def _make_backend():
    choice = os.environ.get("MNEMOSYNE_PLAYER_BACKEND", "auto").lower()

    if choice == "simulated":
        return SimulatedBackend()

    if choice in ("vlc", "auto"):
        try:
            return VlcBackend()
        except Exception:
            if choice == "vlc":
                raise
            return SimulatedBackend()

    return SimulatedBackend()


# --------------------------------------------------------------------------- #
# Engine
# --------------------------------------------------------------------------- #

class PlayerEngine:
    def __init__(self, backend=None):
        self._lock = threading.RLock()
        self._backend = backend or _make_backend()
        self._queue = []
        self._index = -1
        self._session_id = None
        self._ended = False

    @property
    def session_id(self):
        return self._session_id

    # -- queue loading ------------------------------------------------------ #

    def _load_current(self, autoplay=True):
        self._ended = False
        track = self._queue[self._index]
        path = resolve_media_path(track.get("flac_path"))
        track["resolved_path"] = str(path) if path else None
        track["missing"] = not (path and path.exists())

        self._backend.load(track.get("resolved_path"), track.get("duration_seconds"))
        self._start_session(track)

        if autoplay and not track["missing"]:
            self._backend.play()

    def _start_session(self, track):
        # Record the listen; never let a DB hiccup break playback.
        self._end_session()
        try:
            self._session_id = create_session(
                album_id=track.get("album_id"),
                track_id=track.get("id"),
                mode="listen",
            )
        except Exception:
            self._session_id = None

    def _end_session(self):
        if self._session_id is not None:
            try:
                end_session(self._session_id)
            except Exception:
                pass
            self._session_id = None

    def play_tracks(self, tracks, start=0):
        tracks = [t for t in tracks if t]
        if not tracks:
            raise ValueError("No tracks to play.")
        with self._lock:
            self._queue = tracks
            self._index = max(0, min(start, len(tracks) - 1))
            self._load_current(autoplay=True)
            return self.state_unlocked()

    # -- public play entry points ------------------------------------------ #

    def play_search(self, term):
        track = find_track(term)
        if track is None:
            raise ValueError(f"No playable track found for: {term}")
        return self.play_tracks([track])

    def play_track_id(self, track_id):
        track = get_track(track_id)
        if track is None or not track.get("flac_path"):
            raise ValueError(f"Track not playable: {track_id}")
        return self.play_tracks([track])

    def play_album(self, album_id, start=0):
        return self.play_tracks(get_album_tracks(album_id), start=start)

    # -- transport ---------------------------------------------------------- #

    def toggle(self):
        with self._lock:
            if not self._queue:
                return self.state_unlocked()
            if self._backend.is_playing:
                self._backend.pause()
            else:
                self._backend.play()
            return self.state_unlocked()

    def pause(self):
        with self._lock:
            self._backend.pause()
            return self.state_unlocked()

    def play(self):
        with self._lock:
            if self._queue:
                self._ended = False
                self._backend.play()
            return self.state_unlocked()

    def stop(self):
        with self._lock:
            self._backend.stop()
            self._end_session()
            return self.state_unlocked()

    def next(self):
        """Manual skip forward: keep whatever play/pause state we were in.

        (Auto-advance at natural end of track is :meth:`_advance`, which always
        keeps playing.)
        """
        with self._lock:
            if self._index < len(self._queue) - 1:
                was_playing = self._backend.is_playing
                self._index += 1
                self._load_current(autoplay=was_playing)
            # At the last track a manual "next" is a no-op — stay put.
            return self.state_unlocked()

    def prev(self):
        with self._lock:
            was_playing = self._backend.is_playing
            # Restart current track if we're past the intro, else go back one.
            if self._backend.position_seconds > 3 or self._index <= 0:
                self._backend.seek(0)
                if was_playing:
                    self._backend.play()
            else:
                self._index -= 1
                self._load_current(autoplay=was_playing)
            return self.state_unlocked()

    def seek_fraction(self, fraction):
        with self._lock:
            fraction = max(0.0, min(1.0, float(fraction)))
            self._ended = False
            self._backend.seek(self._backend.duration_seconds * fraction)
            return self.state_unlocked()

    def _advance(self):
        # Auto-advance when a track finishes on its own: always keep playing.
        if self._index < len(self._queue) - 1:
            self._index += 1
            self._load_current(autoplay=True)
        else:
            # End of queue: keep the last track shown, mark as finished.
            self._backend.stop()
            self._end_session()
            self._ended = True
        return self.state_unlocked()

    # -- state -------------------------------------------------------------- #

    def state(self):
        with self._lock:
            return self.state_unlocked()

    def state_unlocked(self):
        # Auto-advance / end-of-queue when the current track finishes on its own.
        if self._queue and not self._ended and self._backend.finished:
            self._advance()

        track = self._queue[self._index] if self._queue and self._index >= 0 else None
        duration = self._backend.duration_seconds or (
            track.get("duration_seconds") if track else 0
        ) or 0

        if self._ended:
            position = duration
            progress = 1.0
            playing = False
        else:
            position = min(self._backend.position_seconds, duration) if duration else 0
            progress = (position / duration) if duration else 0.0
            playing = bool(self._backend.is_playing)

        return {
            "backend": self._backend.name,
            "playing": playing,
            "ended": self._ended,
            "has_track": track is not None,
            "track": _public_track(track),
            "position_seconds": round(position, 2),
            "duration_seconds": round(duration, 2),
            "progress": round(progress, 4),
            "has_next": bool(self._queue) and self._index < len(self._queue) - 1,
            "has_prev": bool(self._queue) and self._index > 0,
            "queue_length": len(self._queue),
            "queue_index": self._index,
        }


def _public_track(track):
    if track is None:
        return None
    return {
        "id": track.get("id"),
        "title": track.get("title"),
        "artist": track.get("artist"),
        "album": track.get("album"),
        "year": track.get("year"),
        "accession": track.get("accession"),
        "track_number": track.get("track_number"),
        "has_artwork": track.get("has_artwork", False),
        "missing": track.get("missing", False),
    }


# Process-wide singleton used by the web layer and the CLI.
engine = PlayerEngine()
