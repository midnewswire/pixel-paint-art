#!/usr/bin/env python3
"""Turns an illustration into a Pixel Paint color-by-number puzzle.

The game's pictures are "region" puzzles: the art is split into outlined
regions, each one a single palette color, and the player taps a numbered
region to fill it. This tool builds that from any picture:

  1. Reduce the image to a fixed palette (exact colors for flat line art,
     k-means for paintings/photos).
  2. Optionally treat dark line pixels as outlines (--lines), the way
     coloring-book art is drawn.
  3. Split each color into connected regions, fold regions too small to
     tap into their neighbors, and give every outline pixel to the
     nearest region.
  4. Write the files the game loads (see `lib/game/region_puzzle.dart`):
       assets/puzzles/<id>/regions.png  every pixel's region id (R = id >> 8, G = id & 255)
       assets/puzzles/<id>/lines.png    anti-aliased outlines (alpha = ink)
       assets/puzzles/<id>/puzzle.json  palette + per-region color and label spot
       assets/puzzles/<id>/thumb.png    finished picture, small, for the gallery
       assets/puzzles/<id>/sketch.png   outlines only, small, for the gallery
  5. Register it in assets/puzzles/index.json (gallery order) and list
     its folder under `flutter: assets:` in pubspec.yaml.

Usage:
  python3 tool/make_puzzle.py ART.png --id koi --name "Koi Pond" --category animals --lines
  python3 tool/make_puzzle.py painting.jpg --id tiger --name "Tiger" --category animals --colors 18

Needs: numpy, scipy, Pillow  (pip install numpy scipy pillow)
"""
import argparse
import json
import os

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
PUZZLES = os.path.join(ROOT, 'assets', 'puzzles')
CATEGORIES = ('animals', 'flowers', 'nature', 'things')


def load(path, long_side):
    img = Image.open(path).convert('RGB')
    scale = long_side / max(img.size)
    if abs(scale - 1) > 1e-3:
        img = img.resize((round(img.width * scale), round(img.height * scale)), Image.NEAREST if scale < 1 else Image.LANCZOS)
    return np.asarray(img).astype(np.int32)


def kmeans(pixels, k, iters=24, seed=7):
    """Plain k-means on RGB (k-means++ init). pixels: (n, 3) float."""
    rng = np.random.default_rng(seed)
    centers = [pixels[rng.integers(len(pixels))]]
    for _ in range(1, k):
        d = np.min(((pixels[:, None, :] - np.array(centers)[None]) ** 2).sum(-1), axis=1)
        centers.append(pixels[rng.choice(len(pixels), p=d / d.sum())])
    centers = np.array(centers, dtype=np.float64)
    for _ in range(iters):
        labels = np.argmin(((pixels[:, None, :] - centers[None]) ** 2).sum(-1), axis=1)
        for j in range(k):
            members = pixels[labels == j]
            if len(members):
                centers[j] = members.mean(0)
    return centers


def quantize(rgb, max_colors, line_mask):
    """Returns (class map with -1 for lines, palette as (n,3) ints)."""
    fill = rgb[~line_mask]
    flat = fill[:, 0] * 65536 + fill[:, 1] * 256 + fill[:, 2]
    uniq, counts = np.unique(flat, return_counts=True)
    if len(uniq) <= max_colors:
        palette = np.stack([uniq // 65536, (uniq // 256) % 256, uniq % 256], 1)
    else:
        img = Image.fromarray(rgb.astype(np.uint8)).filter(ImageFilter.MedianFilter(5))
        rgb = np.asarray(img).astype(np.int32)
        sample = rgb[~line_mask][::max(1, (~line_mask).sum() // 40000)].astype(np.float64)
        palette = np.clip(np.round(kmeans(sample, max_colors)), 0, 255).astype(np.int32)
    h, w, _ = rgb.shape
    cls = np.empty((h, w), np.int32)
    flat_rgb = rgb.reshape(-1, 3)
    out = cls.reshape(-1)
    for start in range(0, len(flat_rgb), 200000):
        chunk = flat_rgb[start:start + 200000]
        out[start:start + 200000] = np.argmin(((chunk[:, None, :] - palette[None]) ** 2).sum(-1), axis=1)
    cls[line_mask] = -1
    return cls, palette


def components(cls):
    """Region id map (1..n) of connected same-class areas; lines get 0."""
    ids = np.zeros(cls.shape, np.int32)
    next_id = 1
    for c in np.unique(cls):
        if c < 0:
            continue
        lab, n = ndimage.label(cls == c)
        mask = lab > 0
        ids[mask] = lab[mask] + (next_id - 1)
        next_id += n
    return ids, next_id - 1


def absorb_small(cls, min_area, min_depth=4.5, passes=6):
    """Folds every region smaller than min_area into the class that
    surrounds it most, so nothing is too small to tap."""
    for _ in range(passes):
        ids, n = components(cls)
        if n == 0:
            break
        areas = np.bincount(ids.ravel(), minlength=n + 1)
        # Depth = how far the region's deepest pixel is from its edge;
        # thin slivers (along outlines) are as hard to tap as tiny ones.
        edge = ids == 0
        edge[:, 1:] |= ids[:, 1:] != ids[:, :-1]
        edge[1:, :] |= ids[1:, :] != ids[:-1, :]
        depth = ndimage.maximum(ndimage.distance_transform_edt(~edge), ids, np.arange(n + 1))
        small = np.where((areas < min_area) | (np.asarray(depth) < min_depth))[0]
        small = small[small > 0]
        if len(small) == 0:
            break
        is_small = np.isin(ids, small)
        # Give each small-region pixel the class of the nearest pixel that
        # is in a big region (lines count as "nowhere").
        keep = ~is_small & (cls >= 0)
        _, (iy, ix) = ndimage.distance_transform_edt(~keep, return_indices=True)
        nearest = cls[iy, ix]
        # Decide per region (majority of its pixels' nearest class) so a
        # small region becomes one solid neighbor, not a split.
        lab = ids[is_small].astype(np.int64)
        near = nearest[is_small].astype(np.int64)
        k = int(cls.max()) + 2
        pairs, counts = np.unique(lab * k + (near + 1), return_counts=True)
        best = {}
        for pair, cnt in zip(pairs.tolist(), counts.tolist()):
            rid, c = divmod(pair, k)
            if c > 0 and cnt > best.get(rid, (0, -1))[0]:
                best[rid] = (cnt, c - 1)
        lut = np.arange(n + 1, dtype=np.int64) * 0 - 2
        for rid, (_, c) in best.items():
            lut[rid] = c
        new = lut[lab]
        cur = cls[is_small]
        cls[is_small] = np.where(new >= -1, new, cur)
    return cls


def assign_lines(ids):
    """Every outline pixel joins its nearest region."""
    if (ids == 0).any():
        _, (iy, ix) = ndimage.distance_transform_edt(ids == 0, return_indices=True)
        ids = ids[iy, ix]
    return ids


def renumber(ids):
    uniq, inv = np.unique(ids, return_inverse=True)
    return inv.reshape(ids.shape).astype(np.int32) + 1, len(uniq)


def label_spots(ids, n):
    """Per region: (x, y, r) = the point deepest inside it and its depth,
    where the number goes and how big it can be."""
    spots = [None] * (n + 1)
    objs = ndimage.find_objects(ids)
    for rid, sl in enumerate(objs, start=1):
        if sl is None:
            continue
        mask = np.pad(ids[sl] == rid, 1)
        dist = ndimage.distance_transform_edt(mask)
        y, x = np.unravel_index(np.argmax(dist), dist.shape)
        spots[rid] = (int(sl[1].start + x - 1), int(sl[0].start + y - 1), float(dist[y, x]))
    return spots


def render_lines(ids, factor=3, width=1.4):
    """Anti-aliased boundary lines, as an alpha mask the size of ids."""
    big = np.kron(ids, np.ones((factor, factor), np.int32))
    edge = np.zeros(big.shape, bool)
    edge[:, 1:] |= big[:, 1:] != big[:, :-1]
    edge[1:, :] |= big[1:, :] != big[:-1, :]
    dist = ndimage.distance_transform_edt(~edge)
    alpha = np.clip(1.0 - (dist - width * factor / 2) / 1.2, 0, 1)
    img = Image.fromarray((alpha * 255).astype(np.uint8))
    return img.resize((ids.shape[1], ids.shape[0]), Image.LANCZOS)


def hue_order(palette):
    """Palette order: by hue, grays last, so neighboring numbers look related."""
    import colorsys

    def key(c):
        h, l, s = colorsys.rgb_to_hls(*(c / 255.0))
        return (1 if s < 0.12 else 0, round(h * 12) if s >= 0.12 else 0, l)

    return sorted(range(len(palette)), key=lambda i: key(palette[i]))


def register_asset_dir(pid):
    """Flutter asset folders aren't recursive: list the new one in pubspec.yaml."""
    path = os.path.join(ROOT, 'pubspec.yaml')
    lines = open(path).read().split('\n')
    entry = f'    - assets/puzzles/{pid}/'
    if entry in lines:
        return
    anchor = lines.index('    - assets/puzzles/')
    lines.insert(anchor + 1, entry)
    with open(path, 'w') as f:
        f.write('\n'.join(lines))


def build(args):
    rgb = load(args.image, args.size)
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    line_mask = lum < args.line_threshold if args.lines else np.zeros(lum.shape, bool)

    cls, palette = quantize(rgb, args.colors, line_mask)
    min_area = args.min_area if args.min_area else max(60, int(rgb.shape[0] * rgb.shape[1] * 0.00015))
    cls = absorb_small(cls, min_area)

    ids, _ = components(cls)
    ids = assign_lines(ids)
    ids, n = renumber(ids)
    # Final sweep: anything still too small or thin is handed, pixel by
    # pixel, to the nearest surviving region.
    for _ in range(3):
        areas = np.bincount(ids.ravel(), minlength=n + 1)
        edge = np.zeros(ids.shape, bool)
        edge[:, 1:] |= ids[:, 1:] != ids[:, :-1]
        edge[1:, :] |= ids[1:, :] != ids[:-1, :]
        depth = np.asarray(ndimage.maximum(ndimage.distance_transform_edt(~edge), ids, np.arange(n + 1)))
        bad = np.where((areas < min_area) | (depth < 4.0))[0]
        bad = bad[bad > 0]
        if len(bad) == 0:
            break
        ids[np.isin(ids, bad)] = 0
        ids = assign_lines(ids)
        ids, n = renumber(ids)
    # Region -> palette class: the majority class of its (non-line) pixels.
    flat_ids = ids.ravel().astype(np.int64)
    flat_cls = cls.ravel().astype(np.int64)
    valid = flat_cls >= 0
    k = int(cls.max()) + 1
    counts = np.bincount(flat_ids[valid] * k + flat_cls[valid], minlength=(n + 1) * k).reshape(n + 1, k)
    region_cls = np.where(counts.sum(1) > 0, counts.argmax(1), -1)
    if (region_cls[1:] < 0).any():
        raise SystemExit('internal error: a region has no color')

    used = sorted(set(region_cls[1:].tolist()))
    order = [used[i] for i in hue_order(palette[used])]
    remap = {old: new for new, old in enumerate(order)}
    spots = label_spots(ids, n)
    h, w = ids.shape

    puzzles_dir = os.path.abspath(args.puzzles_dir) if args.puzzles_dir else PUZZLES
    out_dir = os.path.join(puzzles_dir, args.id)
    os.makedirs(out_dir, exist_ok=True)
    enc = np.zeros((h, w, 3), np.uint8)
    enc[..., 0] = ids >> 8
    enc[..., 1] = ids & 255
    Image.fromarray(enc).save(os.path.join(out_dir, 'regions.png'), optimize=True)

    lines = render_lines(ids)
    line_rgba = np.zeros((h, w, 4), np.uint8)
    line_rgba[..., :3] = (38, 34, 48)
    line_rgba[..., 3] = np.asarray(lines)
    Image.fromarray(line_rgba).save(os.path.join(out_dir, 'lines.png'), optimize=True)

    pal = np.array([palette[o] for o in order], np.uint8)
    color_of = np.array([0] + [remap[c] for c in region_cls[1:]], np.int32)
    finished = pal[color_of[ids]]
    ink = np.asarray(lines, np.float32)[..., None] / 255.0
    finished = (finished * (1 - ink) + np.array([38, 34, 48]) * ink).astype(np.uint8)
    sketch = (255 * (1 - ink) + np.array([38, 34, 48]) * ink).astype(np.uint8)
    tw = 320
    th = round(h * tw / w)
    Image.fromarray(finished).resize((tw, th), Image.LANCZOS).save(os.path.join(out_dir, 'thumb.png'), optimize=True)
    Image.fromarray(sketch[..., 0]).resize((tw, th), Image.LANCZOS).save(os.path.join(out_dir, 'sketch.png'), optimize=True)

    meta = {
        'id': args.id,
        'name': args.name,
        'category': args.category,
        'width': w,
        'height': h,
        'palette': ['%02X%02X%02X' % tuple(int(v) for v in c) for c in pal],
        # One entry per region id (1-based in regions.png): [color, x, y, r]
        'regions': [[int(color_of[r]), spots[r][0], spots[r][1], round(spots[r][2], 1)] for r in range(1, n + 1)],
    }
    with open(os.path.join(out_dir, 'puzzle.json'), 'w') as f:
        json.dump(meta, f, separators=(',', ':'))

    if not args.no_register:
        index_path = os.path.join(PUZZLES, 'index.json')
        index = json.load(open(index_path)) if os.path.exists(index_path) else []
        if args.id not in index:
            index.append(args.id)
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=1)

        register_asset_dir(args.id)

    small = sum(1 for r in range(1, n + 1) if spots[r][2] < 6)
    print(f'{args.id}: {w}x{h}, {len(pal)} colors, {n} regions ({small} tiny), min area {min_area}px -> {os.path.relpath(out_dir, os.getcwd())}')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('image')
    p.add_argument('--id', required=True, help='lowercase id, also the asset folder name')
    p.add_argument('--name', required=True, help='name shown in the gallery')
    p.add_argument('--category', required=True, choices=CATEGORIES)
    p.add_argument('--colors', type=int, default=16, help='max palette size (default 16)')
    p.add_argument('--size', type=int, default=1400, help='long side in pixels (default 1400)')
    p.add_argument('--puzzles-dir', help='write <dir>/<id>/ instead of the app assets folder')
    p.add_argument('--no-register', action='store_true', help='do not touch index.json / pubspec.yaml (catalog-style output)')
    p.add_argument('--lines', action='store_true', help='treat dark pixels as outlines (coloring-book art)')
    p.add_argument('--line-threshold', type=int, default=60, help='luminance below which a pixel is a line')
    p.add_argument('--min-area', type=int, default=0, help='smallest region in pixels (default ~0.012%% of the image)')
    build(p.parse_args())


if __name__ == '__main__':
    main()
