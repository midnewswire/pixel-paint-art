#!/usr/bin/env python3
"""Generates new Pixel Paint pictures and adds them to catalog.json.

  python3 tool/generate.py --count 3            # next 3 pictures
  python3 tool/generate.py --count 1 --seed 42  # reproducible

Each picture is a seeded random scene (tool/art/variants.py) turned into a
puzzle by tool/make_puzzle.py, checked, and appended to catalog.json. Only
pictures that pass the checks are kept. The app reads catalog.json and
downloads a picture's files when the player opens it.
"""
import argparse
import datetime
import hashlib
import json
import os
import random
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'tool', 'art'))
from shapes import Canvas  # noqa: E402
from variants import NOUNS, TEMPLATES  # noqa: E402

PUZZLES = os.path.join(ROOT, 'puzzles')
CATALOG = os.path.join(ROOT, 'catalog.json')
FILES = ('puzzle.json', 'regions.png', 'lines.png', 'thumb.png', 'sketch.png')


def load_catalog():
    if os.path.exists(CATALOG):
        return json.load(open(CATALOG))
    return {'version': 1, 'puzzles': []}


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def check(pid):
    """Returns a list of problems with the built puzzle (empty = good)."""
    d = os.path.join(PUZZLES, pid)
    problems = []
    for name in FILES:
        if not os.path.exists(os.path.join(d, name)):
            problems.append('missing ' + name)
    if problems:
        return problems
    meta = json.load(open(os.path.join(d, 'puzzle.json')))
    regions = meta['regions']
    n = len(regions)
    if not 25 <= n <= 260:
        problems.append(f'{n} regions (want 25-260)')
    if not 6 <= len(meta['palette']) <= 28:
        problems.append(f'{len(meta["palette"])} colors (want 6-28)')
    used = {r[0] for r in regions}
    if len(used) != len(meta['palette']):
        problems.append('unused palette color')
    tiny = sum(1 for r in regions if r[3] < 6)
    if tiny > max(2, n * 0.05):
        problems.append(f'{tiny} tiny regions')
    total = sum(os.path.getsize(os.path.join(d, f)) for f in FILES)
    if total > 900_000:
        problems.append(f'{total // 1000} KB (want < 900)')
    return problems


def build(pid, name, category, template, seed):
    fn = TEMPLATES[template][0]
    import random as _r
    rng = _r.Random(seed)
    c = Canvas(seed=seed)
    c.rng = rng
    fn(c, rng)
    out = os.path.join(ROOT, 'tool', 'art', 'out')
    os.makedirs(out, exist_ok=True)
    png = os.path.join(out, pid + '.png')
    c.save(png)
    subprocess.run([sys.executable, os.path.join(ROOT, 'tool', 'make_puzzle.py'), png, '--id', pid, '--name', name,
                    '--category', category, '--lines', '--colors', '24', '--size', '1400',
                    '--puzzles-dir', PUZZLES, '--no-register'], check=True, stdout=subprocess.DEVNULL)


def entry(pid, name, category):
    d = os.path.join(PUZZLES, pid)
    meta = json.load(open(os.path.join(d, 'puzzle.json')))
    return {
        'id': pid,
        'name': name,
        'category': category,
        'colors': len(meta['palette']),
        'regions': len(meta['regions']),
        'added': datetime.date.today().isoformat(),
        'files': {f: {'bytes': os.path.getsize(os.path.join(d, f)), 'sha256': sha256(os.path.join(d, f))} for f in FILES},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--count', type=int, default=1)
    ap.add_argument('--seed', type=int, help='base seed (default: derived from the catalog size)')
    args = ap.parse_args()

    catalog = load_catalog()
    have = {p['id'] for p in catalog['puzzles']}
    names = {p['name'] for p in catalog['puzzles']}
    templates = list(TEMPLATES)
    added = 0
    attempt = 0
    start = len(catalog['puzzles'])
    base = args.seed if args.seed is not None else start * 101 + 7
    while added < args.count and attempt < args.count * 6:
        seed = base + attempt * 13
        template = templates[(start + attempt) % len(templates)]
        attempt += 1
        _, category, adjectives = TEMPLATES[template]
        rng = random.Random(seed)
        name = f'{rng.choice(adjectives)} {NOUNS[template]}'
        n = 2
        while name in names:
            name = f'{name.rsplit(" #", 1)[0]} #{n}'
            n += 1
        pid = f'{template}-{seed}'
        if pid in have:
            continue
        try:
            build(pid, name, category, template, seed)
        except Exception as error:  # a bad seed shouldn't stop the batch
            print(f'{pid}: build failed: {error}')
            shutil.rmtree(os.path.join(PUZZLES, pid), ignore_errors=True)
            continue
        problems = check(pid)
        if problems:
            print(f'{pid}: rejected: {"; ".join(problems)}')
            shutil.rmtree(os.path.join(PUZZLES, pid), ignore_errors=True)
            continue
        catalog['puzzles'].append(entry(pid, name, category))
        names.add(name)
        have.add(pid)
        added += 1
        print(f'{pid}: added "{name}" ({catalog["puzzles"][-1]["regions"]} regions)')

    catalog['updated'] = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with open(CATALOG, 'w') as f:
        json.dump(catalog, f, indent=1)
    if added < args.count:
        print(f'only {added} of {args.count} pictures passed the checks')
        sys.exit(1 if added == 0 else 0)


if __name__ == '__main__':
    main()
