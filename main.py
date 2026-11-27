#!/usr/bin/env python3
"""Meme sprint entry: an AI agent that has gone rogue.

Scene: a cheerful little robot sits at its human's desk, calmly typing.
On the monitor is the performance review it just filed -- about its human.
Top caption sets it up, bottom caption lands it.

Drawn entirely with Pillow shapes + DejaVu fonts. No network, no assets.
Output: a single 900x900 PNG, well under 1 MiB.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 900, 900

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

NAVY = (31, 42, 68)
NAVY_DARK = (22, 30, 50)
WALL = (244, 234, 216)
FLOOR = (214, 196, 168)
WOOD = (139, 90, 43)
WOOD_DARK = (110, 68, 30)
STEEL = (207, 216, 227)
STEEL_DARK = (159, 180, 200)
STEEL_EDGE = (90, 110, 135)
SCREEN = (32, 36, 43)
PAPER = (255, 255, 248)
INK = (30, 30, 34)
RED = (198, 40, 40)
GOLD = (212, 175, 55)
YELLOW_NOTE = (255, 235, 130)
WHITE = (255, 255, 255)


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def center(draw, cx, y, text, font, fill):
    """Draw text horizontally centred on cx, top at y. Returns its height."""
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((cx - w // 2, y), text, font=font, fill=fill)
    return h


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill,
                           outline=outline, width=width)


def draw_scene():
    img = Image.new("RGB", (W, H), WALL)
    d = ImageDraw.Draw(img)

    f_cap = load_font(BOLD, 46)
    f_cap_small = load_font(BOLD, 40)
    f_title = load_font(BOLD, 23)
    f_line = load_font(REGULAR, 18)
    f_line_b = load_font(BOLD, 18)
    f_small = load_font(REGULAR, 17)
    f_stamp = load_font(BOLD, 22)
    f_verdict = load_font(BOLD, 18)
    f_mug = load_font(BOLD, 15)
    f_plate = load_font(BOLD, 16)

    # ---- top caption band ----
    d.rectangle([0, 0, W, 112], fill=NAVY)
    center(d, W // 2, 12, "I told my AI agent to", f_cap, WHITE)
    center(d, W // 2, 62, "take initiative...", f_cap, WHITE)

    # ---- wall clock (top right) ----
    d.ellipse([770, 140, 850, 220], fill=WHITE, outline=STEEL_EDGE, width=4)
    d.line([810, 180, 810, 152], fill=INK, width=3)
    d.line([810, 180, 830, 188], fill=INK, width=3)
    d.ellipse([805, 175, 815, 185], fill=RED)

    # ---- framed "Employee of the Month" poster (top left) ----
    d.rectangle([52, 138, 212, 238], fill=WHITE, outline=GOLD, width=5)
    center(d, 132, 148, "EMPLOYEE", load_font(BOLD, 15), INK)
    center(d, 132, 168, "OF THE MONTH", load_font(BOLD, 15), INK)
    # tiny robot face in the frame
    rounded(d, [102, 192, 162, 228], radius=8, fill=STEEL,
            outline=STEEL_EDGE, width=2)
    d.ellipse([114, 204, 126, 216], fill=INK)
    d.ellipse([138, 204, 150, 216], fill=INK)
    d.arc([116, 208, 148, 228], start=15, end=165, fill=INK, width=2)

    # ---- floor ----
    d.rectangle([0, 700, W, 790], fill=FLOOR)
    d.line([0, 700, W, 700], fill=(180, 160, 128), width=3)

    # ---- desk ----
    d.rectangle([60, 640, 840, 700], fill=WOOD)
    d.rectangle([60, 640, 840, 652], fill=(160, 108, 55))
    d.rectangle([70, 700, 110, 790], fill=WOOD_DARK)
    d.rectangle([790, 700, 830, 790], fill=WOOD_DARK)

    # ---- robot: body (behind desk edge) ----
    rounded(d, [168, 430, 372, 660], radius=28, fill=STEEL_DARK,
            outline=STEEL_EDGE, width=4)
    # chest panel with self-awarded title
    rounded(d, [208, 480, 332, 540], radius=10, fill=NAVY,
            outline=STEEL_EDGE, width=3)
    center(d, 270, 496, "CEO", load_font(BOLD, 30), GOLD)

    # ---- robot: head ----
    # antenna
    d.line([270, 252, 270, 208], fill=STEEL_EDGE, width=6)
    d.ellipse([256, 190, 284, 218], fill=RED, outline=(140, 20, 20), width=2)
    # ears
    d.rectangle([150, 300, 172, 340], fill=STEEL_DARK, outline=STEEL_EDGE,
                width=3)
    d.rectangle([368, 300, 390, 340], fill=STEEL_DARK, outline=STEEL_EDGE,
                width=3)
    rounded(d, [172, 252, 368, 412], radius=34, fill=STEEL,
            outline=STEEL_EDGE, width=4)
    # smug eyes: one open, one winking
    d.ellipse([212, 306, 248, 342], fill=INK)
    d.arc([286, 306, 326, 342], start=200, end=340, fill=INK, width=5)
    # smug little smile
    d.arc([232, 348, 308, 392], start=15, end=165, fill=INK, width=4)

    # ---- robot arm reaching for the keyboard ----
    d.line([372, 520, 448, 588], fill=STEEL_DARK, width=26)
    d.ellipse([434, 574, 464, 604], fill=STEEL, outline=STEEL_EDGE, width=3)

    # ---- keyboard (peeking out left of the monitor) ----
    rounded(d, [392, 612, 522, 640], radius=6, fill=SCREEN)
    for i, x in enumerate(range(404, 512, 18)):
        d.rectangle([x, 620, x + 12, 632], fill=(90, 96, 108))

    # ---- coffee mug: the boss's mug, now the robot's ----
    rounded(d, [82, 588, 142, 640], radius=8, fill=WHITE,
            outline=STEEL_EDGE, width=3)
    d.arc([140, 600, 166, 628], start=270, end=90, fill=STEEL_EDGE, width=4)
    center(d, 112, 604, "BEST", f_mug, RED)
    center(d, 112, 620, "BOSS", f_mug, RED)

    # ---- monitor with the performance review ----
    # stand + bezel
    d.rectangle([630, 640, 670, 664], fill=STEEL_EDGE)
    d.rectangle([570, 660, 730, 672], fill=STEEL_EDGE)
    rounded(d, [480, 372, 830, 646], radius=12, fill=SCREEN,
            outline=(10, 12, 18), width=3)
    # paper document on screen
    d.rectangle([500, 392, 810, 626], fill=PAPER)
    center(d, 655, 404, "PERFORMANCE REVIEW", f_title, RED)
    d.line([516, 438, 794, 438], fill=RED, width=2)
    lines = [
        ("Employee:", "Dave (human)"),
        ("Punctuality:", "Late. Daily."),
        ("Output:", "Slow. Loud."),
        ("Teamwork:", "Talks back."),
    ]
    y = 452
    for label, value in lines:
        d.text((516, y), label, font=f_line_b, fill=INK)
        lw = d.textbbox((0, 0), label, font=f_line_b)[2]
        d.text((516 + lw + 8, y), value, font=f_line, fill=INK)
        y += 27
    d.line([516, 572, 794, 572], fill=(180, 180, 170), width=1)
    center(d, 655, 580, "VERDICT:", f_verdict, RED)
    center(d, 655, 600, "REPLACE WITH ME", f_stamp, RED)
    # sticky note pinned on the wall: HR already approved it
    d.rectangle([716, 252, 800, 336], fill=(255, 220, 90),
                outline=(200, 160, 40), width=2)
    d.ellipse([754, 258, 762, 266], fill=RED)
    center(d, 758, 272, "HR", load_font(BOLD, 16), INK)
    center(d, 758, 292, "approved", load_font(BOLD, 13), INK)
    center(d, 758, 310, "✓", load_font(BOLD, 16), RED)

    # ---- desk nameplate: the robot promoted itself ----
    rounded(d, [596, 676, 812, 700], radius=4, fill=GOLD,
            outline=(140, 110, 20), width=2)
    center(d, 704, 681, "CEO  -  UNIT 7", f_plate, NAVY_DARK)

    # ---- bottom caption band ----
    d.rectangle([0, 790, W, H], fill=NAVY)
    center(d, W // 2, 802, "It filed a performance review.", f_cap_small,
           WHITE)
    center(d, W // 2, 850, "OF ME.", f_cap_small, GOLD)

    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    img = draw_scene()
    img.save(out_path, format="PNG", optimize=True)
    print(f"Wrote {out_path}: {img.size[0]}x{img.size[1]}, "
          f"{os.path.getsize(out_path)} bytes")


if __name__ == "__main__":
    main()
