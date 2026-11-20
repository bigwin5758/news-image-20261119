#!/usr/bin/env python3
"""News image: THE WORLD IN ONE DAY - Thursday 19 November 2026.
make.fun competition news-image-20261119. Pure stdlib: draws a 1024x853
newspaper front page (3 varied highlights, 7 stories in category clusters,
20 briefs = 30 stories) and writes it to $MAKEFUN_OUTPUT_DIR/entry.png.
Deterministic: two runs produce byte-identical PNGs.
"""
import math
import os
import struct
import zlib

W, H = 1024, 853

CREAM = (246, 239, 221)
INK = (25, 25, 25)
RED = (185, 28, 28)
GREY = (107, 107, 107)
GREEN = (34, 120, 60)
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)

SKY = (176, 208, 232)
SUN = (245, 197, 66)
DBLUE = (38, 62, 110)
LBLUE = (120, 170, 220)
ORANGE = (245, 166, 66)
PINK = (232, 130, 150)
PURPLE = (122, 82, 160)
SAND = (222, 198, 150)
TAN = (203, 178, 130)
LTAN = (216, 196, 152)
BROWN = (120, 82, 50)
GRN = (46, 139, 76)
BLU = (52, 110, 190)
WATER = (90, 150, 205)
SMOKE = (150, 150, 150)
CLOUD = (140, 140, 140)

# 5x7 bitmap font. '#' = on, '.' = off. Uppercase only (text is uppercased).
FONT = {
'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
'0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
'1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
'2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
'3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
'4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
'5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
'6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
'7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
'8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
'9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
'.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
',': (".....", ".....", ".....", ".....", ".##..", ".##..", "#...."),
':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "#...."),
"'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
'-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
'&': (".###.", "#...#", "#...#", ".###.", "#.#..", "#..#.", ".##.#"),
'$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
'%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
'(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
'/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
'+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
'=': (".....", ".....", ".####", ".....", ".####", ".....", "....."),
'?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
'!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
# middle dot (used in kickers / footers as "PLACE . TOPIC")
'\u00b7': (".....", ".....", ".....", ".##..", ".##..", ".....", "....."),
}

px = bytearray()  # canvas buffer, initialised in main()


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i] = c[0]
        px[i + 1] = c[1]
        px[i + 2] = c[2]


def fill_rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i] = c[0]
            px[i + 1] = c[1]
            px[i + 2] = c[2]


def rect_outline(x, y, w, h, c, t=1):
    fill_rect(x, y, w, t, c)
    fill_rect(x, y + h - t, w, t, c)
    fill_rect(x, y, t, h, c)
    fill_rect(x + w - t, y, t, h, c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        set_px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def wline(x0, y0, x1, y1, c, wdt=3):
    # thick line: stamp a wdt x wdt block at every Bresenham step
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    r = wdt // 2
    while True:
        fill_rect(x0 - r, y0 - r, wdt, wdt, c)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def fill_circle(cx, cy, r, c):
    for y in range(cy - r, cy + r + 1):
        d = r * r - (y - cy) * (y - cy)
        if d < 0:
            continue
        dx = int(math.sqrt(d))
        for x in range(cx - dx, cx + dx + 1):
            set_px(x, y, c)


def fill_poly(pts, c):
    ys = [p[1] for p in pts]
    ymin, ymax = min(ys), max(ys)
    n = len(pts)
    for y in range(ymin, ymax + 1):
        xs = []
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            x0 = int(math.ceil(xs[i]))
            x1 = int(math.floor(xs[i + 1]))
            for x in range(x0, x1 + 1):
                set_px(x, y, c)


def norm(s):
    return (s.replace("\u2014", "-").replace("\u2013", "-")
             .replace("\u2019", "'").replace("\u2018", "'")
             .replace("\u201c", '"').replace("\u201d", '"'))


def text_w(s, scale):
    s = norm(s).upper()
    return len(s) * 6 * scale - scale if s else 0


def draw_text(x, y, s, scale, c):
    s = norm(s).upper()
    cx = x
    for ch in s:
        g = FONT.get(ch)
        if g is None:
            cx += 6 * scale
            continue
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == '#':
                    fill_rect(cx + col * scale, y + r * scale,
                              scale, scale, c)
        cx += 6 * scale


def draw_text_centered(cx, y, s, scale, c):
    draw_text(cx - text_w(s, scale) // 2, y, s, scale, c)


def wrap(s, scale, max_w):
    s = norm(s).upper()
    words = s.split(" ")
    lines = []
    cur = ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            # hard-break a single overlong word
            while text_w(wd, scale) > max_w:
                cut = max_w // (6 * scale)
                lines.append(wd[:cut])
                wd = wd[cut:]
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(x, y, s, scale, max_w, c, max_lines, lh):
    lines = wrap(s, scale, max_w)[:max_lines]
    for i, ln in enumerate(lines):
        draw_text(x, y + i * lh, ln, scale, c)
    return y + len(lines) * lh


def badge(x, y, n):
    s = str(n)
    wdt = 18 if len(s) == 1 else 26
    fill_rect(x, y, wdt, 18, BLACK)
    draw_text_centered(x + wdt // 2, y + 5, s, 1, WHITE)
    return wdt


def write_png(path, w, h, buf):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw.extend(buf[y * w * 3:(y + 1) * w * 3])
    comp = zlib.compress(bytes(raw), 6)

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    data = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)

# ---------------- illustrations (flat-vector, simple shapes) ----------------

def ill_shenzhen(x, y, w, h):
    fill_rect(x, y, w, h, SKY)
    fill_circle(x + w - 32, y + 26, 16, SUN)
    # skyline, varying heights
    base = y + h
    heights = [0.42, 0.60, 0.50, 0.72, 0.55, 0.66, 0.46, 0.58, 0.40, 0.62]
    bw = w // len(heights)
    for i, f in enumerate(heights):
        bh = int(h * f)
        fill_rect(x + i * bw + 2, base - bh, bw - 4, bh, DBLUE)
    # three flags on poles above the skyline
    for i, col in enumerate((RED, LBLUE, GRN)):
        px0 = x + w // 4 + i * (w // 4)
        line(px0, y + 12, px0, y + 52, INK)
        fill_rect(px0 + 1, y + 12, 22, 12, col)


def ill_vicecity(x, y, w, h):
    fill_rect(x, y, w, h // 3, ORANGE)
    fill_rect(x, y + h // 3, w, h // 3, PINK)
    fill_rect(x, y + 2 * h // 3, w, h - 2 * h // 3, PURPLE)
    fill_circle(x + w // 2, y + h // 2, 16, SUN)
    # palm tree
    tx = x + 34
    wline(tx, y + h - 6, tx + 6, y + 8, BROWN, 3)
    for dx, dy in ((-26, -14), (-18, -22), (-6, -26), (8, -24), (20, -16)):
        wline(tx + 6, y + 10, tx + 6 + dx, y + 10 + dy, GRN, 2)
    # skyline silhouette: buildings of varying heights along the bottom,
    # kept short near the sun so the sun stays clear
    base = y + h
    towers = [(80, 38, 26), (122, 38, 18), (164, 38, 24), (206, 38, 12),
              (248, 38, 28), (290, 38, 20), (332, 38, 26), (374, 38, 16),
              (416, 28, 22)]
    for bx, bw, bh in towers:
        fill_rect(x + bx, base - bh, bw, bh, DBLUE)
    # lit windows on a few towers (offset, height from base)
    for wx, wh in ((88, 20), (172, 18), (256, 22), (396, 12), (424, 16)):
        fill_rect(x + wx, base - wh, 3, 4, SUN)
    # bigger car silhouette, in front of the skyline
    cx0 = x + w - 150
    fill_rect(cx0, base - 20, 96, 14, BLACK)       # body
    fill_rect(cx0 + 18, base - 32, 56, 12, BLACK)  # cabin
    fill_rect(cx0 + 24, base - 29, 44, 7, LBLUE)   # windshield
    fill_circle(cx0 + 22, base - 7, 7, BLACK)      # rear wheel
    fill_circle(cx0 + 74, base - 7, 7, BLACK)      # front wheel
    fill_circle(cx0 + 22, base - 7, 2, GREY)       # hub
    fill_circle(cx0 + 74, base - 7, 2, GREY)       # hub


def ill_anthropic(x, y, w, h):
    fill_rect(x, y, w, h, (232, 240, 248))
    n = 6
    bw = w // (n + 1)
    for i in range(n):
        bh = int(h * (0.30 + 0.12 * i))
        col = BLU if i < 4 else GRN
        fill_rect(x + (i + 1) * bw - bw // 2, y + h - 8 - bh, bw - 8, bh, col)
    # rising arrow
    x0, y0 = x + 10, y + h - 22
    x1, y1 = x + w - 12, y + 12
    wline(x0, y0, x1, y1, GRN, 3)
    fill_poly([(x1, y1), (x1 - 16, y1 + 2), (x1 - 2, y1 + 16)], GRN)


def ill_court(x, y, w, h):
    fill_rect(x, y, w, h, CREAM)
    # pediment triangle + columns + base
    fill_poly([(x + 6, y + 22), (x + w // 2, y + 10), (x + w - 6, y + 22)],
              DBLUE)
    for i in range(4):
        cx = x + 10 + i * ((w - 20) // 3)
        fill_rect(cx, y + 24, 7, h - 34, INK)
    fill_rect(x + 4, y + h - 10, w - 8, 6, INK)


def ill_kerch(x, y, w, h):
    fill_rect(x, y, w, h * 2 // 3, SKY)
    fill_rect(x, y + h * 2 // 3, w, h - h * 2 // 3, WATER)
    # smoke puffs
    fill_circle(x + w // 3, y + 10, 6, SMOKE)
    fill_circle(x + w // 3 + 10, y + 6, 5, SMOKE)
    fill_circle(x + 2 * w // 3, y + 12, 5, SMOKE)
    # bridge deck + towers + cables
    fill_rect(x + 2, y + h // 2, w - 4, 5, INK)
    for tx in (w // 4, 3 * w // 4):
        fill_rect(x + tx - 2, y + 8, 4, h // 2, INK)
    line(x + w // 4, y + 8, x + w // 2, y + h // 2, INK)
    line(x + 3 * w // 4, y + 8, x + w // 2, y + h // 2, INK)
    # waves
    for wy in (y + h - 12, y + h - 5):
        for wx in range(x + 4, x + w - 4, 12):
            line(wx, wy, wx + 6, wy - 3, WHITE)
            line(wx + 6, wy - 3, wx + 12, wy, WHITE)


def ill_gaza_op(x, y, w, h):
    fill_rect(x, y, w, h, SAND)
    fill_circle(x + w - 16, y + 12, 9, SUN)
    for i, off in enumerate((8, w // 2 - 10, w - 34)):
        ax = x + off
        ty = y + h - 26 + (i % 2) * 6
        fill_poly([(ax, ty), (ax + 12, ty - 16), (ax + 24, ty)], INK)
        line(ax + 12, ty - 16, ax + 12, ty - 24, INK)


def ill_rain(x, y, w, h):
    fill_rect(x, y, w, h, SKY)
    fill_circle(x + w // 2 - 10, y + 12, 10, CLOUD)
    fill_circle(x + w // 2 + 8, y + 10, 12, CLOUD)
    fill_rect(x + w // 2 - 18, y + 12, 36, 8, CLOUD)
    for i in range(5):
        rx = x + 8 + i * (w // 5)
        line(rx, y + 28, rx - 3, y + 40, BLU)
    tx = x + w // 2 - 14
    fill_poly([(tx, y + h - 4), (tx + 14, y + h - 20), (tx + 28, y + h - 4)],
              (170, 120, 70))


def ill_estonia(x, y, w, h):
    fill_rect(x, y, w, h, (214, 226, 200))
    # fence: posts + two rails
    for i in range(6):
        fx = x + 6 + i * ((w - 12) // 5)
        fill_rect(fx, y + 10, 4, h - 20, INK)
    fill_rect(x + 4, y + 16, w - 8, 3, INK)
    fill_rect(x + 4, y + h - 18, w - 8, 3, INK)
    # sign
    fill_rect(x + w - 30, y + 8, 24, 16, WHITE)
    rect_outline(x + w - 30, y + 8, 24, 16, RED, 2)
    fill_rect(x + 4, y + h - 8, w - 8, 5, GRN)


def ill_cyclone(x, y, w, h):
    fill_rect(x, y, w, h, SKY)
    cx, cy = x + w // 2, y + h // 2 - 4
    for r in (18, 13, 8):
        for a in range(0, 270, 6):
            t = math.radians(a + r * 8)
            set_px(int(cx + r * math.cos(t)), int(cy + r * math.sin(t)), BLU)
            set_px(int(cx + r * math.cos(t)) + 1, int(cy + r * math.sin(t)), BLU)
    fill_circle(cx, cy, 3, BLU)
    for wy in (y + h - 10, y + h - 4):
        for wx in range(x + 4, x + w - 4, 12):
            line(wx, wy, wx + 6, wy - 3, WHITE)
            line(wx + 6, wy - 3, wx + 12, wy, WHITE)


def ill_cop31(x, y, w, h):
    fill_rect(x, y, w, h, (222, 235, 220))
    cx, cy = x + w // 2 - 8, y + h // 2
    fill_circle(cx, cy, 16, BLU)
    fill_circle(cx - 6, cy - 4, 5, GRN)
    fill_circle(cx + 6, cy + 5, 4, GRN)
    fill_circle(cx + 4, cy - 8, 3, GRN)
    # leaf
    lx, ly = x + w - 16, y + 8
    fill_poly([(lx, ly), (lx + 12, ly + 4), (lx, ly + 14), (lx - 8, ly + 6)],
              GRN)
    line(lx, ly + 14, lx - 4, ly + 18, GRN)


def ill_map(x, y, w, h):
    # simple world map: tan continent polygons on a light panel.
    # Designed for a wide, short panel (~292x48); coordinates are
    # relative to (x, y) and fit inside w x h.
    fill_rect(x, y, w, h, (238, 232, 210))
    # North America (wide, flat, top-left)
    fill_poly([(x + 8, y + 6), (x + 80, y + 4), (x + 100, y + 10),
               (x + 92, y + 20), (x + 66, y + 22), (x + 54, y + 28),
               (x + 40, y + 22), (x + 14, y + 16), (x + 6, y + 10)], TAN)
    # South America (below North America)
    fill_poly([(x + 58, y + 30), (x + 86, y + 28), (x + 92, y + 36),
               (x + 80, y + 46), (x + 66, y + 44), (x + 56, y + 36)], TAN)
    # Europe (tiny, centre-top)
    fill_poly([(x + 138, y + 8), (x + 158, y + 6), (x + 164, y + 12),
               (x + 154, y + 18), (x + 138, y + 16)], TAN)
    # Africa (centre)
    fill_poly([(x + 136, y + 22), (x + 168, y + 20), (x + 174, y + 30),
               (x + 162, y + 44), (x + 146, y + 42), (x + 134, y + 32)],
              TAN)
    # Asia (wide, flat, top-right)
    fill_poly([(x + 172, y + 6), (x + 258, y + 4), (x + 282, y + 10),
               (x + 274, y + 20), (x + 232, y + 24), (x + 190, y + 22),
               (x + 170, y + 14)], TAN)
    # Australia (small, bottom-right)
    fill_poly([(x + 222, y + 32), (x + 250, y + 30), (x + 258, y + 38),
               (x + 242, y + 46), (x + 224, y + 42)], TAN)
    # red story markers, all on land
    for mx, my in ((45, 12), (150, 12), (72, 36), (228, 14)):
        fill_circle(x + mx, y + my, 3, RED)

# ---------------- content (verbatim from spec) ----------------

HEROES = [
    {"n": 1, "kicker": "SHENZHEN \u00b7 SUMMIT",
     "headline": "Trump, Xi and Putin hold first three-way summit",
     "summary": ("Historic trilateral at APEC: nuclear security and the "
                 "Ukraine war on the agenda."),
     "ill": ill_shenzhen},
    {"n": 2, "kicker": "VICE CITY \u00b7 GAMES",
     "headline": "GTA VI arrives after a 13-year wait",
     "summary": ("Metacritic 99, 15.88m preorders worth $1.54bn, "
                 "Take-Two up 8%. Twitch peaks at 2.4m viewers."),
     "ill": ill_vicecity},
    {"n": 3, "kicker": "NASDAQ \u00b7 MARKETS",
     "headline": "Anthropic debuts in the biggest IPO on record",
     "summary": ("$81.3bn raised, shares priced at $83 - the largest "
                 "public offering ever."),
     "ill": ill_anthropic},
]

GRID = [
    {"n": 4, "kicker": "THE HAGUE \u00b7 LAW", "tag": "LAW",
     "headline": "World Court finds Myanmar committed genocide",
     "summary": "ICJ rules 9-6 in the 7-year Gambia v. Myanmar case.",
     "ill": ill_court},
    {"n": 5, "kicker": "KYIV \u00b7 WAR", "tag": "WAR",
     "headline": "Kerch Bridge hit again, traffic halted",
     "summary": ("Ukrainian strikes damage the Russia-Crimea link; "
                 "the crossing is suspended."),
     "ill": ill_kerch},
    {"n": 6, "kicker": "GAZA \u00b7 WAR", "tag": "WAR",
     "headline": "Israel launches ground operation in central Gaza",
     "summary": ("Displaced Palestinians flee tents and shelters in a "
                 "ceasefire area."),
     "ill": ill_gaza_op},
    {"n": 7, "kicker": "GAZA \u00b7 CRISIS", "tag": "CRISIS",
     "headline": "Rain deepens Gaza's shelter crisis",
     "summary": ("Heavy rainfall displaces 46,000+ households, damages "
                 "40,000+ shelters."),
     "ill": ill_rain},
    {"n": 8, "kicker": "TALLINN \u00b7 EUROPE", "tag": "EUROPE",
     "headline": "Estonia to shut its Russia border",
     "summary": ("Road crossings close from 1 December after an alleged "
                 "GRU sabotage plot."),
     "ill": ill_estonia},
    {"n": 9, "kicker": "ODISHA \u00b7 STORM", "tag": "STORM",
     "headline": "Cyclone Akvan nears India's east coast",
     "summary": "Heavy rain and strong winds batter the coast.",
     "ill": ill_cyclone},
    {"n": 10, "kicker": "ANTALYA \u00b7 CLIMATE", "tag": "CLIMATE",
     "headline": "COP31 enters its final 48 hours",
     "summary": "Disagreements remain as ministers warn of a deadlock.",
     "ill": ill_cop31},
]

BRIEFS = [
    "Houthis seize Red Sea coast",
    "Zelensky urges US to lift Starlink curbs",
    "EU proposes EUR45bn loan for Ukraine in 2027",
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
    "US Senate rejects Iran war-powers resolution 51-48",
    "Denmark approves Greenland defence deal",
    "UK and Norway fund GBP100m Ukraine naval craft",
    "Brent crude steady near $92",
    "Yunus home set ablaze in Bangladesh unrest",
]


# ---------------- layout helpers ----------------

def tag(x, y, s):
    wdt = text_w(s, 1) + 16
    fill_rect(x, y, wdt, 12, RED)
    draw_text(x + 8, y + 2, s, 1, WHITE)
    return wdt


def draw_story(x, y, w, ill_h, ill, kicker, headline, summary, n,
               hscale=2, hlh=15):
    ill(x, y, w, ill_h)
    badge(x + 4, y + 4, n)
    ky = y + ill_h + 8
    draw_text(x, ky, kicker, 1, RED)
    hy = ky + 7 + 6
    end = draw_wrapped(x, hy, headline, hscale, w, INK, 2, hlh)
    sy = end + 4
    draw_wrapped(x, sy, summary, 1, w, INK, 2, 9)
    return sy


def draw_brief(x, y, w, n, text):
    num = str(n) + ". "
    draw_text(x, y, num, 1, RED)
    nx = x + text_w(num, 1)
    draw_wrapped(nx, y, text, 1, w - text_w(num, 1), INK, 2, 9)


def build():
    # ---- masthead ----
    fill_rect(14, 10, 996, 2, INK)
    draw_text_centered(512, 18, "THE WORLD IN ONE DAY", 4, INK)
    draw_text_centered(512, 52, "THURSDAY 19 NOVEMBER 2026", 3, RED)
    fill_rect(14, 80, 996, 2, INK)

    # ---- highlights: hero 1 big on the left, heroes 2+3 stacked right ----
    h1 = HEROES[0]
    draw_story(14, 88, 540, 160, h1["ill"], h1["kicker"], h1["headline"],
               h1["summary"], 1, hscale=3, hlh=23)
    h2 = HEROES[1]
    draw_story(566, 88, 444, 58, h2["ill"], h2["kicker"], h2["headline"],
               h2["summary"], 2)
    h3 = HEROES[2]
    draw_story(566, 224, 444, 58, h3["ill"], h3["kicker"], h3["headline"],
               h3["summary"], 3)

    fill_rect(14, 358, 996, 2, INK)

    # ---- categories, row 1: WAR cluster (2 wide cards) + LAW ----
    tag(14, 366, "WAR")
    tag(668, 366, "LAW")
    g = GRID[1]  # Kerch
    draw_story(14, 384, 315, 55, g["ill"], g["kicker"], g["headline"],
               g["summary"], g["n"])
    g = GRID[2]  # Gaza op
    draw_story(341, 384, 315, 55, g["ill"], g["kicker"], g["headline"],
               g["summary"], g["n"])
    g = GRID[0]  # ICJ
    draw_story(668, 384, 342, 55, g["ill"], g["kicker"], g["headline"],
               g["summary"], g["n"])

    # ---- categories, row 2: CRISIS + EUROPE + STORM + CLIMATE ----
    tag(14, 518, "CRISIS")
    tag(266, 518, "EUROPE")
    tag(518, 518, "STORM")
    tag(770, 518, "CLIMATE")
    for i, gx in enumerate((14, 266, 518, 770)):
        g = GRID[3 + i]
        draw_story(gx, 536, 240, 55, g["ill"], g["kicker"], g["headline"],
                   g["summary"], g["n"])

    fill_rect(14, 668, 996, 2, INK)

    # ---- briefs: 4 columns x 5 rows ----
    col_x = (14, 266, 518, 770)
    for c in range(4):
        for r in range(5):
            idx = c * 5 + r
            draw_brief(col_x[c], 676 + r * 18, 240, 11 + idx,
                       BRIEFS[idx])

    # ---- bottom strip: world map + DATE CHECK ----
    rect_outline(14, 770, 300, 56, INK, 1)
    ill_map(18, 774, 292, 48)
    rect_outline(326, 770, 684, 56, INK, 1)
    # DATE CHECK content, centred in the box
    tx = 326 + 684 // 2
    # checkmark (green, vector) left of the text block
    wline(500, 795, 509, 805, GREEN, 4)
    wline(509, 805, 524, 786, GREEN, 4)
    draw_text(533, 778, "DATE CHECK", 1, RED)
    draw_text(533, 788, "THURSDAY 19 NOVEMBER 2026", 2, INK)
    draw_text(533, 806, "ALL STORIES VERIFIED FOR THIS DATE", 1, GREY)
    _ = tx

    # ---- count row + footer ----
    draw_text_centered(512, 832,
                       "3 HIGHLIGHTS \u00b7 7 IN CATEGORIES \u00b7 "
                       "20 BRIEFS = 30 STORIES", 1, INK)
    draw_text_centered(512, 844,
                       "SOURCES: REUTERS \u00b7 AP \u00b7 BBC \u00b7 "
                       "FINANCIAL TIMES \u00b7 BERNAMA", 1, GREY)


def main():
    global px
    px = bytearray(bytes(CREAM) * (W * H))
    build()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    write_png(os.path.join(out_dir, "entry.png"), W, H, px)


if __name__ == "__main__":
    main()
