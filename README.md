# Pixel Paint art

Puzzle files for the Pixel Paint color-by-number app, plus the generator
that makes them. The app reads `catalog.json` and downloads a picture's
files only when the player opens it.

## How it works

- `tool/art/variants.py` – seeded random scene templates (mandala, garden, reef).
- `tool/make_puzzle.py` – turns a picture into a puzzle (regions, outlines, thumbnail).
- `tool/generate.py` – builds new pictures, rejects bad ones (too few/many regions, too many tiny
  regions, oversized files) and appends the good ones to `catalog.json` with SHA-256 checksums.
- `.github/workflows/generate.yml` – runs the generator every Monday and opens a pull request.
  Review the thumbnails, then merge to publish.

Published URL (GitHub Pages): `https://midnewswire.github.io/pixel-paint-art/catalog.json`

## Run it locally

```
pip install -r requirements.txt
python tool/generate.py --count 3
```

## Layout

```
catalog.json            list of pictures + file sizes + checksums
puzzles/<id>/           puzzle.json, regions.png, lines.png, thumb.png, sketch.png
```
