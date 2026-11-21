#!/usr/bin/env python3
"""Draws Pixel Paint's built-in, original line-art scenes and converts
each into a puzzle with tool/make_puzzle.py.

  python3 tool/art/scenes.py            # all scenes
  python3 tool/art/scenes.py koi rose   # just these

Each scene is plain code (seeded, so the output is reproducible).
"""
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from shapes import Canvas, blob_pts, ellipse_pts, leaf_halves, petal_pts, ridge, shade, wave_band  # noqa: E402

OUT = os.path.join(HERE, 'out')

# ---------------------------------------------------------------- palettes
ROSE = (232, 76, 120)
CORAL = (247, 129, 98)
PEACH = (255, 183, 140)
BUTTER = (255, 214, 92)
GOLD = (245, 166, 35)
LEAF = (76, 160, 82)
LEAF_D = (38, 112, 70)
MINT = (152, 214, 160)
SKY = (140, 200, 240)
SKY_L = (200, 232, 250)
TEAL = (44, 170, 170)
NAVY = (40, 62, 120)
LILAC = (176, 132, 222)
VIOLET = (120, 80, 190)
PINK = (255, 170, 200)
CREAM = (255, 244, 222)
WHITE = (255, 255, 255)
BROWN = (140, 90, 60)
RED = (220, 50, 60)


# ------------------------------------------------------------------ pieces
def rose(c, cx, cy, r, base, rot=0.0):
    """Layered rose: shrinking, rotating circles leave crescent petals."""
    dark, mid, light = shade(base, -0.25), base, shade(base, 0.35)
    for k in range(6):
        a = rot + k * 2 * math.pi / 6
        c.poly(petal_pts(cx, cy, a, r * 1.05, r * 0.55, base=r * 0.2), dark if k % 2 else mid)
    rr = r * 0.82
    ang = rot
    i = 0
    while rr > r * 0.16:
        off = rr * 0.16
        c.circle(cx + off * math.cos(ang), cy + off * math.sin(ang), rr, [light, mid, dark][i % 3])
        rr *= 0.76
        ang += 2.1
        i += 1


def daisy(c, cx, cy, r, petal, center, n=12, rot=0.0):
    for k in range(n):
        a = rot + k * 2 * math.pi / n
        c.poly(petal_pts(cx, cy, a, r, r * 0.22, base=r * 0.25), petal if k % 2 == 0 else shade(petal, -0.08))
    c.circle(cx, cy, r * 0.32, center)
    c.circle(cx, cy, r * 0.16, shade(center, -0.25))


def tulip(c, x, y, h, color, stem=LEAF):
    c.poly([(x - 4, y), (x + 4, y), (x + 4, y + h), (x - 4, y + h)], stem)
    w = h * 0.22
    top = y - w * 1.4
    c.poly([(x - w, y - w * 0.2), (x - w * 1.05, top), (x - w * 0.4, top + w * 0.5), (x, top - w * 0.1),
            (x + w * 0.4, top + w * 0.5), (x + w * 1.05, top), (x + w, y - w * 0.2), (x, y + w * 0.35)], color)
    c.poly([(x - w * 0.45, y - w * 0.1), (x, top + w * 0.35), (x + w * 0.45, y - w * 0.1), (x, y + w * 0.25)], shade(color, 0.3))


def leaf(c, bx, by, tx, ty, width, light=LEAF, dark=LEAF_D, curl=0.0):
    left, right = leaf_halves(bx, by, tx, ty, width, curl=curl)
    c.poly(left, light)
    c.poly(right, dark)


def butterfly(c, cx, cy, s, wing, accent, rot=0.0):
    for sign in (1, -1):
        for upper in (True, False):
            a = (-0.8 if upper else 0.55) if sign > 0 else (math.pi + 0.8 if upper else math.pi - 0.55)
            ln = s * (1.0 if upper else 0.72)
            c.poly(petal_pts(cx, cy, a + rot, ln, ln * 0.5), wing)
            c.poly(petal_pts(cx, cy, a + rot, ln * 0.62, ln * 0.3), accent)
            dx, dy = math.cos(a + rot), math.sin(a + rot)
            c.circle(cx + dx * ln * 0.8, cy + dy * ln * 0.8, ln * 0.09, WHITE)
    c.ellipse(cx, cy, s * 0.08, s * 0.38, BROWN, angle=rot)
    for side in (-1, 1):
        c.line([(cx, cy - s * 0.3), (cx + side * s * 0.22, cy - s * 0.62)], width=3)


def cloud(c, cx, cy, s, color=WHITE):
    for dx, dy, r in ((-0.55, 0.1, 0.38), (0.55, 0.12, 0.36), (-0.15, -0.15, 0.5), (0.25, -0.05, 0.45)):
        c.circle(cx + dx * s, cy + dy * s, r * s, color if r > 0.4 else shade(color, -0.06))
    c.poly([(cx - 0.9 * s, cy + 0.2 * s), (cx + 0.9 * s, cy + 0.2 * s), (cx + 0.9 * s, cy + 0.42 * s), (cx - 0.9 * s, cy + 0.42 * s)], color)


# ------------------------------------------------------------------ scenes
def scene_bouquet(c):
    rng = c.rng
    W, H = c.w, c.h
    # background: soft bands
    for i, col in enumerate([(255, 236, 214), (255, 222, 230), (232, 222, 255), (214, 238, 250)]):
        c.poly(wave_band(W, -40 + i * 260, 35, 1.1, i * 1.7, H + 10), col)
    # vase
    vx, vy = W / 2, 760
    vase = [(vx - 120, vy), (vx + 120, vy), (vx + 150, vy + 120), (vx + 120, H + 10), (vx - 120, H + 10), (vx - 150, vy + 120)]
    c.poly(vase, (90, 190, 200))
    for k in range(-3, 4):
        c.poly([(vx + k * 40 - 12, vy), (vx + k * 40 + 12, vy), (vx + k * 46 + 14, H + 10), (vx + k * 46 - 14, H + 10)], (60, 160, 180) if k % 2 else (150, 220, 225))
    c.poly([(vx - 130, vy - 20), (vx + 130, vy - 20), (vx + 120, vy + 18), (vx - 120, vy + 18)], (60, 150, 170))
    # leaves fan
    for a in range(-80, 81, 16):
        ang = math.radians(a - 90)
        L = rng.uniform(260, 360)
        leaf(c, vx, vy - 10, vx + L * math.cos(ang), vy - 10 + L * math.sin(ang), 34, curl=rng.uniform(-1, 1))
    # filler berries / lilac clusters
    for _ in range(9):
        x, y = rng.uniform(140, 660), rng.uniform(170, 560)
        for k in range(7):
            c.circle(x + rng.uniform(-30, 30), y + rng.uniform(-30, 30), 13, LILAC if k % 2 else VIOLET)
    # daisies and tulips behind
    for x, y in ((150, 380), (650, 350), (260, 180), (560, 190)):
        daisy(c, x, y, 62, WHITE if x < 400 else BUTTER, GOLD, rot=rng.uniform(0, 1))
    tulip(c, 120, 560, 120, CORAL)
    tulip(c, 690, 540, 120, PINK)
    # roses in front
    rose(c, 300, 470, 110, ROSE, rot=0.3)
    rose(c, 520, 430, 100, CORAL, rot=1.2)
    rose(c, 420, 620, 92, PINK, rot=2.0)
    rose(c, 600, 640, 70, ROSE, rot=0.8)
    rose(c, 210, 650, 72, PEACH, rot=2.4)
    for x, y in ((160, 750), (650, 760)):
        leaf(c, x, y, x + (60 if x < 400 else -60), y - 80, 26)
    butterfly(c, 640, 120, 70, SKY, NAVY, rot=0.3)
    butterfly(c, 140, 120, 55, BUTTER, GOLD, rot=-0.3)


def scene_sunset(c):
    rng = c.rng
    W, H = c.w, c.h
    sky = [(255, 228, 160), (255, 196, 140), (250, 160, 130), (226, 120, 140), (160, 100, 160)]
    for i, col in enumerate(reversed(sky)):
        c.poly(wave_band(W, -30 + i * 95, 18, 0.8, i, H + 10), col)
    c.circle(W / 2, 470, 120, (255, 236, 170))
    c.circle(W / 2, 470, 86, (255, 246, 205))
    cloud(c, 170, 170, 70, (255, 214, 214))
    cloud(c, 610, 250, 60, (255, 222, 200))
    for idx, (base, col, peaks) in enumerate([
        (560, (140, 80, 130), [(80, 180), (260, 260), (420, 170), (560, 300), (760, 200)]),
        (600, (110, 60, 110), [(0, 120), (190, 200), (380, 110), (620, 230), (800, 150)]),
        (640, (80, 50, 90), [(120, 110), (300, 60), (520, 140), (700, 90)]),
    ]):
        pts = ridge(W, base + 10, peaks, rng)
        c.poly(pts + [(W + 5, H), (-5, H)], col)
        for x, hgt in peaks:  # sunlit facet
            c.poly([(x, base - hgt + 10), (x + hgt * 0.45, base + 10), (x + hgt * 0.1, base + 10)], shade(col, 0.25))
    # lake
    c.poly([(-5, 650), (W + 5, 650), (W + 5, H + 5), (-5, H + 5)], (110, 140, 200))
    for i in range(7):
        y = 670 + i * 32
        w = 260 - i * 26
        c.poly([(W / 2 - w, y), (W / 2 + w, y), (W / 2 + w - 20, y + 12), (W / 2 - w + 20, y + 12)], (255, 220, 160) if i % 2 == 0 else (240, 180, 150))
        c.poly(wave_band(W, y + 18, 4, 3, i, y + 26, steps=40), (90, 120, 185))
    # pines on both sides
    for side in (0, 1):
        for k in range(4):
            x = (40 + k * 55) if side == 0 else (W - 40 - k * 55)
            base = 760 + k * 40
            hgt = 260 - k * 30
            for t in range(4):
                tw = 70 - t * 14
                ty = base - t * hgt / 5
                c.poly([(x - tw, ty), (x + tw, ty), (x, ty - hgt / 3)], (40, 90, 80) if t % 2 else (30, 70, 70))
            c.poly([(x - 8, base), (x + 8, base), (x + 8, base + 40), (x - 8, base + 40)], (70, 45, 50))
    # foreground meadow with flowers
    c.poly(wave_band(W, 900, 14, 1.4, 0.5, H + 10), (70, 130, 80))
    for x in range(60, W, 90):
        daisy(c, x + rng.uniform(-15, 15), 930 + rng.uniform(-10, 15), 26, (255, 200, 210) if x % 180 else WHITE, GOLD, n=8)
    for x, y in ((300, 200), (360, 240), (470, 180)):  # birds
        c.poly([(x - 30, y), (x - 10, y - 8), (x, y + 2), (x + 10, y - 8), (x + 30, y), (x, y + 10)], (70, 50, 70))


def scene_koi(c):
    rng = c.rng
    W, H = c.w, c.h
    c.poly([(0, 0), (W, 0), (W, H), (0, H)], (40, 140, 160))
    # ripple rings
    for cx, cy in ((200, 260), (600, 700), (560, 180)):
        for k, r in enumerate((230, 180, 130, 80)):
            c.circle(cx, cy, r, (60, 165, 180) if k % 2 == 0 else (40, 140, 160))
    # lily pads
    for cx, cy, r in ((120, 820, 95), (680, 420, 85), (330, 560, 70), (700, 900, 70), (90, 130, 70)):
        notch = rng.uniform(0, 6.28)
        pts = [(cx, cy)] + [(cx + r * math.cos(notch + 0.35 + t / 30 * (2 * math.pi - 0.7)), cy + r * math.sin(notch + 0.35 + t / 30 * (2 * math.pi - 0.7))) for t in range(31)]
        c.poly(pts, MINT)
        for v in range(5):
            a = notch + 0.9 + v * 1.1
            c.line([(cx, cy), (cx + r * 0.85 * math.cos(a), cy + r * 0.85 * math.sin(a))], width=3)
    # koi
    def koi(x, y, ang, L, body, spot):
        ca, sa = math.cos(ang), math.sin(ang)

        def P(a, b):
            return (x + a * ca - b * sa, y + a * sa + b * ca)
        tail = [P(-L * 0.45, 0), P(-L * 0.8, -L * 0.22), P(-L * 0.68, 0), P(-L * 0.8, L * 0.22)]
        c.poly(tail, shade(body, 0.2))
        for s in (-1, 1):
            c.poly([P(L * 0.12, s * L * 0.1), P(-L * 0.05, s * L * 0.3), P(-L * 0.08, s * L * 0.12)], shade(body, 0.2))
        c.poly([P(L * 0.5 * math.cos(t), L * 0.15 * math.sin(t) * (1 - 0.35 * (math.cos(t) < 0))) for t in [i / 30 * 2 * math.pi for i in range(30)]], body)
        for sx, sy, sr in ((0.15, 0.03, 0.07), (-0.12, -0.04, 0.06), (0.32, -0.02, 0.05)):
            c.circle(*P(L * sx, L * sy), L * sr, spot)
        c.circle(*P(L * 0.4, L * 0.06), 5, (30, 30, 40), width=1)
    koi(330, 300, 0.4, 230, (250, 120, 50), WHITE)
    koi(520, 560, 3.6, 210, WHITE, (230, 70, 50))
    koi(220, 760, -0.6, 190, (255, 190, 60), (230, 90, 40))
    # lotus
    for cx, cy, s in ((600, 380, 55), (150, 800, 45)):
        for k in range(8):
            c.poly(petal_pts(cx, cy, k * math.pi / 4, s * 1.4, s * 0.45), PINK if k % 2 else (255, 140, 180))
        for k in range(5):
            c.poly(petal_pts(cx, cy, k * 2 * math.pi / 5 + 0.3, s * 0.9, s * 0.35), (255, 205, 220))
        c.circle(cx, cy, s * 0.28, BUTTER)


def scene_mandala(c):
    W, H = c.w, c.h
    cx, cy = W / 2, H / 2
    c.poly([(0, 0), (W, 0), (W, H), (0, H)], (40, 50, 100))
    for k, r in enumerate((620, 560)):
        c.circle(cx, cy, r, (60, 70, 130) if k % 2 == 0 else (40, 50, 100))
    rings = [
        (24, 380, 70, (0.25, (90, 200, 200), (50, 150, 170))),
        (16, 320, 80, (0.0, (255, 170, 80), (245, 120, 70))),
        (16, 250, 70, (0.2, (240, 100, 140), (255, 160, 190))),
        (12, 190, 70, (0.0, (160, 120, 220), (200, 170, 245))),
        (12, 135, 60, (0.26, (255, 214, 92), (255, 240, 170))),
        (8, 85, 55, (0.0, (90, 200, 160), (170, 235, 200))),
    ]
    for n, length, width, (rot, a, b) in rings:
        for k in range(n):
            ang = rot + k * 2 * math.pi / n
            c.poly(petal_pts(cx, cy, ang, length, width * 0.5 * (16 / n) ** 0.4, base=length * 0.35), a if k % 2 == 0 else b)
            if length > 200:
                c.poly(petal_pts(cx, cy, ang, length * 0.86, width * 0.22 * (16 / n) ** 0.4, base=length * 0.55), shade(a if k % 2 == 0 else b, -0.2))
    c.circle(cx, cy, 45, (255, 120, 90))
    c.circle(cx, cy, 24, (255, 214, 92))
    for k in range(24):  # dots ring
        a = k * 2 * math.pi / 24
        c.circle(cx + 410 * math.cos(a), cy + 410 * math.sin(a), 11, (255, 240, 170))
    for x, y in ((60, 60), (W - 60, 60), (60, H - 60), (W - 60, H - 60)):
        for k in range(6):
            c.poly(petal_pts(x, y, k * math.pi / 3, 55, 18), (255, 170, 80) if k % 2 else (240, 100, 140))
        c.circle(x, y, 14, (255, 214, 92))


def scene_balloons(c):
    rng = c.rng
    W, H = c.w, c.h
    for i, col in enumerate([(150, 205, 245), (175, 220, 250), (200, 232, 252), (225, 242, 255)]):
        c.poly(wave_band(W, -30 + i * 150, 12, 0.7, i, H + 10), col)
    for x, y, s in ((140, 120, 60), (620, 90, 70), (420, 300, 50), (700, 420, 45)):
        cloud(c, x, y, s)
    # hills patchwork
    for i, col in enumerate([(120, 190, 110), (90, 170, 100), (150, 205, 120)]):
        c.poly(wave_band(W, 720 + i * 70, 40, 0.6 + i * 0.3, i * 2, H + 10), col)
    for k in range(9):
        x = k * 100 + rng.uniform(-20, 20)
        c.poly([(x, 800 + (k % 3) * 40), (x + 90, 790 + (k % 2) * 50), (x + 110, H + 10), (x - 10, H + 10)],
               [(240, 210, 110), (200, 225, 120), (110, 175, 95), (230, 180, 120)][k % 4])

    def balloon(cx, cy, r, colors):
        gores = 8
        top = cy - r
        for g in range(gores):
            a0 = math.pi + g * math.pi / gores
            a1 = math.pi + (g + 1) * math.pi / gores
            pts = []
            for t in range(13):
                y = top + t / 12 * r * 1.75
                yy = (y - cy) / r
                wfac = math.sqrt(max(0.0, 1 - yy * yy)) if yy < 0.35 else max(0.18, 0.94 - (yy - 0.35) * 1.6)
                pts.append((cx + r * wfac * math.cos(a0), y))
            for t in range(12, -1, -1):
                y = top + t / 12 * r * 1.75
                yy = (y - cy) / r
                wfac = math.sqrt(max(0.0, 1 - yy * yy)) if yy < 0.35 else max(0.18, 0.94 - (yy - 0.35) * 1.6)
                pts.append((cx + r * wfac * math.cos(a1), y))
            c.poly(pts, colors[g % len(colors)])
        by = top + r * 1.75
        for s in (-1, 1):
            c.line([(cx + s * r * 0.18, by), (cx + s * r * 0.14, by + r * 0.45)], width=2)
        c.poly([(cx - r * 0.16, by + r * 0.45), (cx + r * 0.16, by + r * 0.45), (cx + r * 0.13, by + r * 0.68), (cx - r * 0.13, by + r * 0.68)], BROWN)
    balloon(250, 330, 140, [(232, 76, 90), (255, 214, 92), (232, 76, 90), (255, 244, 222)])
    balloon(560, 520, 110, [(110, 90, 200), (90, 200, 200), (255, 170, 80)])
    balloon(640, 200, 70, [(90, 180, 120), (255, 244, 222)])
    balloon(120, 620, 60, [(255, 140, 180), (176, 132, 222)])


def scene_hummingbird(c):
    rng = c.rng
    W, H = c.w, c.h
    c.poly([(0, 0), (W, 0), (W, H), (0, H)], (230, 245, 230))
    for _ in range(14):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        c.poly(blob_pts(x, y, rng.uniform(60, 120), rng), (205, 232, 210) if rng.random() < 0.5 else (240, 250, 225))
    # big leaves
    for _ in range(14):
        bx, by = rng.choice([(0, rng.uniform(0, H)), (W, rng.uniform(0, H)), (rng.uniform(0, W), H)])
        tx = bx + (240 if bx == 0 else -240 if bx == W else rng.uniform(-150, 150))
        ty = by - rng.uniform(60, 260)
        leaf(c, bx, by, tx, ty, 55, LEAF, LEAF_D, curl=rng.uniform(-1, 1))

    def hibiscus(cx, cy, r, col, rot):
        for k in range(5):
            a = rot + k * 2 * math.pi / 5
            c.poly(blob_pts(cx + r * 0.55 * math.cos(a), cy + r * 0.55 * math.sin(a), r * 0.55, rng, 0.08, lobes=4), col if k % 2 else shade(col, 0.15))
        for k in range(5):
            a = rot + 0.6 + k * 2 * math.pi / 5
            c.poly(petal_pts(cx, cy, a, r * 0.45, r * 0.12), shade(col, -0.3))
        c.poly(petal_pts(cx, cy, rot - 0.9, r * 1.1, 8), GOLD)
        c.circle(cx + r * 1.05 * math.cos(rot - 0.9), cy + r * 1.05 * math.sin(rot - 0.9), 12, BUTTER)
    hibiscus(560, 700, 150, (235, 70, 100), 0.4)
    hibiscus(180, 260, 110, (255, 140, 90), 2.0)
    hibiscus(660, 220, 80, (255, 120, 170), 1.0)
    # hummingbird
    bx, by = 360, 470
    for k in range(7):  # far wing
        c.poly(petal_pts(bx + 10, by - 30, -2.0 + k * 0.12, 210 - k * 18, 20), (90, 170, 200) if k % 2 else (130, 210, 220))
    c.poly(petal_pts(bx - 40, by + 40, 2.2, 150, 34), (40, 110, 110))  # tail
    c.poly(petal_pts(bx - 40, by + 40, 2.5, 140, 26), (60, 150, 140))
    c.ellipse(bx, by, 95, 52, (60, 170, 140), angle=-0.5)
    c.poly(petal_pts(bx - 10, by + 10, -0.5, 90, 30), (210, 240, 220))  # belly
    c.circle(bx + 85, by - 55, 45, (50, 150, 130))
    c.poly(petal_pts(bx + 60, by - 30, 0.2, 60, 20), (230, 50, 90))  # throat
    c.poly([(bx + 122, by - 62), (bx + 245, by - 30), (bx + 122, by - 48)], (40, 40, 50))
    c.circle(bx + 100, by - 65, 9, (30, 30, 40), width=2)
    for k in range(8):  # near wing
        c.poly(petal_pts(bx - 5, by - 20, -1.6 - k * 0.11, 250 - k * 20, 22), (110, 200, 220) if k % 2 else (170, 230, 235))


def star_pts(cx, cy, r, n=5, inner=0.45, rot=-math.pi / 2):
    out = []
    for i in range(n * 2):
        rr = r if i % 2 == 0 else r * inner
        a = rot + i * math.pi / n
        out.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return out


def grass_row(c, y, color, n=18, h=70, w=30, base=None):
    """A row of grass blades standing on y."""
    base = base if base is not None else c.h + 10
    xs = [c.w * i / n for i in range(n + 1)]
    pts = [(-5, base), (-5, y)]
    for i in range(n):
        x0, x1 = xs[i], xs[i + 1]
        pts += [(x0 + (x1 - x0) * 0.15, y), ((x0 + x1) / 2 + c.rng.uniform(-8, 8), y - h * c.rng.uniform(0.7, 1.1)), (x0 + (x1 - x0) * 0.85, y)]
    pts += [(c.w + 5, y), (c.w + 5, base)]
    c.poly(pts, color)


def scene_sunflower(c):
    rng = c.rng
    W, H = c.w, c.h
    for i, col in enumerate([(200, 232, 250), (222, 240, 252), (255, 244, 214)]):
        c.poly(wave_band(W, -40 + i * 300, 25, 1.0, i * 1.3, H + 10), col)
    c.circle(120, 130, 70, (255, 224, 120))
    cloud(c, 600, 120, 85)
    c.poly(wave_band(W, 720, 40, 0.9, 0.4, H + 10), (130, 196, 110))
    c.poly(wave_band(W, 820, 30, 1.2, 2.0, H + 10), LEAF)
    # stems and leaves
    c.poly([(392, 470), (408, 470), (412, 900), (388, 900)], LEAF_D)
    leaf(c, 400, 760, 190, 640, 60, curl=0.6)
    leaf(c, 400, 700, 620, 580, 60, curl=-0.6)

    def sunflower(x, y, r, petal_a, petal_b, rot=0.0):
        n = 20
        for k in range(n):
            a = rot + k * 2 * math.pi / n
            c.poly(petal_pts(x, y, a, r * 1.55, r * 0.2, base=r * 0.55), petal_a if k % 2 == 0 else petal_b)
        for k in range(n):
            a = rot + (k + 0.5) * 2 * math.pi / n
            c.poly(petal_pts(x, y, a, r * 1.3, r * 0.17, base=r * 0.5), shade(petal_a, 0.15) if k % 2 == 0 else shade(petal_b, 0.15))
        c.circle(x, y, r * 0.78, (120, 74, 40))
        c.circle(x, y, r * 0.56, (150, 96, 52))
        c.circle(x, y, r * 0.34, (96, 58, 34))
        for k in range(8):
            a = rot + k * math.pi / 4
            c.circle(x + r * 0.67 * math.cos(a), y + r * 0.67 * math.sin(a), r * 0.07, (200, 140, 80), width=2)
    sunflower(400, 380, 120, GOLD, BUTTER, 0.1)
    sunflower(160, 690, 65, BUTTER, GOLD, 0.4)
    sunflower(650, 660, 70, GOLD, BUTTER, 0.8)
    for x in (160, 650):
        c.poly([(x - 5, 740 if x < 400 else 735), (x + 5, 740 if x < 400 else 735), (x + 6, 900), (x - 6, 900)], LEAF_D)
    # bee
    bx, by = 560, 300
    for sx in (-1, 1):
        c.ellipse(bx + sx * 22, by - 28, 24, 14, SKY_L, angle=sx * 0.8)
    c.ellipse(bx, by, 40, 26, BUTTER, angle=-0.3)
    for k in (-14, 4, 22):
        c.poly([(bx + k, by - 24), (bx + k + 9, by - 22), (bx + k + 9, by + 22), (bx + k, by + 24)], (60, 50, 50))
    c.circle(bx + 42, by + 4, 12, (60, 50, 50))
    c.circle(bx + 46, by + 1, 3, WHITE, width=1)


def scene_owl(c):
    rng = c.rng
    W, H = c.w, c.h
    c.poly([(0, 0), (W, 0), (W, H), (0, H)], (66, 78, 158))
    c.poly(wave_band(W, 420, 30, 0.8, 0.3, H + 10), (84, 98, 176))
    c.circle(630, 190, 105, (255, 240, 190))
    c.circle(600, 170, 22, (240, 220, 160), width=2)
    c.circle(665, 225, 16, (240, 220, 160), width=2)
    for x, y, r in ((130, 120, 26), (300, 70, 20), (90, 300, 18), (470, 150, 22), (250, 250, 16), (740, 380, 20)):
        c.poly(star_pts(x, y, r), BUTTER)
    # branch
    c.poly([(-10, 780), (810, 740), (810, 800), (-10, 850)], (120, 80, 56))
    c.poly([(560, 770), (700, 640), (730, 668), (610, 790)], (100, 66, 46))
    for x, y, tx, ty in ((120, 800, 40, 690), (700, 660, 770, 560), (520, 770, 470, 690)):
        leaf(c, x, y, tx, ty, 34, curl=0.4)
    # owl
    cx = 400
    c.ellipse(cx, 560, 190, 240, (160, 110, 74))                      # body
    for sx in (-1, 1):                                               # wings
        c.poly(petal_pts(cx + sx * 140, 450, math.pi / 2 + sx * 0.25, 330, 100, base=20), (120, 80, 56))
        for k in range(3):
            c.poly(petal_pts(cx + sx * (150 + k * 6), 560 + k * 40, math.pi / 2 + sx * 0.25, 200 - k * 30, 34, base=10), (150, 104, 70))
    c.ellipse(cx, 600, 120, 170, CREAM)                              # belly
    for row in range(5):
        for col in range(3 - (row % 2)):
            x = cx + (col - (1 - (row % 2) * 0.5)) * 70
            c.ellipse(x, 490 + row * 55, 32, 22, (240, 214, 170))
    for sx in (-1, 1):                                               # ear tufts
        c.poly([(cx + sx * 120, 330), (cx + sx * 175, 215), (cx + sx * 55, 300)], (120, 80, 56))
    c.circle(cx, 360, 150, (176, 124, 84))                           # head
    for sx in (-1, 1):                                               # eyes
        c.circle(cx + sx * 72, 355, 66, CREAM)
        c.circle(cx + sx * 72, 355, 44, GOLD)
        c.circle(cx + sx * 72, 355, 22, (30, 26, 40), width=2)
        c.circle(cx + sx * 72 - 8, 345, 7, WHITE, width=1)
    c.poly([(cx - 22, 392), (cx + 22, 392), (cx, 450)], (240, 140, 50))  # beak
    for sx in (-1, 1):                                               # feet
        for k in range(3):
            c.ellipse(cx + sx * 80 + (k - 1) * 22, 790, 10, 24, (240, 160, 70))


def scene_butterfly(c):
    rng = c.rng
    W, H = c.w, c.h
    for i, col in enumerate([(214, 238, 250), (232, 244, 255), (255, 244, 224)]):
        c.poly(wave_band(W, -40 + i * 280, 30, 1.0, i * 1.5, H + 10), col)
    c.circle(680, 120, 80, (255, 224, 120))
    c.poly(wave_band(W, 780, 30, 1.1, 0.6, H + 10), (140, 200, 120))
    grass_row(c, 880, LEAF, n=14, h=80)
    # flowers on stems
    for x, y, col in ((120, 650, CORAL), (680, 600, PINK), (250, 760, BUTTER), (560, 780, LILAC)):
        c.poly([(x - 5, y), (x + 5, y), (x + 5, 900), (x - 5, 900)], LEAF_D)
        leaf(c, x, y + 120, x + (60 if x < 400 else -60), y + 60, 22)
        daisy(c, x, y, 55, col, GOLD, n=10, rot=x)
    # big butterfly
    bx, by, s = 400, 400, 330
    for sign in (1, -1):
        up = math.pi * 1.22 if sign < 0 else -math.pi * 0.22
        lo = math.pi * 0.78 if sign < 0 else math.pi * 0.22
        c.poly(petal_pts(bx, by, up, s, s * 0.55), (240, 110, 150))
        c.poly(petal_pts(bx, by, up, s * 0.7, s * 0.38), (255, 170, 200))
        c.poly(petal_pts(bx, by, up, s * 0.4, s * 0.2), BUTTER)
        c.poly(petal_pts(bx, by, lo, s * 0.8, s * 0.42), (150, 110, 220))
        c.poly(petal_pts(bx, by, lo, s * 0.5, s * 0.26), (200, 170, 245))
        for k in range(3):
            c.circle(bx + math.cos(up) * s * (0.8 - k * 0.16), by + math.sin(up) * s * (0.8 - k * 0.16) * 0.9, 12, WHITE)
    c.ellipse(bx, by + 10, 22, 130, BROWN)
    c.circle(bx, by - 125, 26, BROWN)
    for sx in (-1, 1):
        c.line([(bx + sx * 6, by - 145), (bx + sx * 60, by - 230)], width=4)
        c.circle(bx + sx * 60, by - 230, 8, GOLD)
    butterfly(c, 130, 170, 70, SKY, NAVY, rot=0.3)
    butterfly(c, 650, 300, 58, BUTTER, GOLD, rot=-0.4)
    butterfly(c, 120, 440, 46, MINT, TEAL, rot=0.5)


def scene_lighthouse(c):
    rng = c.rng
    W, H = c.w, c.h
    for i, col in enumerate([(255, 214, 170), (255, 232, 190), (214, 236, 250), (180, 220, 245)]):
        c.poly(wave_band(W, -40 + i * 180, 22, 1.0, i * 1.1, H + 10), col)
    c.circle(150, 300, 75, (255, 236, 150))
    cloud(c, 620, 170, 90)
    cloud(c, 160, 110, 60, (255, 244, 240))
    # sea
    for i, col in enumerate([(70, 160, 210), (50, 140, 195), (36, 118, 180), (28, 96, 160)]):
        c.poly(wave_band(W, 640 + i * 90, 14, 3.0, i * 1.7, H + 10), col)
    # rock
    c.poly([(150, 760), (260, 650), (400, 620), (540, 650), (650, 770), (700, H), (100, H)], (120, 110, 120))
    c.poly([(260, 650), (400, 620), (440, 700), (330, 720)], (150, 140, 150))
    c.poly([(440, 700), (540, 650), (650, 770), (540, 780)], (96, 88, 100))
    # tower
    top, bot = 330, 640
    for i in range(5):
        y0 = top + (bot - top) * i / 5
        y1 = top + (bot - top) * (i + 1) / 5
        w0 = 70 + (140 - 70) * (y0 - top) / (bot - top)
        w1 = 70 + (140 - 70) * (y1 - top) / (bot - top)
        c.poly([(400 - w0, y0), (400 + w0, y0), (400 + w1, y1), (400 - w1, y1)], RED if i % 2 == 0 else WHITE)
    c.poly([(400 - 28, bot - 90), (400 + 28, bot - 90), (400 + 28, bot), (400 - 28, bot)], BROWN)       # door
    c.circle(400, bot - 90, 28, BROWN)
    for y in (430, 540):
        c.circle(400, y, 18, SKY_L)
    # gallery + lantern
    c.poly([(400 - 105, top), (400 + 105, top), (400 + 105, top - 24), (400 - 105, top - 24)], (60, 60, 70))
    c.poly([(400 - 62, top - 24), (400 + 62, top - 24), (400 + 62, top - 120), (400 - 62, top - 120)], (255, 240, 150))
    for x in (-31, 0, 31):
        c.line([(400 + x, top - 24), (400 + x, top - 120)], width=3)
    c.poly([(400 - 85, top - 120), (400 + 85, top - 120), (400, top - 215)], RED)
    c.circle(400, top - 222, 14, (60, 60, 70))
    # beams
    c.poly([(465, top - 90), (800, top - 190), (800, top + 10)], (255, 250, 200))
    c.poly([(335, top - 90), (0, top - 190), (0, top + 10)], (255, 250, 200))
    # boat
    bx, by = 600, 800
    c.poly([(bx - 80, by), (bx + 80, by), (bx + 55, by + 40), (bx - 55, by + 40)], BROWN)
    c.poly([(bx, by - 150), (bx + 70, by - 10), (bx, by - 10)], WHITE)
    c.poly([(bx - 8, by - 120), (bx - 62, by - 10), (bx - 8, by - 10)], PEACH)
    c.line([(bx, by - 160), (bx, by)], width=4)
    # gulls
    for x, y in ((240, 200), (300, 150), (520, 250)):
        c.line([(x - 26, y), (x - 10, y - 14), (x, y), (x + 10, y - 14), (x + 26, y)], width=4)


def scene_mushrooms(c):
    rng = c.rng
    W, H = c.w, c.h
    c.poly([(0, 0), (W, 0), (W, H), (0, H)], (36, 96, 90))
    c.poly(wave_band(W, 300, 40, 0.8, 0.5, H + 10), (46, 116, 100))
    for x, y in ((120, 160), (300, 90), (520, 190), (690, 110), (420, 280)):
        c.circle(x, y, 13, (255, 240, 150))
        c.circle(x, y, 5, WHITE, width=1)
    c.poly(wave_band(W, 760, 30, 1.0, 0.2, H + 10), (96, 150, 70))
    grass_row(c, 840, (60, 130, 70), n=16, h=70)

    def shroom(x, y, h, cap, spot, stem=CREAM, w=1.0):
        sw = 52 * w
        c.poly([(x - sw * 0.7, y), (x + sw * 0.7, y), (x + sw * 0.5, y - h), (x - sw * 0.5, y - h)], stem)
        c.ellipse(x, y - 6, sw * 1.15, 16, shade(stem, -0.12))
        cr = 135 * w
        c.poly(ellipse_pts(x, y - h, cr, cr * 0.72, 0, 60)[30:], cap)
        c.poly([(x - cr, y - h), (x + cr, y - h), (x + cr * 0.8, y - h + 22), (x - cr * 0.8, y - h + 22)], shade(stem, -0.05))
        for dx, dy, r in ((-0.45, -0.38, 0.17), (0.2, -0.55, 0.2), (0.55, -0.25, 0.13), (-0.1, -0.2, 0.1)):
            c.circle(x + dx * cr, y - h + dy * cr, r * cr, spot)
    shroom(260, 800, 260, RED, WHITE, w=1.25)
    shroom(580, 780, 190, (250, 160, 70), (255, 236, 190), w=0.95)
    shroom(470, 560, 130, (170, 120, 210), (235, 215, 250), w=0.7)
    shroom(110, 590, 110, (240, 120, 150), WHITE, w=0.6)
    shroom(690, 540, 90, RED, WHITE, w=0.5)
    for x, y, tx, ty in ((40, 840, 150, 700), (760, 840, 650, 690), (400, 850, 360, 740)):
        leaf(c, x, y, tx, ty, 34, curl=0.4)
    # snail
    sx, sy = 330, 870
    c.ellipse(sx + 20, sy, 70, 20, (230, 200, 160))
    c.circle(sx, sy - 22, 46, (190, 130, 90))
    c.circle(sx, sy - 22, 26, (220, 170, 120))
    c.circle(sx, sy - 22, 10, (190, 130, 90), width=2)
    c.line([(sx + 70, sy - 8), (sx + 82, sy - 40)], width=3)
    c.line([(sx + 60, sy - 8), (sx + 62, sy - 42)], width=3)


def scene_reef(c):
    rng = c.rng
    W, H = c.w, c.h
    for i, col in enumerate([(120, 210, 240), (90, 190, 235), (60, 160, 220), (40, 130, 200), (30, 100, 170)]):
        c.poly(wave_band(W, -40 + i * 200, 22, 1.0, i * 1.4, H + 10), col)
    for x, y, r in ((120, 260, 20), (160, 200, 12), (100, 150, 16), (650, 330, 22), (690, 270, 13), (620, 220, 17)):
        c.circle(x, y, r, (200, 240, 255))
    # sand
    c.poly(wave_band(W, 860, 24, 1.2, 0.3, H + 10), (250, 226, 170))
    # seaweed
    for x, h in ((60, 300), (150, 220), (730, 260), (650, 200)):
        for k in range(4):
            leaf(c, x + (k % 2) * 8, 880, x + (-34 if k % 2 else 34), 880 - h * (0.5 + k * 0.17), 22, light=(70, 170, 90), dark=(40, 130, 80), curl=(-1) ** k)
    # coral
    def coral(x, y, col, arms=5, L=150):
        for k in range(arms):
            a = -math.pi / 2 + (k - (arms - 1) / 2) * 0.55
            ex, ey = x + L * math.cos(a), y + L * math.sin(a)
            c.poly(petal_pts(x, y, a, L, 30, tip=0.6), col if k % 2 == 0 else shade(col, 0.2))
            c.circle(ex, ey, 17, shade(col, 0.35))
    coral(280, 880, (240, 100, 130), 5, 190)
    coral(520, 890, (250, 150, 70), 6, 170)
    coral(420, 900, (180, 120, 220), 4, 130)
    # anemone
    ax, ay = 160, 860
    for k in range(9):
        c.poly(petal_pts(ax, ay, -math.pi / 2 + (k - 4) * 0.3, 110, 12, tip=0.5), (255, 190, 90) if k % 2 else (255, 140, 100))
    c.ellipse(ax, ay, 55, 26, (240, 110, 80))
    # fish
    def fish(x, y, L, body, fin, stripe, flip=1):
        def P(a, b):
            return (x + flip * a, y + b)
        c.poly([P(-L * 0.4, 0), P(-L * 0.78, -L * 0.3), P(-L * 0.7, 0), P(-L * 0.78, L * 0.3)], fin)
        c.poly([P(-L * 0.1, -L * 0.28), P(L * 0.1, -L * 0.5), P(L * 0.2, -L * 0.28)], fin)
        c.poly([P(L * 0.5 * math.cos(t), L * 0.3 * math.sin(t)) for t in [i / 40 * 2 * math.pi for i in range(40)]], body)
        for dx in (-0.12, 0.12):
            c.poly([P(L * dx - 8, -L * 0.28), P(L * dx + 8, -L * 0.28), P(L * dx + 8, L * 0.28), P(L * dx - 8, L * 0.28)], stripe)
        c.circle(*P(L * 0.33, -L * 0.05), L * 0.07, WHITE)
        c.circle(*P(L * 0.35, -L * 0.05), L * 0.035, (30, 30, 40), width=1)
    fish(300, 330, 230, (255, 170, 60), (245, 120, 60), WHITE)
    fish(540, 560, 200, (130, 120, 240), (170, 150, 250), (250, 240, 120), flip=-1)
    fish(210, 620, 150, (250, 220, 90), (255, 190, 80), (60, 90, 120))
    # turtle? starfish
    c.poly(star_pts(660, 880, 55, inner=0.5, rot=-1.3), (255, 130, 100))
    c.circle(660, 880, 12, (255, 200, 170))


def scene_cottage(c):
    rng = c.rng
    W, H = c.w, c.h
    for i, col in enumerate([(200, 232, 250), (222, 240, 252), (255, 248, 224)]):
        c.poly(wave_band(W, -40 + i * 260, 20, 1.0, i * 1.0, H + 10), col)
    c.circle(130, 120, 65, (255, 224, 120))
    cloud(c, 600, 130, 85)
    c.poly(wave_band(W, 520, 40, 0.8, 0.0, H + 10), (150, 206, 120))
    c.poly(wave_band(W, 620, 34, 1.1, 1.8, H + 10), (110, 180, 100))
    # tree
    c.poly([(660, 700), (700, 700), (710, 430), (650, 430)], BROWN)
    for dx, dy, r in ((0, 0, 110), (-70, 60, 80), (70, 70, 85), (10, -70, 70)):
        c.circle(680 + dx, 380 + dy, r, LEAF if (dx + dy) % 2 else (96, 176, 96))
    for x, y in ((630, 400), (720, 430), (680, 340)):
        c.circle(x, y, 12, RED)
    # house
    hx0, hx1, hy0, hy1 = 150, 520, 520, 800
    c.poly([(hx0, hy0), (hx1, hy0), (hx1, hy1), (hx0, hy1)], CREAM)
    for i in range(5):
        c.line([(hx0, hy0 + 55 * (i + 1)), (hx1, hy0 + 55 * (i + 1))], width=2)
    # roof
    c.poly([(hx0 - 40, hy0), (hx1 + 40, hy0), ((hx0 + hx1) / 2 + 70, 330), ((hx0 + hx1) / 2 - 70, 330)], (200, 90, 70))
    for i in range(4):
        y = 330 + (hy0 - 330) * (i + 1) / 5
        c.line([((hx0 + hx1) / 2 - 70 - (i + 1) * 20, y), ((hx0 + hx1) / 2 + 70 + (i + 1) * 20, y)], width=3)
    c.poly([(400, 300), (440, 300), (440, 400), (400, 380)], (150, 80, 70))   # chimney
    c.poly([(395, 296), (445, 296), (445, 312), (395, 312)], (110, 70, 66))
    c.circle(335, 440, 36, (255, 240, 150))                                  # attic window
    c.line([(335, 404), (335, 476)], width=3)
    c.line([(299, 440), (371, 440)], width=3)
    # door
    c.poly([(290, 800), (290, 640), (320, 610), (350, 640), (350, 800)], (60, 130, 140))
    c.circle(338, 715, 6, GOLD, width=2)
    # windows
    for x in (190, 400):
        c.poly([(x, 600), (x + 90, 600), (x + 90, 700), (x, 700)], SKY_L)
        c.line([(x + 45, 600), (x + 45, 700)], width=3)
        c.line([(x, 650), (x + 90, 650)], width=3)
        c.poly([(x - 8, 700), (x + 98, 700), (x + 98, 716), (x - 8, 716)], (140, 90, 70))
        for k in range(3):
            c.circle(x + 14 + k * 30, 704, 9, [ROSE, BUTTER, PINK][k])
    # path
    c.poly([(290, 800), (350, 800), (480, H + 10), (190, H + 10)], (232, 210, 170))
    for y, wd in ((860, 40), (920, 55), (975, 70)):
        c.ellipse(320, y, wd, 14, (210, 186, 146))
    # fence + flowers
    for i in range(9):
        x = 40 + i * 28 if i < 4 else 560 + (i - 4) * 38
        if 120 < x < 540:
            continue
        c.poly([(x, 800), (x + 22, 800), (x + 22, 880), (x - 0, 880)], WHITE)
    for x, y, col in ((110, 880, ROSE), (160, 900, BUTTER), (470, 880, LILAC), (530, 905, CORAL), (240, 920, PINK)):
        c.line([(x, y), (x, y + 50)], width=4)
        daisy(c, x, y, 30, col, GOLD, n=8)


def scene_rainbow(c):
    rng = c.rng
    W, H = c.w, c.h
    for i, col in enumerate([(176, 214, 245), (200, 228, 250), (228, 242, 252), (255, 244, 224)]):
        c.poly(wave_band(W, -40 + i * 200, 18, 1.0, i * 1.2, H + 10), col)
    c.circle(680, 140, 70, (255, 224, 120))
    cx, cy = 400, 640
    bands = [(RED, 380), ((247, 129, 98), 335), (BUTTER, 290), ((100, 190, 110), 245), (SKY, 200), ((90, 110, 220), 155), (LILAC, 110)]
    for col, r in bands:
        c.circle(cx, cy, r, col)
    c.circle(cx, cy, 65, (228, 242, 252))
    cloud(c, 90, 650, 95)
    cloud(c, 720, 650, 95)
    c.poly(wave_band(W, 690, 36, 0.9, 0.4, H + 10), (150, 206, 120))
    c.poly(wave_band(W, 790, 30, 1.2, 1.9, H + 10), (110, 180, 100))
    c.poly(wave_band(W, 890, 24, 1.5, 0.9, H + 10), LEAF)
    for x, y, col in ((120, 800, ROSE), (260, 860, BUTTER), (420, 820, LILAC), (560, 870, CORAL), (690, 810, PINK), (340, 940, SKY)):
        c.line([(x, y), (x, y + 55)], width=4)
        daisy(c, x, y, 34, col, GOLD, n=8, rot=x)
    for x, y in ((230, 200), (330, 150), (560, 280)):
        c.line([(x - 28, y), (x - 12, y - 16), (x, y), (x + 12, y - 16), (x + 28, y)], width=4)
    butterfly(c, 150, 330, 50, BUTTER, GOLD, rot=0.3)


SCENES = {
    'bouquet': ('Spring Bouquet', 'flowers', scene_bouquet, 22),
    'sunset': ('Mountain Sunset', 'nature', scene_sunset, 26),
    'koi': ('Koi Pond', 'animals', scene_koi, 22),
    'mandala': ('Petal Mandala', 'things', scene_mandala, 22),
    'balloons': ('Balloon Festival', 'things', scene_balloons, 26),
    'hummingbird': ('Hummingbird', 'animals', scene_hummingbird, 22),
    'sunflower': ('Sunflower Field', 'flowers', scene_sunflower, 22),
    'owl': ('Night Owl', 'animals', scene_owl, 22),
    'butterfly': ('Butterfly Garden', 'animals', scene_butterfly, 24),
    'lighthouse': ('Lighthouse', 'nature', scene_lighthouse, 24),
    'mushrooms': ('Forest Mushrooms', 'nature', scene_mushrooms, 22),
    'reef': ('Coral Reef', 'animals', scene_reef, 24),
    'cottage': ('Cozy Cottage', 'things', scene_cottage, 24),
    'rainbow': ('Rainbow Meadow', 'nature', scene_rainbow, 22),
}


def main():
    os.makedirs(OUT, exist_ok=True)
    names = sys.argv[1:] or list(SCENES)
    for i, key in enumerate(SCENES):
        if key not in names:
            continue
        name, cat, fn, colors = SCENES[key]
        c = Canvas(seed=i + 3)
        fn(c)
        path = os.path.join(OUT, key + '.png')
        c.save(path)
        subprocess.run([sys.executable, os.path.join(HERE, '..', 'make_puzzle.py'), path, '--id', key, '--name', name,
                        '--category', cat, '--lines', '--colors', str(colors), '--size', '1400'], check=True)


if __name__ == '__main__':
    main()
