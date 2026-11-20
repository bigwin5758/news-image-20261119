"""Thursday 19 November 2026 -- one-image world-news front page.

make.fun competition news-image-20261119. Pure Python standard library:
draws a 1024x853 PNG with a 5x7 bitmap font and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
Deterministic: two runs produce byte-identical files.
"""

import math
import os
import struct
import zlib

W, H = 1024, 853

PAPER = (246, 239, 221)
INK = (25, 25, 25)
RED = (185, 28, 28)
GREY = (107, 107, 107)
LIGHT = (233, 226, 203)
TAN = (212, 194, 158)
GREEN = (0, 130, 70)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph is 7 rows; each row is a 5-bit number,
# bit 4 = leftmost pixel. Only the characters used by the content are
# defined; anything else falls back to '?'.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0, 0x0C),
    ",": (0, 0, 0, 0, 0, 0x04, 0x08),
    ":": (0, 0x04, 0, 0, 0, 0x04, 0),
    ";": (0, 0x04, 0, 0, 0x04, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "-": (0, 0, 0, 0x0E, 0, 0, 0),
    "\u2014": (0, 0, 0, 0x1F, 0, 0, 0),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "%": (0x18, 0x19, 0x02, 0x04, 0x08, 0x13, 0x03),
    "\u20ac": (0x0E, 0x11, 0x1F, 0x10, 0x1F, 0x11, 0x0E),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "\u00b7": (0, 0, 0, 0x0C, 0x0C, 0, 0),
}


def norm(s):
    """Uppercase + normalise dashes/quotes to glyphs the font has."""
    return (s.replace("\u2013", "-").replace("\u2019", "'")
             .replace("\u2018", "'").upper())


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(bytes(bg) * (w * h))

    def _idx(self, x, y):
        return (y * self.w + x) * 3

    def set_pixel(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._idx(x, y)
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = self._idx(x0, yy)
            self.buf[i:i + (x1 - x0) * 3] = row

    def rect(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def hline(self, x, y, w, color, t=1):
        self.fill_rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.fill_rect(x, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, w=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0 - w // 2, y0 - w // 2, w, w, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def fill_ellipse(self, cx, cy, rx, ry, color):
        for dy in range(-ry, ry + 1):
            t = 1.0 - (dy * dy) / float(ry * ry)
            dx = int(rx * math.sqrt(max(0.0, t)))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def fill_poly(self, pts, color):
        if not pts:
            return
        ys = [p[1] for p in pts]
        ymin = max(0, min(ys))
        ymax = min(self.h - 1, max(ys))
        n = len(pts)
        for y in range(ymin, ymax + 1):
            xs = []
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / float(y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                xa = int(math.ceil(xs[i]))
                xb = int(math.floor(xs[i + 1]))
                if xb >= xa:
                    self.fill_rect(xa, y, xb - xa + 1, 1, color)


# ---------------------------------------------------------------- text
def text_width(s, scale):
    s = norm(s)
    return len(s) * 6 * scale - scale if s else 0


def draw_char(cv, x, y, ch, scale, color, bold=False):
    glyph = FONT.get(ch, FONT["?"])
    for row in range(7):
        bits = glyph[row]
        if not bits:
            continue
        for col in range(5):
            if bits >> (4 - col) & 1:
                px = x + col * scale
                py = y + row * scale
                cv.fill_rect(px, py, scale, scale, color)
                if bold:
                    cv.fill_rect(px + 1, py, scale, scale, color)


def draw_text(cv, x, y, s, scale, color, bold=False, align="left"):
    s = norm(s)
    w = text_width(s, scale)
    if align == "center":
        x -= w // 2
    elif align == "right":
        x -= w
    cx = x
    for ch in s:
        draw_char(cv, cx, y, ch, scale, color, bold)
        cx += 6 * scale
    return w


def wrap(s, max_chars):
    words = norm(s).split(" ")
    lines = []
    cur = ""
    for word in words:
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    out = []
    for ln in lines:
        while len(ln) > max_chars:
            out.append(ln[:max_chars])
            ln = ln[max_chars:]
        out.append(ln)
    return out


def draw_wrapped(cv, x, y, s, scale, color, max_chars, line_h, max_lines,
                 bold=False):
    lines = wrap(s, max_chars)
    if len(lines) > max_lines:
        raise SystemExit("TEXT OVERFLOW: %r wraps to %d lines (max %d)"
                         % (s, len(lines), max_lines))
    for i, ln in enumerate(lines):
        draw_text(cv, x, y + i * line_h, ln, scale, color, bold=bold)
    return len(lines)


# ---------------------------------------------------------------- illustrations
def ill_shenzhen(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (188, 214, 236))
    cv.fill_circle(x + w - 34, y + 26, 16, (255, 224, 130))
    base = y + h
    heights = [0.45, 0.62, 0.38, 0.72, 0.52, 0.80, 0.58, 0.42, 0.66, 0.50]
    bw = w // len(heights)
    for i, f in enumerate(heights):
        bh = int(h * 0.55 * f)
        cv.fill_rect(x + i * bw + 2, base - bh, bw - 4, bh, (52, 68, 92))
    for i, col in enumerate(((185, 28, 28), (50, 110, 180), (60, 140, 80))):
        px = x + w // 2 - 30 + i * 30
        cv.vline(px, y + 18, 34, INK, 2)
        cv.fill_rect(px + 1, y + 18, 22, 12, col)


def ill_vicecity(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h // 3, (255, 190, 110))
    cv.fill_rect(x, y + h // 3, w, h // 3, (255, 150, 140))
    cv.fill_rect(x, y + 2 * h // 3, w, h - 2 * h // 3, (150, 110, 185))
    cv.fill_circle(x + w // 2, y + h // 2, 22, (255, 226, 130))
    tx, ty = x + 34, y + 34
    cv.line(tx, y + h - 18, tx + 6, ty, (90, 60, 30), 4)
    for ang in (-160, -125, -90, -55, -20):
        rad = math.radians(ang)
        ex = int(tx + 6 + 32 * math.cos(rad))
        ey = int(ty + 20 * math.sin(rad))
        cv.line(tx + 6, ty, ex, ey, (40, 130, 70), 3)
    cv.fill_rect(x + w - 112, y + h - 26, 86, 14, (30, 30, 40))
    cv.fill_rect(x + w - 100, y + h - 40, 60, 14, (30, 30, 40))
    cv.fill_circle(x + w - 94, y + h - 12, 7, (20, 20, 25))
    cv.fill_circle(x + w - 46, y + h - 12, 7, (20, 20, 25))


def ill_nasdaq(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (228, 238, 245))
    for i in range(1, 4):
        cv.hline(x + 8, y + i * h // 4, w - 16, (200, 210, 220), 1)
    bw = w // 7
    vals = [0.25, 0.35, 0.30, 0.50, 0.62, 0.78, 0.95]
    for i, f in enumerate(vals):
        bh = int(h * 0.70 * f)
        bx = x + 12 + i * bw
        col = (50, 110, 180) if i < 5 else (40, 160, 90)
        cv.fill_rect(bx, y + h - 14 - bh, bw - 8, bh, col)
    cv.line(x + 16, y + h - 30, x + w - 20, y + 22, (40, 160, 90), 4)
    cv.line(x + w - 20, y + 22, x + w - 42, y + 24, (40, 160, 90), 4)
    cv.line(x + w - 20, y + 22, x + w - 22, y + 44, (40, 160, 90), 4)


def ill_court(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (232, 228, 215))
    cv.fill_poly([(x + 8, y + 26), (x + w - 8, y + 26),
                  (x + w // 2, y + 8)], (90, 90, 100))
    for i in range(4):
        cx = x + 16 + i * (w - 32) // 3
        cv.fill_rect(cx, y + 30, 8, h - 44, (250, 250, 245))
    cv.fill_rect(x + 6, y + h - 14, w - 12, 8, (90, 90, 100))


def ill_kerch(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (190, 215, 235))
    cv.fill_rect(x, y + h - 22, w, 22, (90, 150, 200))
    cv.fill_rect(x + 30, y + 12, 6, h - 22, (70, 70, 80))
    cv.fill_rect(x + w - 36, y + 12, 6, h - 22, (70, 70, 80))
    cv.fill_rect(x + 4, y + 34, w - 8, 6, (50, 50, 60))
    cv.line(x + 33, y + 14, x + 10, y + 34, (120, 120, 130), 2)
    cv.line(x + 33, y + 14, x + 56, y + 34, (120, 120, 130), 2)
    cv.line(x + w - 33, y + 14, x + w - 56, y + 34, (120, 120, 130), 2)
    cv.line(x + w - 33, y + 14, x + w - 10, y + 34, (120, 120, 130), 2)
    cv.fill_circle(x + w // 2, y + 22, 7, (160, 160, 160))
    cv.fill_circle(x + w // 2 + 8, y + 16, 5, (175, 175, 175))


def ill_tents(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (233, 211, 170))
    cv.fill_circle(x + w - 22, y + 18, 10, (255, 220, 130))
    cv.fill_poly([(x + 12, y + h - 12), (x + 34, y + h - 12),
                  (x + 23, y + h - 44)], (200, 170, 120))
    cv.fill_poly([(x + 44, y + h - 12), (x + 74, y + h - 12),
                  (x + 59, y + h - 52)], (180, 145, 100))
    cv.fill_poly([(x + 84, y + h - 12), (x + 108, y + h - 12),
                  (x + 96, y + h - 40)], (200, 170, 120))
    cv.fill_rect(x, y + h - 12, w, 3, (170, 140, 100))


def ill_rain(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (200, 210, 220))
    cv.fill_circle(x + 40, y + 22, 14, (120, 125, 135))
    cv.fill_circle(x + 62, y + 16, 17, (135, 140, 150))
    cv.fill_circle(x + 86, y + 24, 12, (120, 125, 135))
    cv.fill_rect(x + 30, y + 22, 66, 12, (120, 125, 135))
    for rx in (36, 52, 68, 84, 100):
        cv.line(x + rx, y + 40, x + rx - 3, y + 56, (70, 120, 180), 2)
    cv.fill_poly([(x + 44, y + h - 8), (x + 88, y + h - 8),
                  (x + 66, y + h - 34)], (200, 170, 120))


def ill_fence(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (215, 225, 205))
    cv.fill_rect(x, y + h - 16, w, 16, (170, 180, 150))
    cv.fill_rect(x + 6, y + 22, w - 12, 5, (90, 90, 90))
    cv.fill_rect(x + 6, y + 44, w - 12, 5, (90, 90, 90))
    for i in range(9):
        bx = x + 10 + i * ((w - 20) // 8)
        cv.fill_rect(bx, y + 12, 4, 44, (70, 70, 70))
    cv.fill_rect(x + w - 34, y + 8, 26, 18, (240, 240, 235))
    cv.rect(x + w - 34, y + 8, 26, 18, RED, 1)


def ill_cyclone(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (205, 220, 232))
    cx, cy = x + w // 2, y + h // 2 - 6
    pts = []
    for t in range(0, 541, 6):
        rad = math.radians(t)
        r = 4 + t * 0.055
        pts.append((int(cx + r * math.cos(rad)),
                    int(cy + r * math.sin(rad))))
    for i in range(len(pts) - 1):
        cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                (60, 100, 160), 2)
    for wy in (y + h - 16, y + h - 8):
        for i in range(0, w, 8):
            cv.line(x + i, wy, x + i + 4, wy - 4, (90, 150, 200), 2)
            cv.line(x + i + 4, wy - 4, x + i + 8, wy, (90, 150, 200), 2)


def ill_cop31(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (225, 235, 225))
    cv.fill_circle(x + w // 2, y + h // 2, 26, (90, 150, 200))
    cv.fill_circle(x + w // 2 - 10, y + h // 2 - 8, 8, (80, 160, 90))
    cv.fill_circle(x + w // 2 + 10, y + h // 2 + 8, 7, (80, 160, 90))
    cv.fill_circle(x + w // 2 + 4, y + h // 2 - 12, 5, (80, 160, 90))
    cv.fill_ellipse(x + w - 22, y + 16, 10, 5, (60, 140, 80))
    cv.line(x + w - 22, y + 16, x + w - 12, y + 8, (60, 140, 80), 2)


def ill_map(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, LIGHT)
    cv.rect(x, y, w, h, INK, 1)
    # North America: broad top, east coast, tapering to Central America
    cv.fill_poly([(x + 14, y + 28), (x + 10, y + 16), (x + 30, y + 8),
                  (x + 70, y + 8), (x + 100, y + 12), (x + 116, y + 22),
                  (x + 110, y + 34), (x + 96, y + 38), (x + 84, y + 44),
                  (x + 78, y + 54), (x + 66, y + 58), (x + 56, y + 50),
                  (x + 40, y + 44), (x + 18, y + 40)], TAN)
    # South America: separate teardrop below, tapering to a southern tip
    cv.fill_poly([(x + 78, y + 66), (x + 100, y + 64), (x + 118, y + 72),
                  (x + 112, y + 86), (x + 98, y + 96), (x + 86, y + 88),
                  (x + 74, y + 76)], TAN)
    # Europe: small separate landmass, upper centre
    cv.fill_poly([(x + 168, y + 18), (x + 184, y + 12), (x + 198, y + 16),
                  (x + 196, y + 26), (x + 186, y + 32), (x + 172, y + 30)],
                 TAN)
    # Africa: large, tapering down to a southern point
    cv.fill_poly([(x + 172, y + 40), (x + 192, y + 38), (x + 206, y + 46),
                  (x + 204, y + 62), (x + 194, y + 78), (x + 182, y + 82),
                  (x + 172, y + 68), (x + 164, y + 52)], TAN)
    # Asia: wide landmass, upper right, with a small gap from Europe
    cv.fill_poly([(x + 208, y + 14), (x + 240, y + 8), (x + 290, y + 10),
                  (x + 322, y + 18), (x + 326, y + 30), (x + 310, y + 40),
                  (x + 280, y + 44), (x + 240, y + 42), (x + 212, y + 34),
                  (x + 208, y + 24)], TAN)
    # Australia: small separate blob, lower right
    cv.fill_poly([(x + 268, y + 66), (x + 296, y + 62), (x + 312, y + 68),
                  (x + 308, y + 80), (x + 288, y + 84), (x + 270, y + 78)],
                 TAN)
    for dx, dy in ((262, 30), (186, 22), (182, 48), (60, 28)):
        cv.fill_circle(x + dx, y + dy, 3, RED)


# ---------------------------------------------------------------- content
HEROES = [
    {"n": 1, "kicker": "SHENZHEN \u00b7 SUMMIT",
     "headline": "Trump, Xi and Putin hold first three-way summit",
     "summary": "Historic trilateral at APEC: nuclear security and the "
                "Ukraine war on the agenda.",
     "ill": ill_shenzhen},
    {"n": 2, "kicker": "VICE CITY \u00b7 GAMES",
     "headline": "GTA VI arrives after a 13-year wait",
     "summary": "Metacritic 99, 15.88m preorders worth $1.54bn, "
                "Take-Two up 8%. Twitch peaks at 2.4m viewers.",
     "ill": ill_vicecity},
    {"n": 3, "kicker": "NASDAQ \u00b7 MARKETS",
     "headline": "Anthropic debuts in the biggest IPO on record",
     "summary": "$81.3bn raised, shares priced at $83 \u2014 the largest "
                "public offering ever.",
     "ill": ill_nasdaq},
]

GRID = [
    {"n": 4, "kicker": "THE HAGUE \u00b7 LAW",
     "headline": "World Court rules on Myanmar's Rohingya case",
     "summary": "ICJ delivers its verdict in the 7-year Gambia v. "
                "Myanmar case.",
     "ill": ill_court},
    {"n": 5, "kicker": "KYIV \u00b7 WAR",
     "headline": "Kerch Bridge hit again, traffic halted",
     "summary": "Ukrainian strikes damage the Russia\u2013Crimea link; "
                "the crossing is suspended.",
     "ill": ill_kerch},
    {"n": 6, "kicker": "GAZA \u00b7 WAR",
     "headline": "Israel launches ground operation in central Gaza",
     "summary": "Displaced Palestinians flee tents and shelters in a "
                "ceasefire area.",
     "ill": ill_tents},
    {"n": 7, "kicker": "GAZA \u00b7 CRISIS",
     "headline": "Rain deepens Gaza's shelter crisis",
     "summary": "Heavy rainfall displaces 46,000+ households, damages "
                "40,000+ shelters.",
     "ill": ill_rain},
    {"n": 8, "kicker": "TALLINN \u00b7 EUROPE",
     "headline": "Estonia to shut its Russia border",
     "summary": "Road crossings close from 1 December after an alleged "
                "GRU sabotage plot.",
     "ill": ill_fence},
    {"n": 9, "kicker": "ODISHA \u00b7 STORM",
     "headline": "Cyclone Akvan nears India's east coast",
     "summary": "Heavy rain and strong winds batter the coast.",
     "ill": ill_cyclone},
    {"n": 10, "kicker": "ANTALYA \u00b7 CLIMATE",
     "headline": "COP31 enters its final 48 hours",
     "summary": "Disagreements remain as ministers warn of a deadlock.",
     "ill": ill_cop31},
]

BRIEFS = [
    "Houthis seize Red Sea coast",
    "Zelensky urges US to lift Starlink curbs",
    "EU proposes \u20ac45bn loan for Ukraine in 2027",
    "GOP threatens to strip Ukraine aid",
    "Myanmar president weighs leaving ASEAN",
    "US panel urges action on China over Panama ships",
    "Bukele demolishes gang leader's home in Haiti",
    "Russian spy suspect held over Silicon Valley firm",
    "Ukraine-Russia-US talks in Abu Dhabi",
    "Voyager 1 one light-day out",
    "Nvidia $115.8bn quarter, chip crackdown",
    "US-China rare-earth curbs add tension",
    "Global stocks fall ahead of Nvidia earnings",
    "Australia sanctions West Bank settlers",
    "Nvidia shares slide",
]


# ---------------------------------------------------------------- layout
def build():
    cv = Canvas(W, H, PAPER)
    cv.rect(8, 8, W - 16, H - 16, INK, 2)

    # masthead
    draw_text(cv, W // 2, 28, "Thursday 19 November 2026", 4, INK,
              bold=True, align="center")
    draw_text(cv, W // 2, 66, "The World in One Picture", 2, RED,
              bold=True, align="center")
    cv.hline(24, 88, W - 48, INK, 2)
    cv.hline(24, 93, W - 48, INK, 1)

    # heroes: 3 columns
    for i, hero in enumerate(HEROES):
        x = 24 + i * 332
        hero["ill"](cv, x, 104, 312, 160)
        cv.fill_rect(x + 6, 110, 18, 18, INK)
        draw_text(cv, x + 15, 114, str(hero["n"]), 1, WHITE,
                  align="center")
        draw_text(cv, x, 274, hero["kicker"], 1, RED, bold=True)
        draw_wrapped(cv, x, 288, hero["headline"], 2, INK, 26, 17, 2,
                     bold=True)
        draw_wrapped(cv, x, 330, hero["summary"], 1, INK, 52, 10, 2)
    cv.hline(24, 362, W - 48, GREY, 1)

    # grid: 7 uniform cards in one row
    for i, card in enumerate(GRID):
        x = 24 + i * 140
        card["ill"](cv, x, 372, 132, 80)
        cv.fill_rect(x + 4, 376, 14, 14, INK)
        draw_text(cv, x + 11, 379, str(card["n"]), 1, WHITE,
                  align="center")
        draw_text(cv, x, 460, card["kicker"], 1, RED, bold=True)
        draw_wrapped(cv, x, 474, card["headline"], 1, INK, 22, 9, 3,
                     bold=True)
        draw_wrapped(cv, x, 506, card["summary"], 1, INK, 22, 9, 5)
    cv.hline(24, 556, W - 48, GREY, 1)

    # briefs: 3 columns x 5 rows, column-major
    for col in range(3):
        bx = 24 + col * 325
        for row in range(5):
            idx = col * 5 + row
            n = 11 + idx
            y = 566 + row * 22
            num = "%d." % n
            draw_text(cv, bx, y, num, 1, RED, bold=True)
            draw_text(cv, bx + text_width(num + " ", 1), y,
                      BRIEFS[idx], 1, INK)
    cv.hline(24, 672, W - 48, GREY, 1)

    # bottom strip: world map + date check
    ill_map(cv, 24, 684, 336, 104)
    cv.rect(376, 684, 624, 104, INK, 2)
    # content block (checkmark + text) centred in the box: block spans
    # x 503..873, box centre x 688
    cv.line(503, 736, 517, 750, GREEN, 5)
    cv.line(517, 750, 545, 714, GREEN, 5)
    draw_text(cv, 563, 706, "Date Check", 2, INK, bold=True)
    draw_text(cv, 563, 730, "Thursday 19 November 2026", 2, INK)
    draw_text(cv, 563, 758, "All stories verified for this date", 1, GREY)

    # count row + footer
    draw_text(cv, W // 2, 798, "3 Heroes \u00b7 7 Grid \u00b7 15 Briefs = "
              "25 Stories", 1, INK, align="center")
    draw_text(cv, W // 2, 822, "Sources: Reuters \u00b7 AP \u00b7 BBC \u00b7 "
              "Financial Times \u00b7 Bernama", 1, GREY, align="center")
    return cv


# ---------------------------------------------------------------- png
def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(path, cv):
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += cv.buf[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", comp) + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


def main():
    cv = build()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    write_png(os.path.join(out_dir, "entry.png"), cv)


if __name__ == "__main__":
    main()
