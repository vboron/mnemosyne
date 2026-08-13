"""Entry point for the native Mnemosyne UI.

    python -m ui.main                 # windowed 1280x800 (dev)
    python -m ui.main --fullscreen    # kiosk, for the Pi touchscreen

Backend selection is via ``MNEMOSYNE_PLAYER_BACKEND`` (see playback.engine):
``simulated`` on a dev machine, ``vlc`` on the Pi.
"""

import os
import sys

from PySide6 import QtCore, QtWidgets

from playback import library
from playback.engine import engine
from ui.now_playing import NowPlayingScreen


def _seed_default_track():
    """Load a sensible default so the screen isn't empty on launch (paused).

    Queue the whole disc the default track belongs to (not just the one track)
    so the ⏮/⏭ transport can actually move between tracks.
    """
    if engine.state()["has_track"]:
        return
    track = library.first_playable()
    if not track:
        return
    tracks = library.get_album_tracks(track["album_id"]) or [track]
    engine.play_tracks(tracks, start=0)
    engine.pause()


def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts, True)
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Mnemosyne")
    app.setApplicationDisplayName("Mnemosyne")

    _seed_default_track()

    screen = NowPlayingScreen()
    screen.resize(1280, 800)

    fullscreen = "--fullscreen" in sys.argv or os.environ.get("MNEMOSYNE_FULLSCREEN")
    if fullscreen:
        screen.showFullScreen()
    else:
        screen.show()

    # Dev conveniences (harmless in kiosk): F11 toggles fullscreen, Esc quits.
    def _key(event):
        if event.key() == QtCore.Qt.Key_Escape:
            app.quit()
        elif event.key() == QtCore.Qt.Key_F11:
            (screen.showNormal if screen.isFullScreen() else screen.showFullScreen)()
    screen.keyPressEvent = _key

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
