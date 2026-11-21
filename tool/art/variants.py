"""Seeded, randomized scene templates for the scheduled generator.

Each template takes a Canvas and a random.Random and draws a different
picture every seed: different palettes, counts and placements. Colors are
kept light enough that tool/make_puzzle.py never mistakes them for
outlines (luminance threshold 60).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scenes import butterfly, cloud, daisy, leaf, rose, star_pts, tulip  # noqa: E402
from shapes import ellipse_pts, petal_pts, shade, wave_band  # noqa: E402

PALETTES = {
    'sunrise': [(255, 140, 110), (255, 186, 120), (255, 224, 130), (240, 110, 150), (190, 130, 220), (120, 190, 220), (150, 215, 170), (255, 205, 220)],
    'ocean': [(70, 170, 215), (110, 205, 225), (150, 225, 200), (90, 140, 220), (170, 160, 235), (255, 214, 120), (255, 160, 130), (210, 240, 245)],
    'meadow': [(120, 195, 110), (180, 225, 130), (255, 220, 110), (255, 160, 170), (200, 150, 230), (130, 200, 230), (250, 190, 120), (240, 245, 190)],
    'berry': [(220, 90, 140), (245, 140, 170), (170, 110, 215), (120, 130, 225), (250, 190, 210), (255, 220, 140), (140, 200, 205), (230, 170, 235)],
    'candy': [(255, 150, 190), (150, 215, 235), (255, 225, 130), (180, 225, 170), (200, 170, 240), (255, 180, 130), (130, 190, 240), (255, 205, 230)],
    'autumn': [(240, 130, 70), (250, 180, 80), (225, 95, 75), (190, 140, 90), (255, 215, 120), (170, 190, 100), (230, 160, 130), (250, 235, 190)],
}
SKIES = [(200, 230, 250), (255, 232, 200), (226, 216, 250), (210, 240, 232), (255, 220, 224)]


def _pick(rng, seq, n):
    seq = list(seq)
    rng.shuffle(seq)
    return [seq[i % len(seq)] for i in range(n)]


def mandala(c, rng):
    W, H = c.w, c.h
    cx, cy = W / 2, H / 2
    pal = rng.choice(list(PALETTES.values()))
    bg = rng.choice([(92, 110, 190), (150, 110, 200), (70, 150, 160), (200, 110, 140), (110, 160, 120)])
    c.poly([(0, 0), (W, 0), (W, H), (0, H)], bg)
    c.circle(cx, cy, 600, shade(bg, 0.12))
    rings = rng.randint(5, 7)
    length = 390
    for i in range(rings):
        n = rng.choice([8, 10, 12, 14, 16, 18, 20, 24])
        a, b = _pick(rng, pal, 2)
        rot = rng.uniform(0, math.pi)
        width = 0.5 * 90 * (16 / n) ** 0.4 * (0.9 + 0.2 * rng.random())
        for k in range(n):
            ang = rot + k * 2 * math.pi / n
            col = a if k % 2 == 0 else b
            c.poly(petal_pts(cx, cy, ang, length, width, base=length * 0.34), col)
            if length > 160 and rng.random() < 0.8:
                c.poly(petal_pts(cx, cy, ang, length * 0.84, width * 0.42, base=length * 0.52), shade(col, -0.18))
        length *= rng.uniform(0.7, 0.78)
    c.circle(cx, cy, 42, pal[0])
    c.circle(cx, cy, 22, pal[2])
    dots = rng.choice([16, 20, 24, 28])
    for k in range(dots):
        a = k * 2 * math.pi / dots
        c.circle(cx + 425 * math.cos(a), cy + 425 * math.sin(a), 11, rng.choice(pal[:4]))
    for x, y in ((60, 60), (W - 60, 60), (60, H - 60), (W - 60, H - 60)):
        for k in range(6):
            c.poly(petal_pts(x, y, k * math.pi / 3, 55, 18), pal[k % 3])
        c.circle(x, y, 14, pal[3])


def garden(c, rng):
    W, H = c.w, c.h
    sky = rng.choice(SKIES)
    for i in range(3):
        c.poly(wave_band(W, -40 + i * 300, 25, 1.0, rng.uniform(0, 3) + i, H + 10), shade(sky, 0.15 * i))
    if rng.random() < 0.5:
        c.circle(rng.uniform(100, 700), rng.uniform(100, 180), rng.uniform(55, 80), (255, 224, 120))
    else:
        cloud(c, rng.uniform(150, 650), rng.uniform(100, 200), rng.uniform(70, 95))
    greens = [(150, 206, 120), (110, 180, 100), (76, 160, 82)]
    base = rng.randint(560, 640)
    for i, g in enumerate(greens):
        c.poly(wave_band(W, base + i * 110, 30, rng.uniform(0.8, 1.5), rng.uniform(0, 6), H + 10), g)
    pal = rng.choice(list(PALETTES.values()))
    rows = [(rng.randint(430, 520), 1.0), (rng.randint(620, 700), 0.8), (rng.randint(780, 860), 0.65)]
    for y, s in rows:
        n = rng.randint(3, 4)
        for k in range(n):
            x = (k + 0.5) * W / n + rng.uniform(-45, 45)
            top = y + rng.uniform(-40, 40)
            c.poly([(x - 5, top), (x + 5, top), (x + 5, 920), (x - 5, 920)], (38, 112, 70))
            leaf(c, x, top + 130 * s, x + rng.choice((-1, 1)) * 65 * s, top + 70 * s, 24 * s)
            kind = rng.choice(('daisy', 'tulip', 'rose'))
            col = rng.choice(pal)
            if kind == 'daisy':
                daisy(c, x, top, 58 * s, col, (245, 166, 35), n=rng.choice((8, 10, 12)), rot=rng.uniform(0, 1))
            elif kind == 'tulip':
                tulip(c, x, top, 130 * s, col)
            else:
                rose(c, x, top, 62 * s, col, rot=rng.uniform(0, 3))
    for _ in range(rng.randint(1, 3)):
        a, b = _pick(rng, pal, 2)
        butterfly(c, rng.uniform(120, 680), rng.uniform(110, 330), rng.uniform(42, 70), a, b, rot=rng.uniform(-0.6, 0.6))


def reef(c, rng):
    W, H = c.w, c.h
    top = rng.choice([(120, 210, 240), (130, 220, 225), (150, 200, 245)])
    for i in range(5):
        c.poly(wave_band(W, -40 + i * 200, 22, 1.0, i * 1.4 + rng.random(), H + 10), shade(top, -0.07 * i))
    for _ in range(rng.randint(5, 9)):
        c.circle(rng.uniform(60, 740), rng.uniform(120, 600), rng.uniform(9, 24), (205, 242, 255))
    c.poly(wave_band(W, 870, 24, 1.2, rng.random() * 3, H + 10), (250, 226, 170))
    pal = rng.choice(list(PALETTES.values()))
    for _ in range(rng.randint(3, 4)):
        x = rng.uniform(60, 740)
        for k in range(3):
            leaf(c, x + k * 8, 890, x + (-32 if k % 2 else 32), 890 - rng.uniform(160, 300), 20, light=(70, 170, 90), dark=(40, 130, 80), curl=(-1) ** k)
    for x in sorted(rng.uniform(120, 700) for _ in range(rng.randint(3, 4))):
        col = rng.choice(pal)
        arms = rng.randint(4, 6)
        length = rng.uniform(120, 200)
        for k in range(arms):
            a = -math.pi / 2 + (k - (arms - 1) / 2) * 0.55
            c.poly(petal_pts(x, 895, a, length, 28, tip=0.6), col if k % 2 == 0 else shade(col, 0.2))
            c.circle(x + length * math.cos(a), 895 + length * math.sin(a), 16, shade(col, 0.35))
    for _ in range(rng.randint(3, 4)):
        x, y, L = rng.uniform(170, 630), rng.uniform(230, 700), rng.uniform(130, 230)
        flip = rng.choice((1, -1))
        body, fin, stripe = (rng.choice(pal) for _ in range(3))
        P = lambda a, b: (x + flip * a, y + b)  # noqa: E731
        c.poly([P(-L * 0.4, 0), P(-L * 0.78, -L * 0.3), P(-L * 0.7, 0), P(-L * 0.78, L * 0.3)], fin)
        c.poly([P(-L * 0.1, -L * 0.28), P(L * 0.1, -L * 0.5), P(L * 0.2, -L * 0.28)], fin)
        c.poly([P(L * 0.5 * math.cos(t), L * 0.3 * math.sin(t)) for t in [i / 40 * 2 * math.pi for i in range(40)]], body)
        for dx in (-0.12, 0.12):
            c.poly([P(L * dx - 8, -L * 0.28), P(L * dx + 8, -L * 0.28), P(L * dx + 8, L * 0.28), P(L * dx - 8, L * 0.28)], stripe)
        c.circle(*P(L * 0.33, -L * 0.05), L * 0.07, (255, 255, 255))
        c.circle(*P(L * 0.35, -L * 0.05), L * 0.035, (30, 30, 40), width=1)
    c.poly(star_pts(rng.uniform(80, 720), 885, 50, inner=0.5, rot=rng.uniform(-2, -1)), (255, 130, 100))


def balloons(c, rng):
    W, H = c.w, c.h
    sky = rng.choice(SKIES)
    for i in range(4):
        c.poly(wave_band(W, -40 + i * 230, 20, 1.0, i * 1.1 + rng.random(), H + 10), shade(sky, 0.1 * i))
    for _ in range(rng.randint(2, 3)):
        cloud(c, rng.uniform(100, 700), rng.uniform(80, 880), rng.uniform(60, 95))
    c.poly(wave_band(W, 800, 36, 0.9, rng.random() * 3, H + 10), (130, 196, 110))
    c.poly(wave_band(W, 890, 28, 1.3, rng.random() * 3, H + 10), (76, 160, 82))
    pal = rng.choice(list(PALETTES.values()))
    slots = [(210, 260, 120), (590, 340, 105), (400, 560, 130), (150, 650, 70), (660, 640, 75)]
    for x, y, r in slots[: rng.randint(3, 5)]:
        a, b, d = _pick(rng, pal, 3)
        c.ellipse(x, y, r, r * 1.15, a)
        for k in range(-2, 3):
            c.poly(ellipse_pts(x + k * r * 0.4, y, r * 0.2, r * 1.12, 0, 24)[:], b if k % 2 == 0 else d)
        c.poly([(x - r * 0.35, y + r * 1.05), (x + r * 0.35, y + r * 1.05), (x + r * 0.25, y + r * 1.5), (x - r * 0.25, y + r * 1.5)], (150, 90, 60))
        for sx in (-1, 1):
            c.line([(x + sx * r * 0.3, y + r * 1.05), (x + sx * r * 0.22, y + r * 1.5)], width=3)
        for k in range(2):
            c.circle(x + (k * 2 - 1) * r * 0.45, y - r * 0.2, r * 0.1, (255, 255, 255))


TEMPLATES = {
    'mandala': (mandala, 'things', ['Dream', 'Bloom', 'Aurora', 'Lotus', 'Starlight', 'Velvet', 'Harmony']),
    'garden': (garden, 'flowers', ['Wild', 'Morning', 'Secret', 'Sunny', 'Cottage', 'Spring', 'Lazy']),
    'reef': (reef, 'animals', ['Coral', 'Lagoon', 'Tide', 'Sunken', 'Rainbow', 'Hidden', 'Tropical']),
}
# (balloons() is parked: its stripes spill outside the balloon.)
NOUNS = {'mandala': 'Mandala', 'garden': 'Garden', 'reef': 'Reef'}
