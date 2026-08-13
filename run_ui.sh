#!/usr/bin/env bash
# Launch the native Mnemosyne touchscreen UI (PySide6/Qt on labwc/Wayland).
#
# Intended to be started from the labwc autostart on the Pi, where
# WAYLAND_DISPLAY / XDG_RUNTIME_DIR are already exported by the compositor.
# For a manual launch over SSH, export those first, e.g.:
#   WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/1000 ./run_ui.sh
set -euo pipefail
cd "$(dirname "$0")"

export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-wayland}"
export MNEMOSYNE_PLAYER_BACKEND="${MNEMOSYNE_PLAYER_BACKEND:-vlc}"

exec .venv/bin/python -m ui.main --fullscreen
