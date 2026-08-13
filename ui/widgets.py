"""Custom-painted transport widgets: the pseudo-waveform and the scrub bar.

Both emit ``seekRequested(fraction)`` on click/drag so the screen can drive
``engine.seek_fraction``.
"""

import math

from PySide6 import QtCore, QtGui, QtWidgets

from ui import theme


def build_bars(seed, count=96):
    """Deterministic pseudo-waveform seeded by track id.

    Direct port of ``buildBars`` in ``web/static/now_playing.js`` so a given
    track looks identical in the web and native UIs. Real spectral data can
    replace this later.
    """
    x = (seed or 1) * 9301 + 49297
    out = []
    for i in range(count):
        x = (x * 9301 + 49297) % 233280
        r = x / 233280
        # Shape it like a track envelope rather than pure noise.
        env = 0.35 + 0.65 * abs(math.sin((i / count) * math.pi * 3))
        out.append(0.12 + r * 0.88 * env)
    return out


class WaveformBar(QtWidgets.QWidget):
    """Amber-on-dark bars; played portion is amber, the rest is dim."""

    seekRequested = QtCore.Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bars = build_bars(1)
        self._progress = 0.0
        self._played = theme.color(theme.AMBER)
        self._unplayed = theme.color(theme.WAVE_UNPLAYED)
        self.setMinimumHeight(96)
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def set_bars_for(self, seed):
        self._bars = build_bars(seed or 1)
        self.update()

    def set_progress(self, progress):
        progress = max(0.0, min(1.0, progress))
        if abs(progress - self._progress) > 1e-4:
            self._progress = progress
            self.update()

    def paintEvent(self, _event):
        p = QtGui.QPainter(self)
        w, h = self.width(), self.height()
        n = len(self._bars) or 1
        step = w / n
        bar_w = max(1.0, step - 2)
        played_x = self._progress * w
        for i, val in enumerate(self._bars):
            x = i * step
            bar_h = val * (h * 0.9)
            y = (h - bar_h) / 2
            p.fillRect(QtCore.QRectF(x, y, bar_w, bar_h),
                       self._played if x < played_x else self._unplayed)

    def _seek(self, event):
        if self.width() > 0:
            self.seekRequested.emit(
                max(0.0, min(1.0, event.position().x() / self.width())))

    def mousePressEvent(self, event):
        self._seek(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self._seek(event)


class ScrubBar(QtWidgets.QWidget):
    """Thin track with an amber fill and a draggable head."""

    seekRequested = QtCore.Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0.0
        self._track = theme.color(theme.LINE_SOFT)
        self._fill = theme.color(theme.AMBER)
        self.setFixedHeight(20)
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def set_progress(self, progress):
        self._progress = max(0.0, min(1.0, progress))
        self.update()

    def paintEvent(self, _event):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        p.setPen(QtCore.Qt.NoPen)
        w, h = self.width(), self.height()
        cy = h / 2
        track_h = 4
        p.setBrush(self._track)
        p.drawRoundedRect(QtCore.QRectF(0, cy - track_h / 2, w, track_h), 2, 2)
        fill_w = w * self._progress
        p.setBrush(self._fill)
        p.drawRoundedRect(QtCore.QRectF(0, cy - track_h / 2, fill_w, track_h), 2, 2)
        p.drawEllipse(QtCore.QPointF(fill_w, cy), 6, 6)

    def _seek(self, event):
        if self.width() > 0:
            self.seekRequested.emit(
                max(0.0, min(1.0, event.position().x() / self.width())))

    def mousePressEvent(self, event):
        self._seek(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self._seek(event)
