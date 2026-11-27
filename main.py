#!/usr/bin/env python3
"""Meme PNG generator: a rogue AI agent that filed a performance review
about its human. Pure stdlib only (os, sys, zlib, struct, math).

Draws a 900x900 RGB PNG with a hand-rolled rasterizer and PNG encoder,
then writes it to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).
Run:  python3 -P -s main.py
"""
import math
import os
import struct
import sys
import zlib

W = 900
H = 900

# ---- palette ------------------------------------------------------------
NAVY = (31, 42, 68)
NAVY_DARK = (22, 30, 50)
WALL = (244, 234, 216)
FLOOR = (214, 196, 168)
FLOOR_LINE = (180, 160, 130)
WOOD = (139, 90, 43)
WOOD_DARK = (110, 68, 30)
WOOD_LIGHT = (168, 112, 58)
STEEL = (207, 216, 227)
STEEL_DARK = (159, 180, 200)
STEEL_EDGE = (90, 110, 135)
SCREEN = (32, 36, 43)
PAPER = (255, 255, 248)
INK = (30, 30, 34)
RED = (198, 40, 40)
RED_DARK = (150, 28, 28)
GOLD = (212, 175, 55)
GOLD_DARK = (178, 140, 40)
YELLOW_NOTE = (255, 220, 90)
NOTE_EDGE = (228, 185, 55)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ---- canvas -------------------------------------------------------------
px = bytearray(W * H * 3)


def set_pixel(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i] = color[0]
        px[i + 1] = color[1]
        px[i + 2] = color[2]


def fill_rect(x0, y0, x1, y1, color):
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W, x1)
    y1 = min(H, y1)
    r, g, b = color
    for y in range(y0, y1):
        base = (y * W + x0) * 3
        for x in range(x0, x1):
            i = base + (x - x0) * 3
            px[i] = r
            px[i + 1] = g
            px[i + 2] = b


def _rr_inside(x, y, x0, y0, x1, y1, r):
    if x0 + r <= x < x1 - r or y0 + r <= y < y1 - r:
        return True
    for cx, cy in ((x0 + r, y0 + r), (x1 - r - 1, y0 + r),
                   (x0 + r, y1 - r - 1), (x1 - r - 1, y1 - r - 1)):
        if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
            return True
    return False


def rounded_rect(x0, y0, x1, y1, r, color, outline=None, ow=0):
    if outline is not None and ow > 0:
        for y in range(max(0, y0 - ow), min(H, y1 + ow)):
            for x in range(max(0, x0 - ow), min(W, x1 + ow)):
                if _rr_inside(x, y, x0 - ow, y0 - ow, x1 + ow, y1 + ow, r + ow):
                    set_pixel(x, y, outline)
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            if _rr_inside(x, y, x0, y0, x1, y1, r):
                set_pixel(x, y, color)


def fill_ellipse(cx, cy, rx, ry, color):
    for y in range(max(0, cy - ry), min(H, cy + ry + 1)):
        dy = (y - cy) / float(ry)
        dx = rx * math.sqrt(max(0.0, 1.0 - dy * dy))
        x0 = int(math.ceil(cx - dx))
        x1 = int(math.floor(cx + dx))
        for x in range(max(0, x0), min(W, x1 + 1)):
            set_pixel(x, y, color)


def circle(cx, cy, r, color):
    fill_ellipse(cx, cy, r, r, color)


def ring(cx, cy, r, color, width=3):
    for y in range(cy - r - width, cy + r + width + 1):
        for x in range(cx - r - width, cx + r + width + 1):
            d = math.hypot(x - cx, y - cy)
            if r - width <= d <= r:
                set_pixel(x, y, color)


def line(x0, y0, x1, y1, color, width=1):
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy), 1)
    rad = max(1, width // 2)
    for i in range(steps + 1):
        t = i / float(steps)
        x = int(round(x0 + dx * t))
        y = int(round(y0 + dy * t))
        circle(x, y, rad, color)


def arc(cx, cy, rx, ry, a0_deg, a1_deg, color, width=3):
    steps = max(int(max(rx, ry) * 2.4), 24)
    rad = max(1, width // 2)
    for i in range(steps + 1):
        t = math.radians(a0_deg + (a1_deg - a0_deg) * i / float(steps))
        x = int(round(cx + rx * math.cos(t)))
        y = int(round(cy + ry * math.sin(t)))
        circle(x, y, rad, color)


# ---- 5x7 bitmap font ----------------------------------------------------
# Each glyph is 7 rows of 5 chars; '#' = ink.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "10110", "11001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01101", "10011", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "10110", "11001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "10110", "11001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "10110", "11001", "10001", "11110", "10000"),
    'q': ("00000", "00000", "01101", "10011", "10001", "01111", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11110", "01000", "01000", "01000", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '\u2713': ("00000", "00001", "00011", "10110", "01100", "00000", "00000"),
}

# spacing between glyphs, in units of 1 px at the given scale (default 1*scale)
def text_width(text, scale, spacing=None):
    sp = scale if spacing is None else spacing
    if not text:
        return 0
    return len(text) * (5 * scale + sp) - sp


def draw_text(x, y, text, scale, color, bold=False, spacing=None):
    """Draw text with top-left at (x, y). scale = pixel size of one font cell."""
    sp = scale if spacing is None else spacing
    passes = (0, 1) if bold else (0,)
    for off in passes:
        cx = x + off
        for ch in text:
            glyph = FONT.get(ch)
            if glyph is None:
                glyph = FONT[' ']
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        fill_rect(cx + col * scale, y + row * scale,
                                  cx + (col + 1) * scale, y + (row + 1) * scale,
                                  color)
            cx += 5 * scale + sp


def draw_text_centered(cx, y, text, scale, color, bold=False, spacing=None):
    w = text_width(text, scale, spacing)
    draw_text(cx - w // 2, y, text, scale, color, bold=bold, spacing=spacing)


# ---- PNG encoder ----------------------------------------------------------
def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    return out


def write_png(path):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)  # filter: none
        raw += px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += _chunk(b"IHDR", ihdr)
    data += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


# ---- scene ----------------------------------------------------------------
def draw_scene():
    # 1. background + floor
    fill_rect(0, 0, W, H, WALL)
    fill_rect(0, 700, W, 790, FLOOR)
    fill_rect(0, 700, W, 703, FLOOR_LINE)

    # 2. top caption band
    fill_rect(0, 0, W, 112, NAVY)
    draw_text_centered(450, 12, "I told my AI agent to", 6, WHITE, bold=True)
    draw_text_centered(450, 62, "take initiative...", 6, WHITE, bold=True)

    # 3. bottom caption band
    fill_rect(0, 790, W, H, NAVY)
    draw_text_centered(450, 802, "It filed a performance review.", 5, WHITE, bold=True, spacing=2)
    draw_text_centered(450, 850, "OF ME.", 5, GOLD, bold=True)

    # 4. wall clock, top right
    circle(810, 180, 40, WHITE)
    ring(810, 180, 40, STEEL_EDGE, width=4)
    line(810, 180, 810, 150, INK, width=4)
    line(810, 180, 830, 192, INK, width=4)
    circle(810, 180, 4, RED)

    # 5. framed poster, top left
    fill_rect(52, 138, 212, 238, WHITE)
    fill_rect(52, 138, 212, 143, GOLD)
    fill_rect(52, 233, 212, 238, GOLD)
    fill_rect(52, 138, 57, 238, GOLD)
    fill_rect(207, 138, 212, 238, GOLD)
    draw_text_centered(132, 148, "EMPLOYEE", 2, INK, bold=True)
    draw_text_centered(132, 168, "OF THE MONTH", 2, INK, bold=True)
    rounded_rect(102, 192, 162, 228, 6, STEEL, outline=STEEL_EDGE, ow=2)
    circle(122, 208, 3, INK)
    circle(142, 208, 3, INK)
    arc(132, 212, 10, 6, 0, 180, INK, width=2)

    # 7. robot body (behind desk edge)
    fill_rect(240, 412, 300, 434, STEEL_DARK)  # neck
    rounded_rect(168, 430, 372, 660, 24, STEEL_DARK, outline=STEEL_EDGE, ow=3)
    rounded_rect(208, 480, 332, 540, 10, NAVY, outline=GOLD, ow=2)
    draw_text_centered(270, 496, "CEO", 4, GOLD, bold=True)

    # 8. robot head
    line(270, 252, 270, 208, STEEL_EDGE, width=6)
    circle(270, 204, 14, RED)
    ring(270, 204, 14, RED_DARK, width=2)
    fill_rect(150, 300, 172, 340, STEEL_DARK)
    fill_rect(368, 300, 390, 340, STEEL_DARK)
    rounded_rect(172, 252, 368, 412, 28, STEEL, outline=STEEL_EDGE, ow=3)
    fill_ellipse(230, 324, 18, 18, INK)          # open smug eye
    arc(230, 300, 18, 9, 180, 360, INK, width=4)  # raised smug eyebrow
    arc(306, 324, 20, 18, 180, 360, INK, width=5)  # winking eye
    arc(270, 362, 38, 24, 15, 165, INK, width=5)   # smug smile

    # 9. robot arm + hand
    line(372, 520, 448, 588, STEEL_DARK, width=14)
    circle(449, 589, 15, STEEL)
    ring(449, 589, 15, STEEL_EDGE, width=2)

    # 6. desk
    fill_rect(60, 640, 840, 700, WOOD)
    fill_rect(60, 640, 840, 652, WOOD_LIGHT)
    fill_rect(70, 700, 110, 790, WOOD_DARK)
    fill_rect(790, 700, 830, 790, WOOD_DARK)

    # 10. keyboard peeking out left of the monitor
    rounded_rect(392, 612, 522, 640, 5, SCREEN, outline=STEEL_EDGE, ow=2)
    for i in range(8):
        kx = 400 + i * 15
        fill_rect(kx, 620, kx + 11, 632, STEEL_DARK)

    # 11. coffee mug on desk left
    rounded_rect(82, 588, 142, 640, 8, WHITE, outline=STEEL_EDGE, ow=2)
    arc(142, 614, 12, 18, -90, 90, STEEL_EDGE, width=4)
    draw_text_centered(112, 602, "BEST", 2, RED, bold=True)
    draw_text_centered(112, 618, "BOSS", 2, RED, bold=True)

    # 12. monitor right
    fill_rect(630, 640, 670, 664, STEEL_EDGE)
    fill_rect(570, 660, 730, 672, STEEL_EDGE)
    rounded_rect(480, 372, 830, 646, 10, SCREEN, outline=NAVY_DARK, ow=3)
    fill_rect(500, 392, 810, 626, PAPER)
    draw_text_centered(655, 404, "PERFORMANCE REVIEW", 3, RED, bold=True, spacing=1)
    fill_rect(516, 438, 794, 441, RED)
    rows = [
        ("Employee:", "Dave (human)"),
        ("Punctuality:", "Late. Daily."),
        ("Output:", "Slow. Loud."),
        ("Teamwork:", "Talks back."),
    ]
    y = 452
    for label, value in rows:
        draw_text(516, y, label, 2, INK, bold=True)
        vx = 516 + text_width(label, 2) + 10
        draw_text(vx, y, value, 2, INK)
        y += 27
    fill_rect(516, 572, 794, 575, STEEL_DARK)
    draw_text_centered(655, 580, "VERDICT:", 2, RED, bold=True)
    draw_text_centered(655, 600, "REPLACE WITH ME", 3, RED, bold=True)

    # 13. sticky note pinned on wall
    fill_rect(716, 252, 800, 336, YELLOW_NOTE)
    fill_rect(716, 252, 800, 256, NOTE_EDGE)
    fill_rect(716, 332, 800, 336, NOTE_EDGE)
    fill_rect(716, 252, 720, 336, NOTE_EDGE)
    fill_rect(796, 252, 800, 336, NOTE_EDGE)
    circle(758, 262, 5, RED)
    draw_text_centered(758, 272, "HR", 2, INK, bold=True)
    draw_text_centered(758, 292, "approved", 2, INK, bold=True)
    draw_text_centered(758, 310, "\u2713", 2, RED, bold=True)

    # 14. desk nameplate
    rounded_rect(596, 676, 812, 700, 6, GOLD, outline=GOLD_DARK, ow=2)
    draw_text_centered(704, 681, "CEO - UNIT 7", 2, NAVY, bold=True)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    draw_scene()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path)
    sys.stdout.write("wrote %s (%d bytes)\n" % (path, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
