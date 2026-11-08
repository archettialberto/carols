"""Locate filled noteheads on a raster scan and report their staff positions (development only).

  python sources/scripts/raster_heads.py PDF PAGE --clefs T,B --key F# [--dpi 400] [--x0 .. --x1 ..]

Finds staff lines (rows that are mostly dark across the page width), groups them in fives,
removes them, then reports compact dark blobs of notehead size as pitches per staff,
sorted by x. Hollow heads are filled before detection (head type is not reported); accidentals are not detected; durations and voices
must be read from the page. Requires PyMuPDF, numpy, scipy.
"""
import argparse
import fitz
import numpy as np
from scipy import ndimage

TOP_LINE = {'T': 38, 'T8': 31, 'B': 26}
ap = argparse.ArgumentParser(); ap.add_argument('pdf'); ap.add_argument('page', type=int)
ap.add_argument('--clefs', default='T,B'); ap.add_argument('--key', default='')
ap.add_argument('--dpi', type=int, default=400)
ap.add_argument('--line', type=float, default=.6, help='staff-line row darkness as a fraction of the darkest row')
ap.add_argument('--ink', type=int, default=150, help='grey level below which a pixel is ink')
a = ap.parse_args()
key = {i[0]: ('#' if '#' in i else 'b') for i in a.key.split(',') if i}
page = fitz.open(a.pdf)[a.page]
pix = page.get_pixmap(dpi=a.dpi, colorspace=fitz.csGRAY)
img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width) < a.ink
# Measure line darkness over a narrow central band so slightly skewed scans still show their lines.
w = img.shape[1]
rows = img[:, int(w * .45):int(w * .6)].mean(axis=1)
cand = np.where(rows > a.line * rows.max())[0]
lines = []
for y in cand:
    if lines and y - lines[-1][-1] <= 1: lines[-1].append(y)
    else: lines.append([y])
lines = [float(np.mean(g)) for g in lines]
staves = []
i = 0
while i + 4 < len(lines):
    gaps = np.diff(lines[i:i + 5])
    if gaps.max() - gaps.min() < 3: staves.append(lines[i:i + 5]); i += 5
    else: i += 1
clean = img.copy()
for staff in staves:
    for y in staff:
        y = int(round(y))
        for yy in range(y - 2, y + 3):
            # remove line pixels only where the column is not part of something taller
            above, below = img[max(0, yy - 4)], img[min(img.shape[0] - 1, yy + 4)]
            clean[yy] &= above | below
clefs = a.clefs.split(',')
for n, staff in enumerate(staves):
    gap = (staff[-1] - staff[0]) / 4
    top = staff[0]
    band = ndimage.binary_fill_holes(clean[int(top - 5 * gap):int(staff[-1] + 5 * gap)])  # hollow heads too
    # noteheads: open with an ellipse-ish structuring element to drop stems/beams/text strokes
    s = int(gap * .55)
    opened = ndimage.binary_opening(band, structure=np.ones((s, s)))
    lab, k = ndimage.label(opened)
    heads = []
    for sl in ndimage.find_objects(lab):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if .6 * gap < h < 2.6 * gap and .9 * gap < w < 1.9 * gap:
            cy = (sl[0].start + sl[0].stop) / 2 + int(top - 5 * gap); cx = (sl[1].start + sl[1].stop) / 2
            count = max(1, round(h / gap))  # a clump of two seconds counts twice
            for c in range(count):
                yy = cy + (c - (count - 1) / 2) * gap
                dia = TOP_LINE[clefs[n % len(clefs)]] - round((yy - top) / (gap / 2))
                L = 'CDEFGAB'[dia % 7]
                heads.append((cx * 72 / a.dpi, f'{L}{key.get(L, "")}{dia // 7}'))
    heads.sort()
    cols = []
    for x, p in heads:
        if cols and x - cols[-1][0] < 4: cols[-1][1].append(p)
        else: cols.append([x, [p]])
    print(f'staff {n} y={top * 72 / a.dpi:.0f} ({clefs[n % len(clefs)]}):', ' '.join(f"{x:.0f}:{'/'.join(ps)}" for x, ps in cols))
