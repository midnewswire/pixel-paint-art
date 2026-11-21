"""Small vector-drawing kit for Pixel Paint's built-in line art.

Every shape is a flat fill with a dark outline, drawn without
anti-aliasing, so tool/make_puzzle.py (with --lines) can recover the
exact regions and colors.
"""
import math
import random

from PIL import Image, ImageDraw

INK = (20, 18, 26)
LINE = 3


class Canvas:
    """Scenes draw in an 800x1000 coordinate space; [scale] sets the
    real pixel size (1.4 -> 1120x1400), so art stays the same at any
    output resolution."""

    def __init__(self, w=800, h=1000, bg=(255, 255, 255), seed=1, scale=1.4):
        self.w, self.h = w, h
        self.k = scale
        self.img = Image.new('RGB', (round(w * scale), round(h * scale)), bg)
        self.d = ImageDraw.Draw(self.img)
        self.rng = random.Random(seed)

    def _pts(self, pts):
        return [(float(x) * self.k, float(y) * self.k) for x, y in pts]

    def _w(self, width):
        return max(1, round(width * self.k))

    def poly(self, pts, fill, width=LINE):
        pts = self._pts(pts)
        self.d.polygon(pts, fill=fill)
        self.d.line(pts + [pts[0]], fill=INK, width=self._w(width), joint='curve')

    def line(self, pts, width=LINE):
        self.d.line(self._pts(pts), fill=INK, width=self._w(width), joint='curve')

    def circle(self, cx, cy, r, fill, width=LINE):
        k = self.k
        self.d.ellipse([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], fill=fill, outline=INK, width=self._w(width))

    def ellipse(self, cx, cy, rx, ry, fill, angle=0.0, n=48):
        self.poly(ellipse_pts(cx, cy, rx, ry, angle, n), fill)

    def border(self):
        self.d.rectangle([0, 0, self.img.width - 1, self.img.height - 1], outline=INK, width=self._w(LINE + 1))

    def save(self, path):
        self.border()
        self.img.save(path)


def ellipse_pts(cx, cy, rx, ry, angle=0.0, n=48):
    ca, sa = math.cos(angle), math.sin(angle)
    out = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return out


def petal_pts(cx, cy, angle, length, width, n=28, tip=1.0, base=0.0):
    """A rounded petal from (cx, cy) outward along angle. tip<1 makes a
    blunter end; base>0 starts it away from the center."""
    pts = []
    ca, sa = math.cos(angle), math.sin(angle)
    for i in range(n + 1):
        t = i / n
        along = base + (length - base) * t
        half = width * math.sin(math.pi * min(1.0, t * (0.5 + 0.5 * tip) + (1 - tip) * 0.5 * t)) ** 0.8
        pts.append((along, half))
    side = [(a, h) for a, h in pts] + [(a, -h) for a, h in reversed(pts)]
    return [(cx + a * ca - h * sa, cy + a * sa + h * ca) for a, h in side]


def leaf_halves(bx, by, tx, ty, width, n=20, curl=0.0):
    """Two halves of a leaf split along its midrib: returns (left, right)."""
    dx, dy = tx - bx, ty - by
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    mid = []
    left = []
    right = []
    for i in range(n + 1):
        t = i / n
        bend = curl * math.sin(math.pi * t) * L * 0.15
        mx = bx + dx * t + nx * bend
        my = by + dy * t + ny * bend
        w = width * math.sin(math.pi * t) ** 0.9
        mid.append((mx, my))
        left.append((mx + nx * w, my + ny * w))
        right.append((mx - nx * w, my - ny * w))
    return left + list(reversed(mid)), right + list(reversed(mid))


def blob_pts(cx, cy, r, rng, wobble=0.18, n=40, lobes=5):
    phase = [rng.uniform(0, 6.28) for _ in range(3)]
    out = []
    for i in range(n):
        t = 2 * math.pi * i / n
        k = 1 + wobble * (math.sin(lobes * t + phase[0]) * 0.6 + math.sin((lobes + 2) * t + phase[1]) * 0.4)
        out.append((cx + r * k * math.cos(t), cy + r * k * math.sin(t)))
    return out


def wave_band(w, y, amp, freq, phase, h_to, steps=60):
    """Polygon from a wavy line at height y down to y = h_to."""
    top = [(w * i / steps, y + amp * math.sin(freq * i / steps * 2 * math.pi + phase)) for i in range(steps + 1)]
    return top + [(w + 5, h_to), (-5, h_to)]


def ridge(w, base, peaks, rng, rough=0.25):
    """Mountain silhouette polygon from a list of (x, height) peaks."""
    pts = [(-5, base)]
    for x, hgt in peaks:
        pts.append((x, base - hgt))
    pts.append((w + 5, base))
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        for i in range(6):
            t = i / 6
            jitter = rng.uniform(-1, 1) * rough * abs(y1 - y0) * 0.25 if 0 < i else 0
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + jitter))
    out.append(pts[-1])
    return out


def shade(c, f):
    """Lighten (f>0) or darken (f<0) an RGB color."""
    if f >= 0:
        return tuple(int(v + (255 - v) * f) for v in c)
    return tuple(int(v * (1 + f)) for v in c)
