"""CLI playback entry point.

Delegates to the shared stateful :data:`playback.engine.engine` so the CLI and
the web Now Playing screen drive the *same* player. For CLI ergonomics this
blocks until the track finishes (mirroring the old ``cvlc --play-and-exit``).
"""

import time

from playback.engine import engine


def play_track(term):
    engine.play_search(term)
    session_id = engine.session_id

    state = engine.state()
    track = state.get("track")
    if track:
        print(f"Playing: {track.get('artist') or 'Unknown'} — {track.get('title')}")
        if track.get("missing"):
            print("(audio file not found on this machine — nothing will be heard)")
    print(f"Session: {session_id}")

    try:
        while True:
            state = engine.state()
            if not state["has_track"] or state["ended"]:
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        engine.stop()

    return session_id
