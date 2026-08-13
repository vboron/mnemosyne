"""Warm-dark palette + fonts, shared by the native screens.

Mirrors the values in ``web/static/style.css`` so the native UI matches the
Screen Canvas design (dark warm ground, gold/amber accents).
"""

from PySide6 import QtGui

# -- palette (from the design's CSS :root) --------------------------------- #
BG = "#0b0a08"
SCREEN = "#10100e"
PANEL = "#14130f"
PANEL2 = "#191711"
LINE = "#4a4032"
LINE_SOFT = "#2d2820"
TEXT = "#eee3cf"
MUTED = "#9d907a"
AMBER = "#c8a46b"
AMBER_SOFT = "#c88a6b"          # simulated-backend accent
WAVE_UNPLAYED = "#3a3225"

# Radial ground painted behind the screen (design: circle at top).
GRAD_TOP = "#211c14"
GRAD_BOTTOM = "#070706"


def color(hex_str, alpha=255):
    c = QtGui.QColor(hex_str)
    c.setAlpha(alpha)
    return c


# Font families with generic fallbacks. The design uses Newsreader (serif),
# Hanken Grotesk (sans) and Spline Sans Mono (mono); if those aren't installed
# Qt falls through to the style hint.
def _font(families, size, weight=QtGui.QFont.Normal, hint=QtGui.QFont.SansSerif,
          letter_spacing=0.0):
    f = QtGui.QFont(families, size)
    f.setWeight(weight)
    f.setStyleHint(hint)
    if letter_spacing:
        f.setLetterSpacing(QtGui.QFont.PercentageSpacing, 100 + letter_spacing)
    return f


def serif(size, weight=QtGui.QFont.Normal):
    return _font(["Newsreader", "Georgia", "Times New Roman"], size, weight,
                 QtGui.QFont.Serif)


def sans(size, weight=QtGui.QFont.Normal, letter_spacing=0.0):
    return _font(["Hanken Grotesk", "Inter", "Helvetica Neue", "Arial"], size,
                 weight, QtGui.QFont.SansSerif, letter_spacing)


def mono(size, weight=QtGui.QFont.Normal, letter_spacing=0.0):
    return _font(["Spline Sans Mono", "SF Mono", "Menlo", "DejaVu Sans Mono"],
                 size, weight, QtGui.QFont.Monospace, letter_spacing)


STYLESHEET = f"""
QWidget {{
    color: {TEXT};
    background: transparent;
}}
#eyebrow {{
    color: {MUTED};
    letter-spacing: 4px;
}}
#eyebrowStrong {{ color: {AMBER}; }}
#backend {{
    color: {MUTED};
    border: 1px solid {LINE_SOFT};
    border-radius: 4px;
    padding: 3px 9px;
}}
#backend[backend="simulated"] {{
    color: {AMBER_SOFT};
    border-color: #4a3226;
}}
QPushButton#output {{
    color: {TEXT};
    background: {PANEL2};
    border: 1px solid {LINE_SOFT};
    border-radius: 4px;
    padding: 5px 12px;
    text-align: center;
}}
QPushButton#output:hover {{ border-color: {LINE}; background: {PANEL}; }}
QMenu {{
    background: {PANEL};
    border: 1px solid {LINE};
    padding: 6px;
    color: {TEXT};
}}
QMenu::item {{
    padding: 10px 18px;
    border-radius: 4px;
}}
QMenu::item:selected {{ background: {PANEL2}; color: {AMBER}; }}
QMenu::separator {{ height: 1px; background: {LINE_SOFT}; margin: 6px 8px; }}
#artist {{ color: {AMBER}; letter-spacing: 3px; }}
#title  {{ color: {TEXT}; }}
#album  {{ color: {MUTED}; }}
#year   {{ color: {MUTED}; }}
#missing {{ color: {AMBER_SOFT}; }}
#format {{ color: {MUTED}; letter-spacing: 2px; }}
#elapsed, #remaining {{ color: {TEXT}; }}
QPushButton#transport {{
    color: {TEXT};
    background: {PANEL2};
    border: 1px solid {LINE_SOFT};
    border-radius: 26px;
    min-width: 52px;
    min-height: 52px;
    font-size: 20px;
}}
QPushButton#transport:hover {{ border-color: {LINE}; background: {PANEL}; }}
QPushButton#transport:disabled {{ color: {LINE}; border-color: {LINE_SOFT}; }}
QPushButton#transportMain {{
    color: {BG};
    background: {AMBER};
    border: none;
    border-radius: 34px;
    min-width: 68px;
    min-height: 68px;
    font-size: 26px;
}}
QPushButton#transportMain:hover {{ background: #d8b47b; }}
#cover {{
    background: {PANEL};
    border: 1px solid {LINE_SOFT};
    border-radius: 6px;
    color: {MUTED};
    letter-spacing: 2px;
}}
"""
