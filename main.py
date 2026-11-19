"""News summary image: Thursday 19 November 2026.

Self-contained Python 3.13, standard library only. Renders a classic
landscape newspaper front page (1024x853) to /output/entry.png.
"""

import binascii
import math
import os
import struct
import zlib

W, H = 1024, 853

PAPER = (0xF6, 0xEF, 0xDB)
INK = (0x1A, 0x1A, 0x1A)
RED = (0xB3, 0x26, 0x1E)
GREY = (0x6E, 0x6A, 0x5E)
BOXFILL = (0xFF, 0xFD, 0xF2)
SKY = (0xC7, 0xD2, 0xDC)
BLDG_DARK = (0x3A, 0x4A, 0x58)
BLDG_MID = (0x5A, 0x6B, 0x7A)
BLDG_LT = (0x8A, 0x9A, 0xA8)
GROUND = (0xC9, 0x8A, 0x3D)
SUN_Y = (0xF2, 0xC1, 0x4E)
SUN_O = (0xE8, 0x6A, 0x3C)
SUN_R = (0xD9, 0x4F, 0x30)
SUN = (0xC0, 0x39, 0x2B)
CHART_BG = (0xE9, 0xED, 0xF1)
CHART_GRID = (0xC9, 0xD2, 0xDA)
BAR = (0x2F, 0x7A, 0x4E)
TREND = (0xC0, 0x39, 0x2B)
BLUE = (0x2E, 0x5A, 0x88)
ORANGE = (0xD9, 0x8E, 0x32)
MAPC = (0xC9, 0xB8, 0x8A)

fb = bytearray(bytes(PAPER) * (W * H))


# ---------------------------------------------------------------- pixels
def px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        fb[i] = color[0]
        fb[i + 1] = color[1]
        fb[i + 2] = color[2]


def fill_rect(x0, y0, x1, y1, color):
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W, x1)
    y1 = min(H, y1)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(color) * (x1 - x0)
    for y in range(y0, y1):
        base = (y * W + x0) * 3
        fb[base:base + len(row)] = row


def hline(x0, x1, y, color):
    fill_rect(x0, y, x1, y + 1, color)


def vline(x, y0, y1, color):
    fill_rect(x, y0, x + 1, y1, color)


def rect(x0, y0, x1, y1, color):
    hline(x0, x1, y0, color)
    hline(x0, x1, y1 - 1, color)
    vline(x0, y0, y1, color)
    vline(x1 - 1, y0, y1, color)


def line(x0, y0, x1, y1, color):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        px(x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def fill_circle(cx, cy, r, color):
    for dy in range(-r, r + 1):
        t = 1.0 - (dy * dy) / float(r * r)
        dx = int(r * math.sqrt(max(0.0, t)))
        fill_rect(cx - dx, cy + dy, cx + dx + 1, cy + dy + 1, color)


def fill_ellipse(cx, cy, rx, ry, color):
    for dy in range(-ry, ry + 1):
        t = 1.0 - (dy * dy) / float(ry * ry)
        dx = int(rx * math.sqrt(max(0.0, t)))
        fill_rect(cx - dx, cy + dy, cx + dx + 1, cy + dy + 1, color)


# ---------------------------------------------------------------- font
# 5x7 bitmap font: each glyph is 7 rows, each row a 5-bit value
# (bit 4 = leftmost pixel).
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
    "J": (0x01, 0x01, 0x01, 0x01, 0x01, 0x11, 0x0E),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0E, 0x11, 0x10, 0x0E, 0x01, 0x11, 0x0E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x0E, 0x11, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x11, 0x0E),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "-": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "·": (0x00, 0x00, 0x00, 0x0C, 0x0C, 0x00, 0x00),
    "✓": (0x00, 0x01, 0x00, 0x12, 0x08, 0x04, 0x00),
    "€": (0x0E, 0x11, 0x10, 0x1E, 0x10, 0x11, 0x0E),
}
BLANK = (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)


def normalize(s):
    return (s.replace("’", "'").replace("‘", "'")
             .replace("–", "-").replace("—", "-").upper())


def text_w(s, sx):
    s = normalize(s)
    if not s:
        return 0
    return len(s) * 6 * sx - sx


def draw_text(x, y, s, sx, sy, color, bold=False):
    s = normalize(s)
    cx = x
    for ch in s:
        rows = FONT.get(ch, BLANK)
        for r in range(7):
            bits = rows[r]
            if not bits:
                continue
            for c in range(5):
                if bits & (1 << (4 - c)):
                    fill_rect(cx + c * sx, y + r * sy,
                              cx + (c + 1) * sx, y + (r + 1) * sy, color)
                    if bold:
                        fill_rect(cx + c * sx + 1, y + r * sy,
                                  cx + (c + 1) * sx + 1, y + (r + 1) * sy,
                                  color)
        cx += 6 * sx
    return cx


def wrap(s, max_w, sx):
    words = normalize(s).split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w) if cur else w
        if text_w(trial, sx) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(x, y, s, max_w, sx, sy, color, max_lines, line_h, bold=False):
    lines = wrap(s, max_w, sx)[:max_lines]
    for i, ln in enumerate(lines):
        draw_text(x, y + i * line_h, ln, sx, sy, color, bold)
    return len(lines)


# ---------------------------------------------------------------- stories
HEROES = [
    ("SHENZHEN · SUMMIT",
     "TRUMP, XI AND PUTIN IN FIRST THREE-WAY SUMMIT",
     "Nuclear security and the Ukraine war top the agenda in Shenzhen."),
    ("VICE CITY · GAMES",
     "GTA VI LAUNCHES AFTER 13 YEARS OF WAITING",
     "Metacritic 99. Over $1B to make, 15.88M pre-orders. Take-Two shares up."),
    ("NASDAQ · MARKETS",
     "ANTHROPIC IPO AT $81.3B, LARGEST EVER",
     "Shares priced at $83 in the biggest listing in history."),
]

GRID1 = [
    ("THE HAGUE · LAW", "WORLD COURT RULES ON MYANMAR",
     "Delivers its verdict under the 1948 Genocide Convention.", RED),
    ("KYIV · WAR", "KERCH BRIDGE HIT AGAIN, TRAFFIC",
     "Explosions target span; transit halted.", BLUE),
    ("GAZA · WAR", "ISRAEL LAUNCHES GROUND OPERATION",
     "Troops advance into Nuseirat.", BLUE),
    ("GAZA · CRISIS", "RAIN DEEPENS GAZA SHELTER CRISIS",
     "46,000+ households displaced.", BLUE),
]

GRID2 = [
    ("TALLINN · EUROPE",
     "ESTONIA TO SHUT LAND BORDER WITH RUSSIA FROM 1 DEC",
     "Security measures tightened along eastern border.", ORANGE),
    ("ODISHA · STORM", "CYCLONE AKVAN NEARS INDIA'S EAST COAST",
     "Coastal alerts issued as severe tropical storm nears.", ORANGE),
    ("ANTALYA · CLIMATE", "COP31 ENTERS FINAL 48 HOURS, TALKS STILL",
     "Finance and fossil-fuel phaseout divide.", ORANGE),
]

BRIEFS = [
    "Houthis take Red Sea coast as Yemen pulls back",
    "Zelensky urges US to lift Starlink restrictions",
    "EU proposes €45B Ukraine loan for 2027",
    "US Republicans threaten to strip Ukraine aid",
    "Myanmar president rethinks ASEAN diplomatic ties",
    "US panel urges action on Panama ship seizure",
    "Bukele demolishes gang leader home in Haiti",
    "Suspected Russian spy held in Silicon Valley",
    "Ukraine-Russia-US talks in Abu Dhabi on swaps",
    "Voyager 1 is now one light-day from Earth",
    "Nvidia quarter at $115.8B amid chip curbs",
    "US-China announce rare-earth export curbs",
    "Global stocks dip ahead of Nvidia report",
    "Australia sanctions West Bank settlers",
    "Brent crude steady near $92 as surplus looms",
]


# ---------------------------------------------------------------- hero art
def art_skyline(x, y, w, h):
    fill_rect(x, y, x + w, y + h, SKY)
    for bx, bw, bh in [(8, 26, 34), (72, 24, 30), (132, 22, 26),
                       (222, 24, 30), (282, 22, 28)]:
        fill_rect(x + bx, y + h - bh, x + bx + bw, y + h, BLDG_LT)
    for bx, bw, bh in [(38, 30, 56), (100, 28, 46), (158, 30, 62),
                       (192, 26, 40), (250, 28, 54)]:
        fill_rect(x + bx, y + h - bh, x + bx + bw, y + h, BLDG_DARK)
    fill_rect(x, y + h - 10, x + w, y + h, GROUND)
    fill_circle(x + 60, y + h - 5, 3, RED)
    fill_circle(x + 120, y + h - 5, 3, BLUE)
    fill_circle(x + 180, y + h - 5, 3, INK)


def art_sunset(x, y, w, h):
    fill_rect(x, y, x + w, y + 26, SUN_Y)
    fill_rect(x, y + 26, x + w, y + 52, SUN_O)
    fill_rect(x, y + 52, x + w, y + h, SUN_R)
    fill_circle(x + 205, y + 30, 20, SUN)
    tx = x + 42
    fill_rect(tx - 1, y + 24, tx + 2, y + h, INK)
    for dx, dy in [(-24, -14), (-14, -18), (0, -20), (14, -18),
                   (24, -14), (-28, -6), (28, -6)]:
        line(tx, y + 24, tx + dx, y + 24 + dy, INK)
    fill_rect(x + 140, y + h - 16, x + 190, y + h - 6, INK)
    fill_rect(x + 152, y + h - 24, x + 178, y + h - 16, INK)
    fill_circle(x + 150, y + h - 6, 3, INK)
    fill_circle(x + 180, y + h - 6, 3, INK)


def art_chart(x, y, w, h):
    fill_rect(x, y, x + w, y + h, CHART_BG)
    for gy in (y + 20, y + 40, y + 60):
        hline(x + 4, x + w - 4, gy, CHART_GRID)
    bars = [18, 26, 22, 34, 30, 42, 38, 52]
    pts = []
    for i, bh in enumerate(bars):
        bx = x + 14 + i * 36
        fill_rect(bx, y + h - bh, bx + 26, y + h, BAR)
        pts.append((bx + 13, y + h - bh - 8))
    for i in range(len(pts) - 1):
        line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], TREND)
    for px_, py_ in pts:
        fill_circle(px_, py_, 3, TREND)


# ---------------------------------------------------------------- png out
def chunk(typ, data):
    return (struct.pack(">I", len(data)) + typ + data +
            struct.pack(">I", binascii.crc32(typ + data) & 0xFFFFFFFF))


def save_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += fb[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
           chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- layout
def main():
    rect(8, 8, 1016, 845, INK)

    # masthead
    draw_text(28, 20, "THE WORLD IN ONE PICTURE", 2, 2, RED)
    lab = "INTERNATIONAL EDITION"
    draw_text(996 - text_w(lab, 2), 20, lab, 2, 2, GREY)
    hline(28, 996, 42, INK)

    # title
    draw_text(28, 52, "THURSDAY 19 NOVEMBER 2026", 5, 5, INK)
    hline(28, 996, 94, INK)

    # heroes
    hero_y = 102
    hero_h = 204
    hero_x = [28, 354, 680]
    hero_w = 313
    arts = [art_skyline, art_sunset, art_chart]
    for i, (label, head, summ) in enumerate(HEROES):
        x0 = hero_x[i]
        rect(x0, hero_y, x0 + hero_w, hero_y + hero_h, INK)
        arts[i](x0 + 2, hero_y + 2, hero_w - 4, 78)
        draw_text(x0 + 6, hero_y + 88, label, 2, 2, RED)
        draw_wrapped(x0 + 6, hero_y + 108, head, hero_w - 12,
                     2, 2, INK, 2, 18, bold=True)
        draw_wrapped(x0 + 6, hero_y + 148, summ, hero_w - 12,
                     2, 2, GREY, 3, 18)

    # grid row 1 (4 cards)
    g1_y = 314
    g_h = 90
    g1_x = [28, 273, 518, 763]
    g1_w = 231
    for i, (label, head, summ, stripe) in enumerate(GRID1):
        x0 = g1_x[i]
        rect(x0, g1_y, x0 + g1_w, g1_y + g_h, INK)
        fill_rect(x0 + 1, g1_y + 1, x0 + g1_w - 1, g1_y + 5, stripe)
        draw_text(x0 + 6, g1_y + 8, label, 2, 2, RED)
        draw_wrapped(x0 + 6, g1_y + 24, head, g1_w - 12,
                     2, 2, INK, 2, 16, bold=True)
        draw_wrapped(x0 + 6, g1_y + 56, summ, g1_w - 12,
                     2, 2, GREY, 2, 16)

    # grid row 2 (3 cards)
    g2_y = 412
    g2_x = [28, 355, 682]
    g2_w = 313
    for i, (label, head, summ, stripe) in enumerate(GRID2):
        x0 = g2_x[i]
        rect(x0, g2_y, x0 + g2_w, g2_y + g_h, INK)
        fill_rect(x0 + 1, g2_y + 1, x0 + g2_w - 1, g2_y + 5, stripe)
        draw_text(x0 + 6, g2_y + 8, label, 2, 2, RED)
        draw_wrapped(x0 + 6, g2_y + 24, head, g2_w - 12,
                     2, 2, INK, 2, 16, bold=True)
        draw_wrapped(x0 + 6, g2_y + 56, summ, g2_w - 12,
                     2, 2, GREY, 2, 16)

    # briefs
    draw_text(28, 516, "GLOBAL DISPATCHES IN BRIEF", 2, 2, INK, bold=True)
    hline(28, 996, 534, INK)
    col_x = [28, 354, 680]
    rows_y = [542, 565, 588, 611, 634]
    for col in range(3):
        for row in range(5):
            b = BRIEFS[col * 5 + row]
            y = rows_y[row]
            fill_rect(col_x[col] + 2, y + 4, col_x[col] + 8, y + 10, RED)
            draw_text(col_x[col] + 14, y, b, 1, 2, INK)

    # bottom strip: map
    fill_ellipse(85, 685, 45, 18, MAPC)
    fill_ellipse(60, 720, 22, 16, MAPC)
    fill_ellipse(120, 745, 18, 26, MAPC)
    fill_ellipse(185, 690, 32, 16, MAPC)
    fill_ellipse(200, 740, 36, 28, MAPC)
    fill_ellipse(235, 775, 14, 10, MAPC)
    draw_text(28, 812, "WORLD SUMMARY MAP", 2, 2, GREY)

    # bottom strip: date check box
    fill_rect(262, 664, 668, 776, BOXFILL)
    rect(262, 664, 668, 776, INK)
    draw_text(278, 686, "DATE CHECK & VERIFICATION", 2, 2, RED)
    draw_text(278, 712, "✓ THURSDAY 19 NOVEMBER 2026", 2, 2, INK)
    draw_text(278, 738, "AUTHENTICATED WORLD DESK", 2, 2, GREY)

    # bottom strip: sources
    draw_text(684, 664, "SOURCES & WIRE SERVICES:", 2, 2, RED)
    draw_text(684, 690, "REUTERS · AP · BBC ·", 2, 2, INK)
    draw_text(684, 716, "FINANCIAL TIMES · BERNAMA", 2, 2, INK)
    draw_text(684, 742, "PUBLISHED WORLDWIDE", 2, 2, GREY)

    out = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"),
                       "entry.png")
    save_png(out)


main()
