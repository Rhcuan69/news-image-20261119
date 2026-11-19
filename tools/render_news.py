#!/usr/bin/env python3
"""Render news-19-nov-2026.png: a one-page newspaper front page summing up
the world news of Thursday 19 November 2026.

Pure Python standard library only (zlib, struct, math): the PNG encoder
and the bitmap font below are written from scratch, no Pillow, no numpy.
Deterministic: same input, same bytes out.
Run: python3 tools/render_news.py  ->  writes news-19-nov-2026.png
(1024x1024, < 1 MiB).

Build-time tool only: the graded entry (main.py) never imports it; it
just copies the rendered PNG. All seven stories were first reported on
19 November 2026 (verified against at least two independent sources
this run: USA Today / NY Post / DPA for the summit; Amnesty / Reuters
for the ICJ ruling; Euronews / Al Jazeera for the Crimean Bridge;
AFP / Reuters for the Gaza raid ending; The Hindu BusinessLine / IANS
for Cyclone Akvan; Reuters / CoinDesk for the Anthropic IPO; Reuters /
The Guardian for the COP31 draft). Wording stays close to what was
reported, no hype, no invented facts.
"""
import math
import struct
import zlib

W, H = 1024, 1024
PAPER = (250, 245, 233)
INK = (22, 22, 22)
RED = (163, 22, 33)
GREY = (90, 86, 76)
BLUE = (28, 68, 140)
GOLD = (198, 148, 32)
GREEN = (38, 110, 68)
SKY = (120, 165, 205)

# ---------------------------------------------------------------- font
# 5x7 bitmap font, uppercase + digits + punctuation. Each glyph is 7 rows
# of 5 characters; '#' is ink, '.' is blank. Text is rendered in
# uppercase, which suits a newspaper front page.
FONT = {}
def _g(ch, rows):
    FONT[ch] = rows

_g("A", [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"])
_g("B", ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."])
_g("C", [".####", "#....", "#....", "#....", "#....", "#....", ".####"])
_g("D", ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."])
_g("E", ["#####", "#....", "#....", "####.", "#....", "#....", "#####"])
_g("F", ["#####", "#....", "#....", "####.", "#....", "#....", "#...."])
_g("G", [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."])
_g("H", ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"])
_g("I", ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"])
_g("J", ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."])
_g("K", ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"])
_g("L", ["#....", "#....", "#....", "#....", "#....", "#....", "#####"])
_g("M", ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"])
_g("N", ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"])
_g("O", [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."])
_g("P", ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."])
_g("Q", [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"])
_g("R", ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"])
_g("S", [".####", "#....", "#....", ".###.", "....#", "....#", "####."])
_g("T", ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."])
_g("U", ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."])
_g("V", ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."])
_g("W", ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"])
_g("X", ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"])
_g("Y", ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."])
_g("Z", ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"])
_g("0", [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."])
_g("1", ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."])
_g("2", [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"])
_g("3", ["####.", "....#", "....#", ".###.", "....#", "....#", "####."])
_g("4", ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."])
_g("5", ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."])
_g("6", [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."])
_g("7", ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."])
_g("8", [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."])
_g("9", [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."])
_g(" ", [".....", ".....", ".....", ".....", ".....", ".....", "....."])
_g(".", [".....", ".....", ".....", ".....", ".....", ".....", ".##.."])
_g(",", [".....", ".....", ".....", ".....", ".....", "..#..", ".#..."])
_g("'", ["..#..", "..#..", ".....", ".....", ".....", ".....", "....."])
_g("-", [".....", ".....", ".....", ".###.", ".....", ".....", "....."])
_g(":", [".....", "..#..", ".....", ".....", "..#..", ".....", "....."])
_g(";", [".....", "..#..", ".....", ".....", "..#..", ".#...", "....."])
_g("!", ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."])
_g("?", [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."])
_g("(", ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."])
_g(")", [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."])
_g("/", ["....#", "...#.", "...#.", "..#..", ".#...", "#....", "#...."])
_g("&", [".###.", "#...#", "#...#", ".#...", "#.#.#", "#..#.", ".##.#"])
_g("%", ["#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"])
_g("$", ["..#..", ".####", "#.#.#", ".#...", "..#.#", "####.", "..#.."])
_g("+", [".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."])
_g("=", [".....", ".....", ".###.", ".....", ".###.", ".....", "....."])
_g('"', [".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."])
_g("*", [".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."])
_g("#", [".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."])
_g("@", [".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."])
_g("_", [".....", ".....", ".....", ".....", ".....", ".....", "#####"])
_g("<", ["...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."])
_g(">", [".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."])
_g("~", [".....", ".....", ".##.#", "#.##.", ".....", ".....", "....."])

CHAR_W, CHAR_H = 5, 7


class Canvas:
    """An RGB pixel buffer with simple vector drawing."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def fill_rect(self, x0, y0, x1, y1, color):
        x0, x1 = max(0, x0), min(self.w, x1)
        y0, y1 = max(0, y0), min(self.h, y1)
        row = bytes(color) * (x1 - x0)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def rect(self, x0, y0, x1, y1, color, width=1):
        self.fill_rect(x0, y0, x1, y0 + width, color)
        self.fill_rect(x0, y1 - width, x1, y1, color)
        self.fill_rect(x0, y0, x0 + width, y1, color)
        self.fill_rect(x1 - width, y0, x1, y1, color)

    def hline(self, x0, x1, y, color, width=1):
        self.fill_rect(x0, y, x1, y + width, color)

    def vline(self, x, y0, y1, color, width=1):
        self.fill_rect(x, y0, x + width, y1, color)

    def line(self, x0, y0, x1, y1, color, width=1):
        """Bresenham line, with a square brush of the given width."""
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        half = width // 2
        while True:
            self.fill_rect(x - half, y - half, x - half + width,
                           y - half + width, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, color, fill=False):
        x, y, d = 0, r, 3 - 2 * r
        while x <= y:
            pts = [(cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y),
                   (cx - x, cy - y), (cx + y, cy + x), (cx - y, cy + x),
                   (cx + y, cy - x), (cx - y, cy - x)]
            for px, py in pts:
                self.set(px, py, color)
            if fill:
                for xx in range(cx - x, cx + x + 1):
                    self.set(xx, cy + y, color)
                    self.set(xx, cy - y, color)
                for xx in range(cx - y, cx + y + 1):
                    self.set(xx, cy + x, color)
                    self.set(xx, cy - x, color)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    # ------------------------------------------------------------- text
    def text_width(self, text, scale):
        return len(text) * (CHAR_W + 1) * scale - scale

    def draw_text(self, text, x, y, scale, color):
        text = text.upper()
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT["?"])
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == "#":
                        self.fill_rect(cx + gx * scale, y + gy * scale,
                                       cx + (gx + 1) * scale,
                                       y + (gy + 1) * scale, color)
            cx += (CHAR_W + 1) * scale
        return cx

    def draw_text_centred(self, text, cx, y, scale, color):
        w = self.text_width(text, scale)
        self.draw_text(text, cx - w // 2, y, scale, color)

    def wrap(self, text, scale, max_w):
        """Greedy word wrap; returns lines that fit max_w."""
        words = text.upper().split()
        lines, cur = [], ""
        for word in words:
            trial = (cur + " " + word).strip()
            if self.text_width(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


def save_png(canvas, path):
    """Encode the canvas as a PNG (8-bit RGB, filter 0) and write it."""
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(ctype, data):
        out = struct.pack(">I", len(data)) + ctype + data
        out += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)

# ---------------------------------------------------------------- icons
# Small drawn illustrations, one per story, in a 120x64 box.

def icon_summit(c, x, y):
    """Three flags on poles above a table: US, China, Russia."""
    # poles
    for px in (x + 18, x + 60, x + 102):
        c.vline(px, y + 2, y + 52, INK, 2)
    # US flag: stripes + blue canton
    fx, fy = x + 20, y + 4
    for i in range(7):
        c.fill_rect(fx, fy + i * 4, fx + 34, fy + i * 4 + 2,
                    RED if i % 2 == 0 else PAPER)
    c.fill_rect(fx, fy, fx + 14, fy + 14, BLUE)
    # China flag: red field, gold stars
    fx = x + 62
    c.fill_rect(fx, fy, fx + 34, fy + 26, RED)
    c.fill_rect(fx + 4, fy + 4, fx + 9, fy + 9, GOLD)
    c.fill_rect(fx + 12, fy + 3, fx + 15, fy + 6, GOLD)
    c.fill_rect(fx + 12, fy + 10, fx + 15, fy + 13, GOLD)
    # Russia flag: white / blue / red horizontal
    fx = x + 104
    c.fill_rect(fx, fy, fx + 34, fy + 9, PAPER)
    c.fill_rect(fx, fy + 9, fx + 34, fy + 18, BLUE)
    c.fill_rect(fx, fy + 18, fx + 34, fy + 27, RED)
    c.rect(fx, fy, fx + 34, fy + 27, INK, 1)
    c.rect(x + 20, fy, x + 54, fy + 28, INK, 1)
    # table
    c.hline(x + 6, x + 150, y + 54, INK, 3)
    c.vline(x + 16, y + 54, y + 64, INK, 3)
    c.vline(x + 140, y + 54, y + 64, INK, 3)


def icon_scales(c, x, y):
    """Scales of justice (ICJ)."""
    c.vline(x + 76, y + 6, y + 56, INK, 3)
    c.hline(x + 34, x + 118, y + 10, INK, 3)
    c.circle(x + 76, y + 6, 4, INK, fill=True)
    for px in (x + 38, x + 114):
        c.line(px, y + 10, px - 14, y + 34, INK, 2)
        c.line(px, y + 10, px + 14, y + 34, INK, 2)
        c.line(px - 14, y + 34, px + 14, y + 34, INK, 2)
    c.hline(x + 56, x + 96, y + 56, INK, 3)
    c.hline(x + 48, x + 104, y + 60, INK, 3)


def icon_bridge(c, x, y):
    """A bridge arch over water, one span broken (Crimean Bridge)."""
    # deck, broken in the middle
    c.hline(x + 4, x + 66, y + 30, INK, 4)
    c.hline(x + 92, x + 150, y + 30, INK, 4)
    # fallen span pieces
    c.line(x + 66, y + 30, x + 78, y + 46, INK, 3)
    c.line(x + 92, y + 30, x + 82, y + 46, INK, 3)
    # arch
    for t in range(0, 181, 4):
        a = math.radians(t)
        px = int(x + 76 + 70 * math.cos(a))
        py = int(y + 30 - 26 * math.sin(a))
        c.fill_rect(px - 1, py - 1, px + 2, py + 2, INK)
    # pillars
    c.vline(x + 14, y + 30, y + 44, INK, 3)
    c.vline(x + 138, y + 30, y + 44, INK, 3)
    # water
    for wx in range(x + 4, x + 150, 14):
        c.line(wx, y + 52, wx + 8, y + 52, BLUE, 2)
        c.line(wx + 4, y + 58, wx + 12, y + 58, BLUE, 2)


def icon_tank(c, x, y):
    """A tank halted at a ceasefire line (Gaza)."""
    # ceasefire line
    c.vline(x + 118, y + 2, y + 62, RED, 3)
    for yy in range(y + 2, y + 62, 10):
        c.fill_rect(x + 112, yy, x + 124, yy + 5, RED)
    # tank body + turret + barrel, stopped short of the line
    c.fill_rect(x + 12, y + 30, x + 92, y + 48, INK)
    c.fill_rect(x + 30, y + 18, x + 66, y + 30, INK)
    c.hline(x + 66, x + 104, y + 22, INK, 4)
    for wx in (x + 20, x + 38, x + 56, x + 74):
        c.circle(wx, y + 52, 6, INK, fill=True)
        c.circle(wx, y + 52, 2, PAPER, fill=True)
    # ground
    c.hline(x + 4, x + 150, y + 60, INK, 2)


def icon_cyclone(c, x, y):
    """A cyclone spiral over the coast (Akvan)."""
    cx, cy = x + 76, y + 32
    for r, col in ((26, BLUE), (19, BLUE), (12, BLUE)):
        c.circle(cx, cy, r, col)
    c.circle(cx, cy, 5, RED, fill=True)
    # spiral arms
    for a0 in (20, 140, 260):
        pts = []
        for t in range(0, 121, 10):
            a = math.radians(a0 + t)
            rr = 6 + t * 0.16
            pts.append((int(cx + rr * math.cos(a)),
                        int(cy + rr * math.sin(a))))
        for (px, py), (qx, qy) in zip(pts, pts[1:]):
            c.line(px, py, qx, qy, BLUE, 2)
    # coast + houses
    c.hline(x + 4, x + 150, y + 58, INK, 2)
    for hx in (x + 14, x + 34):
        c.fill_rect(hx, y + 46, hx + 12, y + 58, INK)
        c.line(hx, y + 46, hx + 6, y + 40, INK, 2)
        c.line(hx + 12, y + 46, hx + 6, y + 40, INK, 2)


def icon_chart(c, x, y):
    """A rising stock chart with an arrow (Anthropic IPO)."""
    # axes
    c.vline(x + 12, y + 6, y + 58, INK, 2)
    c.hline(x + 12, x + 148, y + 58, INK, 2)
    # rising line
    pts = [(x + 16, y + 48), (x + 44, y + 42), (x + 62, y + 46),
           (x + 88, y + 30), (x + 106, y + 34), (x + 134, y + 12)]
    for (px, py), (qx, qy) in zip(pts, pts[1:]):
        c.line(px, py, qx, qy, GREEN, 4)
    # arrowhead
    ex, ey = pts[-1]
    c.line(ex, ey, ex - 12, ey + 2, GREEN, 4)
    c.line(ex, ey, ex - 2, ey + 12, GREEN, 4)
    # dollar sign, drawn big
    c.draw_text("$", x + 116, y + 34, 3, GOLD)


def icon_globe(c, x, y):
    """A globe with a leaf (COP31 climate)."""
    cx, cy = x + 66, y + 30
    c.circle(cx, cy, 24, BLUE)
    c.circle(cx, cy, 24, BLUE)  # thicker outline
    for dy in (-12, 0, 12):
        c.hline(cx - 20, cx + 20, cy + dy, BLUE, 1)
    c.vline(cx, cy - 24, cy + 24, BLUE, 1)
    # leaf sprouting from the top
    c.line(cx, cy - 24, cx + 14, cy - 38, GREEN, 3)
    c.line(cx + 14, cy - 38, cx + 26, cy - 34, GREEN, 3)
    c.line(cx + 14, cy - 38, cx + 20, cy - 46, GREEN, 3)
    c.line(cx + 14, cy - 38, cx + 4, cy - 48, GREEN, 3)
    # sun
    c.circle(x + 132, y + 12, 7, GOLD, fill=True)

ICONS = {
    "summit": icon_summit,
    "scales": icon_scales,
    "bridge": icon_bridge,
    "tank": icon_tank,
    "cyclone": icon_cyclone,
    "chart": icon_chart,
    "globe": icon_globe,
}

# ---------------------------------------------------------------- layout

def blit_scaled(dst, src, dx, dy, scale):
    """Draw src canvas onto dst, nearest-neighbour scaled by `scale`."""
    dw = int(src.w * scale)
    dh = int(src.h * scale)
    for y in range(dh):
        sy = min(src.h - 1, int(y / scale))
        for x in range(dw):
            sx = min(src.w - 1, int(x / scale))
            i = (sy * src.w + sx) * 3
            dst.set(dx + x, dy + y, tuple(src.px[i:i + 3]))


def draw_icon(c, name, x, y, scale):
    """Render one icon into a small canvas and blit it scaled."""
    tmp = Canvas(156, 68, PAPER)
    ICONS[name](tmp, 0, 0)
    blit_scaled(c, tmp, x, y, scale)


def story_block(c, x, y, width, kicker, headline, deck, icon=None,
                head_scale=3, deck_scale=2, max_head=3, max_deck=2):
    """One story: red kicker, bold headline, deck. Returns y below block.

    The icon sits at the top right, so the first headline line is wrapped
    narrower to clear it; later lines use the full width.
    """
    c.draw_text(kicker, x, y, 2, RED)
    y += 22
    first_w = width - 122 if icon is not None else width
    if icon is not None:
        draw_icon(c, icon, x + width - 112, y - 18, 0.72)
    words = headline.upper().split()
    lines, cur, limit = [], "", first_w
    for word in words:
        trial = (cur + " " + word).strip()
        if c.text_width(trial, head_scale) <= limit:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
            limit = width
    if cur:
        lines.append(cur)
    for line in lines[:max_head]:
        c.draw_text(line, x, y, head_scale, INK)
        y += head_scale * 7 + 6
    y += 2
    for line in c.wrap(deck, deck_scale, width)[:max_deck]:
        c.draw_text(line, x, y, deck_scale, INK)
        y += deck_scale * 7 + 6
    return y


def main():
    c = Canvas(W, H, PAPER)

    # Outer frame.
    c.rect(14, 14, W - 14, H - 14, INK, 3)
    c.rect(22, 22, W - 22, H - 22, INK, 1)

    # Masthead.
    c.draw_text_centred("THE WORLD TODAY", W // 2, 40, 8, INK)
    c.hline(40, W - 40, 116, INK, 2)
    c.hline(40, W - 40, 122, INK, 1)

    # Date band: black bar, white text - the day this page sums up.
    c.fill_rect(40, 134, W - 40, 188, INK)
    c.draw_text_centred("THURSDAY, 19 NOVEMBER 2026", W // 2, 148, 4, PAPER)
    c.draw_text_centred("SEVEN STORIES  -  ONE DAY  -  REPORTED AROUND "
                        "THE WORLD", W // 2, 198, 2, GREY)

    # Lead story: Trump, Xi and Putin in Shenzhen.
    y = 226
    c.draw_text("ASIA-PACIFIC  -  DIPLOMACY", 40, y, 2, RED)
    y += 24
    draw_icon(c, "summit", 828, y - 6, 1.0)
    for line in c.wrap("TRUMP, XI AND PUTIN HOLD FIRST THREE-WAY "
                       "SUMMIT IN SHENZHEN", 4, 764)[:2]:
        c.draw_text(line, 40, y, 4, INK)
        y += 4 * 7 + 6
    y += 4
    for line in c.wrap("NINETY MINUTES ON NUCLEAR RISKS, UKRAINE AND "
                       "IRAN; A JOINT DECLARATION PLEDGES MORE TALKS, "
                       "BUT NO BREAKTHROUGH.", 2, 764)[:2]:
        c.draw_text(line, 40, y, 2, INK)
        y += 2 * 7 + 6
    y += 10
    c.hline(40, W - 40, y, INK, 2)

    # Six more stories in a 2 x 3 grid.
    stories = [
        ("INTERNATIONAL LAW", "scales",
         "UN COURT: MYANMAR COMMITTED GENOCIDE",
         "First time the court finds a state guilty of genocide; "
         "9-6 vote."),
        ("EUROPE  -  WAR", "bridge",
         "UKRAINE HITS CRIMEAN BRIDGE RAIL LINE",
         "Third strike in a week; trains halted as Neptune "
         "missiles hit the rail."),
        ("MIDDLE EAST", "tank",
         "ISRAEL ENDS GAZA GROUND RAID",
         "Army says the raid is over; Hamas called it a breach "
         "of the truce."),
        ("SOUTH ASIA  -  WEATHER", "cyclone",
         "CYCLONE AKVAN: 80,000 EVACUATED IN ODISHA",
         "Odisha moves 80,000 to safety as the storm nears "
         "landfall on Friday."),
        ("BUSINESS  -  TECHNOLOGY", "chart",
         "ANTHROPIC DEBUTS IN RECORD $81BN IPO",
         "Shares start trading on Nasdaq at $83; the sale tops "
         "SpaceX's record."),
        ("CLIMATE  -  COP31", "globe",
         "COP31 DRAFT DROPS FOSSIL-FUEL WORDING",
         "New draft drops every fossil-fuel mention; talks run "
         "to Friday."),
    ]
    col_w = (W - 2 * 40 - 28) // 2
    row_y = y + 18
    for i, (kicker, icon, head, deck) in enumerate(stories):
        cx = 40 + (i % 2) * (col_w + 28)
        cy = row_y + (i // 2) * 168
        if i % 2 == 1:
            c.vline(40 + col_w + 14, cy + 4, cy + 148, GREY, 1)
        story_block(c, cx, cy, col_w, kicker, head, deck, icon=icon)

    # Footer.
    fy = H - 64
    c.hline(40, W - 40, fy, INK, 1)
    c.draw_text_centred("ALL STORIES FIRST REPORTED THURSDAY "
                        "19 NOVEMBER 2026.", W // 2, fy + 12, 2, GREY)

    out = "news-19-nov-2026.png"
    n = save_png(c, out)
    print(out, (W, H), "bytes:", n)


if __name__ == "__main__":
    main()
