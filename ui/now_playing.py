"""The Now Playing screen — the native counterpart of ``now_playing.html``.

Polls the shared engine ~4Hz and pushes transport commands straight into it
(no HTTP, no WebSocket — same process).
"""

from PySide6 import QtCore, QtGui, QtWidgets

from playback import audio
from playback.engine import engine
from playback.library import artwork_path
from ui import theme
from ui.widgets import ScrubBar, WaveformBar


class _BtConnectWorker(QtCore.QThread):
    """Connect a Bluetooth speaker off the UI thread, then wait for its sink."""

    done = QtCore.Signal(dict)  # the new bluetooth sink, or {} on failure

    def __init__(self, mac, parent=None):
        super().__init__(parent)
        self._mac = mac

    def run(self):
        import time
        if audio.connect_bluetooth(self._mac):
            for _ in range(12):  # the PipeWire sink can lag the connection
                for sink in audio.list_sinks():
                    if sink["kind"] == "bluetooth":
                        self.done.emit(sink)
                        return
                time.sleep(0.5)
        self.done.emit({})


def _fmt(seconds):
    seconds = max(0, int(seconds or 0))
    return f"{seconds // 60}:{seconds % 60:02d}"


class NowPlayingScreen(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("screen")
        self.setStyleSheet(theme.STYLESHEET)
        self._last_track_id = None
        self._cover_pixmap = None
        self._build()

        self._bt_worker = None
        if audio.available():
            self._refresh_output_label()
        else:
            self.output.hide()

        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(250)  # ~4 Hz, matching the old WebSocket cadence
        self._timer.timeout.connect(self.refresh)
        self._timer.start()
        self.refresh()

    # -- construction ------------------------------------------------------- #

    def _build(self):
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(56, 40, 56, 48)
        outer.setSpacing(28)

        # top line: eyebrow + backend badge
        top = QtWidgets.QHBoxLayout()
        eyebrow = QtWidgets.QLabel()
        eyebrow.setObjectName("eyebrow")
        eyebrow.setText(
            f'NOW <span id="eyebrowStrong" '
            f'style="color:{theme.AMBER};">PLAYING</span>')
        eyebrow.setTextFormat(QtCore.Qt.RichText)
        eyebrow.setFont(theme.sans(13, letter_spacing=4))
        self.backend = QtWidgets.QLabel("—")
        self.backend.setObjectName("backend")
        self.backend.setFont(theme.mono(11, letter_spacing=2))

        self.output = QtWidgets.QPushButton("Output")
        self.output.setObjectName("output")
        self.output.setFont(theme.mono(11, letter_spacing=1))
        self.output.setCursor(QtCore.Qt.PointingHandCursor)
        self.output.setFocusPolicy(QtCore.Qt.NoFocus)
        self.output.clicked.connect(self._open_output_menu)

        top.addWidget(eyebrow)
        top.addStretch(1)
        top.addWidget(self.output)
        top.addSpacing(12)
        top.addWidget(self.backend)
        outer.addLayout(top)

        # body: cover + detail
        body = QtWidgets.QHBoxLayout()
        body.setSpacing(48)

        self.cover = QtWidgets.QLabel("NO COVER")
        self.cover.setObjectName("cover")
        self.cover.setFixedSize(340, 340)
        self.cover.setAlignment(QtCore.Qt.AlignCenter)
        self.cover.setFont(theme.mono(12, letter_spacing=2))
        body.addWidget(self.cover, 0, QtCore.Qt.AlignTop)

        detail = QtWidgets.QVBoxLayout()
        detail.setSpacing(10)

        self.artist = QtWidgets.QLabel("—")
        self.artist.setObjectName("artist")
        self.artist.setFont(theme.sans(15, QtGui.QFont.DemiBold, letter_spacing=3))

        self.title = QtWidgets.QLabel("Nothing loaded")
        self.title.setObjectName("title")
        self.title.setFont(theme.serif(46, QtGui.QFont.Medium))
        self.title.setWordWrap(True)

        self.album = QtWidgets.QLabel("")
        self.album.setObjectName("album")
        self.album.setFont(theme.serif(20))

        self.year = QtWidgets.QLabel("")
        self.year.setObjectName("year")
        self.year.setFont(theme.mono(12))

        self.missing = QtWidgets.QLabel(
            "Audio file not found on this machine — showing metadata only.")
        self.missing.setObjectName("missing")
        self.missing.setFont(theme.sans(12))
        self.missing.hide()

        detail.addWidget(self.artist)
        detail.addWidget(self.title)
        detail.addWidget(self.album)
        detail.addWidget(self.year)
        detail.addWidget(self.missing)
        detail.addSpacing(10)

        self.wave = WaveformBar()
        self.wave.seekRequested.connect(engine.seek_fraction)
        detail.addWidget(self.wave)

        self.scrub = ScrubBar()
        self.scrub.seekRequested.connect(engine.seek_fraction)
        detail.addWidget(self.scrub)

        # times row
        times = QtWidgets.QHBoxLayout()
        self.elapsed = QtWidgets.QLabel("0:00")
        self.elapsed.setObjectName("elapsed")
        self.elapsed.setFont(theme.mono(13))
        fmt = QtWidgets.QLabel("FLAC · 16-BIT / 44.1")
        fmt.setObjectName("format")
        fmt.setFont(theme.mono(11, letter_spacing=2))
        self.remaining = QtWidgets.QLabel("0:00")
        self.remaining.setObjectName("remaining")
        self.remaining.setFont(theme.mono(13))
        self.remaining.setAlignment(QtCore.Qt.AlignRight)
        times.addWidget(self.elapsed)
        times.addStretch(1)
        times.addWidget(fmt)
        times.addStretch(1)
        times.addWidget(self.remaining)
        detail.addSpacing(6)
        detail.addLayout(times)

        # transport
        transport = QtWidgets.QHBoxLayout()
        transport.setSpacing(20)
        self.prev = self._transport_button("⏮")
        self.toggle = self._transport_button("▶", main=True)
        self.next = self._transport_button("⏭")
        self.prev.clicked.connect(lambda: self._command(engine.prev))
        self.toggle.clicked.connect(lambda: self._command(engine.toggle))
        self.next.clicked.connect(lambda: self._command(engine.next))
        transport.addStretch(1)
        transport.addWidget(self.prev)
        transport.addWidget(self.toggle)
        transport.addWidget(self.next)
        transport.addStretch(1)
        detail.addSpacing(18)
        detail.addLayout(transport)

        detail.addStretch(1)
        body.addLayout(detail, 1)
        outer.addLayout(body, 1)

    def _transport_button(self, glyph, main=False):
        btn = QtWidgets.QPushButton(glyph)
        btn.setObjectName("transportMain" if main else "transport")
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        btn.setFocusPolicy(QtCore.Qt.NoFocus)
        return btn

    # -- audio output picker ----------------------------------------------- #

    @staticmethod
    def _short_output(sink):
        kind = sink.get("kind")
        if kind == "hdmi":
            return "HDMI"
        if kind == "analog":
            return "Headphones"
        return sink.get("description") or "Output"  # bluetooth shows its name

    def _refresh_output_label(self, sink=None):
        if sink is None:
            sinks = audio.list_sinks()
            sink = next((s for s in sinks if s["is_default"]),
                        sinks[0] if sinks else None)
        if sink is None:
            self.output.setText("Output")
            self.output.setEnabled(False)
            return
        self.output.setEnabled(True)
        self.output.setText("♪ " + self._short_output(sink))

    def _open_output_menu(self):
        menu = QtWidgets.QMenu(self)
        menu.setFont(theme.sans(13))
        sinks = audio.list_sinks()
        for sink in sinks:
            mark = "● " if sink["is_default"] else "    "
            act = menu.addAction(mark + sink["description"])
            act.triggered.connect(
                lambda _=False, s=sink: self._select_output(s))

        offline_bt = [d for d in audio.bluetooth_audio_devices()
                      if not d["connected"]]
        if offline_bt:
            menu.addSeparator()
            for dev in offline_bt:
                act = menu.addAction(f"Connect {dev['name']}…")
                act.triggered.connect(
                    lambda _=False, d=dev: self._connect_bt(d))

        menu.exec(self.output.mapToGlobal(self.output.rect().bottomLeft()))

    def _select_output(self, sink):
        engine.set_output_device(sink["name"])
        if sink.get("id") is not None:
            audio.set_default_sink(sink["id"])
        self._refresh_output_label(sink)

    def _connect_bt(self, dev):
        if self._bt_worker is not None and self._bt_worker.isRunning():
            return
        self.output.setText("Connecting…")
        self._bt_worker = _BtConnectWorker(dev["mac"], self)
        self._bt_worker.done.connect(self._on_bt_connected)
        self._bt_worker.start()

    def _on_bt_connected(self, sink):
        if sink:
            self._select_output(sink)
        else:
            self._refresh_output_label()

    # -- background --------------------------------------------------------- #

    def paintEvent(self, _event):
        p = QtGui.QPainter(self)
        grad = QtGui.QRadialGradient(self.width() / 2, 0, self.height() * 1.1)
        grad.setColorAt(0.0, theme.color(theme.GRAD_TOP))
        grad.setColorAt(0.6, theme.color(theme.GRAD_BOTTOM))
        grad.setColorAt(1.0, theme.color(theme.GRAD_BOTTOM))
        p.fillRect(self.rect(), grad)

    # -- live update -------------------------------------------------------- #

    def _command(self, fn):
        fn()
        self.refresh()

    def refresh(self):
        state = engine.state()
        track = state.get("track")

        self.backend.setText("SIMULATED" if state["backend"] == "simulated" else "VLC")
        self.backend.setProperty("backend", state["backend"])
        self._repolish(self.backend)

        if not track:
            self.title.setText("Nothing loaded")
            self.artist.setText("—")
            self.album.setText("")
            self.year.setText("")
            self.missing.hide()
            self.toggle.setText("▶")
            self.wave.set_progress(0.0)
            self.scrub.set_progress(0.0)
            self.elapsed.setText("0:00")
            self.remaining.setText("0:00")
            return

        self.artist.setText(track.get("artist") or "Unknown artist")
        self.title.setText(track.get("title") or "Untitled")
        self.album.setText(track.get("album") or "")
        self.year.setText(str(track["year"]) if track.get("year") else "")
        self.missing.setVisible(bool(track.get("missing")))

        if track.get("id") != self._last_track_id:
            self._last_track_id = track.get("id")
            self.wave.set_bars_for(track.get("id"))
            self._load_cover(track)

        dur = state["duration_seconds"] or 0
        pos = state["position_seconds"] or 0
        progress = state["progress"] or 0.0
        self.elapsed.setText(_fmt(pos))
        self.remaining.setText("-" + _fmt(max(0, dur - pos)))
        self.wave.set_progress(progress)
        self.scrub.set_progress(progress)
        self.toggle.setText("❚❚" if state["playing"] else "▶")
        self.prev.setEnabled(state["has_prev"] or pos >= 3)
        self.next.setEnabled(state["has_next"])

    def _load_cover(self, track):
        path = artwork_path(track.get("accession")) if track.get("accession") else None
        if path:
            pix = QtGui.QPixmap(str(path))
            if not pix.isNull():
                self.cover.setText("")
                self.cover.setPixmap(pix.scaled(
                    self.cover.size(), QtCore.Qt.KeepAspectRatioByExpanding,
                    QtCore.Qt.SmoothTransformation))
                return
        self.cover.setPixmap(QtGui.QPixmap())
        self.cover.setText("NO COVER")

    @staticmethod
    def _repolish(widget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)
