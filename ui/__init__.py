"""Native (PySide6/Qt) touchscreen UI for the Mnemosyne appliance.

Runs directly on the Pi's labwc/Wayland session — no web server, no browser.
The screens read and drive the shared :data:`playback.engine.engine` in-process,
so a QTimer poll replaces the old WebSocket the web layer used.
"""
