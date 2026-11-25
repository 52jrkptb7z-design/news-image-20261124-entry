#!/usr/bin/env python3
"""The World in One Day -- Tuesday, 24 November 2026.

Draws a one-page newspaper front page summing up 24 November 2026
in world news. Pure standard library: the image is a bytearray canvas,
text is rendered with an embedded 5x7 bitmap font, and the PNG is
encoded by hand (zlib + struct). No network, no randomness, no clock:
two runs produce byte-identical output.

Run:  python3 main.py        -> writes /output/entry.png
"""

import os
import struct
import zlib

# ---------------------------------------------------------------- canvas
W, H = 1024, 1024
PAPER = (246, 241, 231)
INK = (26, 26, 26)
RED = (166, 30, 30)
GREEN = (28, 112, 52)
NAVY = (31, 58, 95)
GREY = (110, 104, 92)
LIGHT = (226, 219, 203)

canvas = bytearray(bytes(PAPER) * (W * H))


def px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        canvas[i:i + 3] = bytes(color)


def rect(x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(color) * (x1 - x0)
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        canvas[i:i + len(row)] = row


def hline(x, y, w, color, t=1):
    rect(x, y, w, t, color)


def vline(x, y, h, color, t=1):
    rect(x, y, t, h, color)


def line(x0, y0, x1, y1, color, t=2):
    """Bresenham line with square thickness."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    half = t // 2
    while True:
        rect(x0 - half, y0 - half, t, t, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


# ------------------------------------------------------------------ font
# 5x7 bitmap font: each glyph is 7 rows of 5 bits, MSB = left column.
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
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "-": (0, 0, 0, 0x1F, 0, 0, 0),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    '"': (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    "·": (0, 0, 0, 0x0C, 0x0C, 0, 0),
}

BLANK = (0, 0, 0, 0, 0, 0, 0)


def char_w(scale):
    return 6 * scale


def text_w(text, scale):
    return len(text) * char_w(scale) - scale


def draw_char(x, y, ch, scale, color):
    glyph = FONT.get(ch, BLANK)
    for row in range(7):
        bits = glyph[row]
        for col in range(5):
            if bits & (0x10 >> col):
                rect(x + col * scale, y + row * scale, scale, scale, color)


def draw_text(x, y, text, scale, color):
    """Draw one line, upper-cased; returns the width drawn."""
    cx = x
    for ch in text.upper():
        draw_char(cx, y, ch, scale, color)
        cx += char_w(scale)
    return cx - x - scale


def draw_centered(y, text, scale, color, x0=0, x1=W):
    w = text_w(text, scale)
    draw_text(x0 + (x1 - x0 - w) // 2, y, text, scale, color)


def wrap_lines(text, scale, max_w):
    """Greedy word wrap on whole words; returns list of lines."""
    words = text.upper().split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def paragraph(x, y, text, scale, color, max_w, leading=None):
    """Draw wrapped paragraph; returns y just past the last line."""
    lh = leading if leading is not None else 7 * scale + 4
    for ln in wrap_lines(text, scale, max_w):
        draw_text(x, y, ln, scale, color)
        y += lh
    return y


# ----------------------------------------------------------------- content
MASTHEAD = "THE WORLD IN ONE DAY"
DATE_LINE = "TUESDAY, 24 NOVEMBER 2026"
TAGLINE = "ONE DAY  -  ONE PAGE  -  THE WORLD"

HERO_HEAD = "HUANG RETURNS TO NVIDIA"
HERO_SUB = ("BOARD REINSTATES CHIEF EXECUTIVE AFTER TRUMP PUSH; "
            "SHARES JUMP ABOUT 30% AS WALL STREET RALLIES")

STORIES = [
    ("VERDICT IN NEW YORK",
     "HUAWEI GUILTY OF TRADE-SECRET THEFT",
     "A US JURY CONVICTS THE CHINESE TECH GIANT OF CONSPIRACY "
     "TO STEAL TRADE SECRETS AND BANK FRAUD, BUT ACQUITS IT OF "
     "THE MORE SERIOUS RACKETEERING CHARGE."),
    ("WAR AT SEA",
     "UKRAINE DRONES HIT RUSSIAN SHIPS",
     "KYIV SAYS ITS NAVAL DRONES STRUCK THE RUSSIAN CARGO SHIP "
     "SPARTA II IN THE GULF OF FINLAND AND A WARSHIP AT A BASE "
     "OFF LIBYA, AS THE WAR SPREADS."),
    ("GULF TENSION",
     "FOUR TANKERS HIT MINES IN HORMUZ",
     "IRAN SAYS FOUR OIL TANKERS STRUCK NAVAL MINES IN THE "
     "STRAIT OF HORMUZ AND CAUGHT FIRE; TEHRAN RULES OUT TALKS "
     "UNTIL WASHINGTON MEETS ITS CONDITIONS."),
    ("TRAGEDY IN TURKIYE",
     "HELICOPTER CRASH KILLS FIVE",
     "A TURKISH AIR FORCE AS-532 HELICOPTER CRASHES AFTER "
     "TAKEOFF FROM ESKISEHIR ON A TRAINING FLIGHT, KILLING "
     "ALL FIVE CREW MEMBERS ABOARD."),
]

BRIEFS = [
    "COLOMBIA: GUNMEN HOLD 25 HOSTAGE AT A SUPERMARKET IN CARTAGENA",
    "NEPAL: 5.6 MAGNITUDE EARTHQUAKE STRIKES NEAR THE CHINA BORDER",
    "WEATHER: KING TIDES FLOOD LOW-LYING CALIFORNIA COAST",
    "SPORT: REAL MADRID THRASH PSV 5-1; SENEGAL REGAIN AFCON TITLE",
]

MARKETS = "MARKETS: S&P +4.7% · NASDAQ +6.5% · NIKKEI +3.9% · GOLD $3,620 · BRENT $86.7"

FOOTER = "COMPILED FROM THE DAY'S REPORTING  -  24 NOVEMBER 2026"


# ------------------------------------------------------------------ layout
def draw_chip(cx, cy, w, h):
    """Stylised processor chip with pins and an NVDA label."""
    # pins
    for i in range(5):
        px0 = cx + 14 + i * ((w - 28) // 4)
        rect(px0, cy - 10, 6, 10, NAVY)
        rect(px0, cy + h, 6, 10, NAVY)
    for i in range(3):
        py0 = cy + 12 + i * ((h - 24) // 2)
        rect(cx - 10, py0, 10, 6, NAVY)
        rect(cx + w, py0, 10, 6, NAVY)
    rect(cx, cy, w, h, NAVY)
    rect(cx + 6, cy + 6, w - 12, h - 12, (255, 255, 255))
    # inner die
    rect(cx + w // 4, cy + h // 4, w // 2, h // 2, GREEN)
    draw_centered(cy + h // 2 - 7, "NVDA", 2, (255, 255, 255),
                  x0=cx + w // 4, x1=cx + 3 * w // 4)


def draw_hero_visual(x, y, w, h):
    """Rising market arrow over a chip, with a +30% tag."""
    rect(x, y, w, h, (255, 255, 255))
    vline(x, y, h, INK, 2)
    hline(x, y + h, w, INK, 2)
    # rising arrow line
    line(x + 14, y + h - 34, x + w // 3, y + h - 66, GREEN, 5)
    line(x + w // 3, y + h - 66, x + 2 * w // 3 - 10, y + h - 44, GREEN, 5)
    line(x + 2 * w // 3 - 10, y + h - 44, x + w - 26, y + 22, GREEN, 5)
    # arrow head
    line(x + w - 26, y + 22, x + w - 46, y + 24, GREEN, 5)
    line(x + w - 26, y + 22, x + w - 28, y + 42, GREEN, 5)
    draw_text(x + 12, y + 10, "+30%", 3, GREEN)
    draw_chip(x + 16, y + h - 78, 92, 56)


def draw_page():
    M = 36  # page margin
    # frame
    rect(0, 0, W, H, PAPER)
    hline(0, 10, W, INK, 3)
    hline(0, H - 11, W, INK, 3)

    # ---- masthead
    y = 30
    draw_centered(y, MASTHEAD, 6, INK)
    y += 7 * 6 + 14
    # dateline with side rules
    dw = text_w(DATE_LINE, 3)
    cx = (W - dw) // 2
    hline(M, y + 9, cx - M - 18, INK, 2)
    hline(cx + dw + 18, y + 9, W - M - (cx + dw + 18), INK, 2)
    draw_text(cx, y, DATE_LINE, 3, RED)
    y += 7 * 3 + 8
    draw_centered(y, TAGLINE, 2, GREY)
    y += 7 * 2 + 12
    hline(M, y, W - 2 * M, INK, 3)
    y += 16

    # ---- hero
    hero_w = 600
    vis_x = M + hero_w + 24
    vis_w = W - M - vis_x
    vis_h = 200
    hy = y
    y = paragraph(M, y, HERO_HEAD, 4, INK, hero_w, leading=7 * 4 + 8)
    y += 6
    y = paragraph(M, y, HERO_SUB, 2, INK, hero_w, leading=7 * 2 + 5)
    draw_hero_visual(vis_x, hy, vis_w, vis_h)
    y = max(y, hy + vis_h) + 10
    hline(M, y, W - 2 * M, INK, 2)
    y += 18

    # ---- story grid, 2 columns x 2 rows
    col_w = (W - 2 * M - 28) // 2
    col_x = [M, M + col_w + 28]
    row_y = y
    for idx, (kicker, head, body) in enumerate(STORIES):
        cx0 = col_x[idx % 2]
        cy = row_y + (idx // 2) * 200
        draw_text(cx0, cy, kicker, 2, RED)
        cy += 7 * 2 + 6
        cy = paragraph(cx0, cy, head, 3, INK, col_w, leading=7 * 3 + 5)
        cy += 4
        paragraph(cx0, cy, body, 2, INK, col_w, leading=7 * 2 + 4)
        if idx % 2 == 0:
            vline(cx0 + col_w + 13, row_y + (idx // 2) * 200, 180, LIGHT, 2)
    y = row_y + 2 * 200 + 8
    hline(M, y, W - 2 * M, INK, 2)
    y += 16

    # ---- briefs
    draw_text(M, y, "IN BRIEF", 2, RED)
    y += 7 * 2 + 8
    for brief in BRIEFS:
        draw_text(M + 18, y, ">", 2, RED)
        draw_text(M + 36, y, brief, 2, INK)
        y += 7 * 2 + 6
    y += 4
    hline(M, y, W - 2 * M, INK, 2)
    y += 14

    # ---- markets strip
    rect(M, y, W - 2 * M, 34, (255, 255, 255))
    hline(M, y, W - 2 * M, INK, 2)
    hline(M, y + 33, W - 2 * M, INK, 2)
    draw_centered(y + 10, MARKETS, 2, INK)
    y += 34 + 16

    # ---- footer
    draw_centered(y, FOOTER, 2, GREY)


# --------------------------------------------------------------------- png
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += canvas[yy * W * 3:(yy + 1) * W * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    draw_page()
    os.makedirs("/output", exist_ok=True)
    size = write_png("/output/entry.png")
    print("wrote /output/entry.png (%d bytes, %dx%d)" % (size, W, H))


if __name__ == "__main__":
    main()
