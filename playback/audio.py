"""Audio output routing for the appliance.

The Pi runs **PipeWire** (there is no ``pactl``), driven here with ``wpctl`` and
``pw-dump``; Bluetooth speakers via ``bluetoothctl``. A sink is identified by
two things:

* its PipeWire **node id** — passed to ``wpctl set-default`` so new streams and
  the system default follow it;
* its **node.name** — what VLC's PipeWire/pulse output targets, so we can move
  the *currently playing* audio live (see ``PlayerEngine.set_output_device``).

Everything is best-effort: on a dev machine without these tools the calls just
return empty/False and the UI hides the picker.
"""

import json
import os
import subprocess


def _env():
    env = os.environ.copy()
    # When launched from the labwc session this is already set; default it so
    # wpctl/pw-dump can still reach the user's PipeWire when run elsewhere.
    env.setdefault("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    return env


def _run(args, timeout=6):
    try:
        return subprocess.run(args, capture_output=True, text=True,
                              env=_env(), timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None


def available():
    """True if the PipeWire tooling is present (so the UI should show a picker)."""
    from shutil import which
    return which("pw-dump") is not None and which("wpctl") is not None


def _default_sink_id():
    r = _run(["wpctl", "inspect", "@DEFAULT_AUDIO_SINK@"])
    if not r or r.returncode != 0:
        return None
    for line in r.stdout.splitlines():
        line = line.strip()
        if line.startswith("id "):
            try:
                return int(line[3:].split(",")[0])
            except ValueError:
                return None
    return None


def _classify(name):
    n = name.lower()
    if "bluez" in n:
        return "bluetooth"
    if "hdmi" in n:
        return "hdmi"
    if "analog" in n or "headphone" in n or "pci" in n or "usb" in n:
        return "analog"
    return "other"


def list_sinks():
    """Available PipeWire audio outputs, default first.

    Each entry: ``{id, name, description, is_default, kind}``.
    """
    r = _run(["pw-dump"])
    if not r or r.returncode != 0:
        return []
    try:
        objs = json.loads(r.stdout)
    except (json.JSONDecodeError, ValueError):
        return []

    default = _default_sink_id()
    sinks = []
    for o in objs:
        props = (o.get("info") or {}).get("props") or {}
        if props.get("media.class") != "Audio/Sink":
            continue
        sid = o.get("id")
        name = props.get("node.name", "") or ""
        sinks.append({
            "id": sid,
            "name": name,
            "description": (props.get("node.description")
                           or props.get("node.nick") or name),
            "is_default": sid == default,
            "kind": _classify(name),
        })
    sinks.sort(key=lambda s: (not s["is_default"], s["description"]))
    return sinks


def set_default_sink(sink_id):
    """Point the system default at ``sink_id`` (new streams follow it)."""
    r = _run(["wpctl", "set-default", str(sink_id)])
    return bool(r and r.returncode == 0)


# -- Bluetooth --------------------------------------------------------------- #

def bluetooth_audio_devices():
    """Paired Bluetooth **audio** devices: ``{mac, name, connected}``.

    Lets the picker offer a disconnected speaker (e.g. the Ruark MR1) as a
    'connect me' entry even before it shows up as a sink.
    """
    r = _run(["bluetoothctl", "devices"])
    if not r or r.returncode != 0:
        return []
    devices = []
    for line in r.stdout.splitlines():
        parts = line.split(" ", 2)  # "Device <mac> <name>"
        if len(parts) < 3 or parts[0] != "Device":
            continue
        mac, name = parts[1], parts[2]
        info = _run(["bluetoothctl", "info", mac])
        if not info or "Audio Sink" not in info.stdout:
            continue
        devices.append({
            "mac": mac,
            "name": name,
            "connected": "Connected: yes" in info.stdout,
        })
    return devices


def connect_bluetooth(mac):
    """Connect a paired Bluetooth device. Blocking (can take ~10s)."""
    r = _run(["bluetoothctl", "connect", mac], timeout=25)
    if not r:
        return False
    return r.returncode == 0 or "Connection successful" in (r.stdout or "")
