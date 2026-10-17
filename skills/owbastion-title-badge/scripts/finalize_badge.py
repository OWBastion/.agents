# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow", "numpy", "scipy"]
# ///
"""Turn a raw generated title badge (magenta background) into a publishable transparent PNG.

Pipeline: key out the #FF00FF background flood-connected to the border, drop every
foreground blob except the badge (this removes the generator's corner watermark),
despill magenta from edge pixels, then scale and centre the badge to the standard
geometry shared by the published set.

    uv run scripts/finalize_badge.py RAW.png OUT.png [--preview PREVIEW.png]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

CANVAS = 2048
BADGE_WIDTH = 1596  # modal width of the published set; height follows the badge aspect
MAGENTA = np.array([255.0, 0.0, 255.0])
BG_DISTANCE = 90  # RGB distance to #FF00FF still counted as background
EDGE_BAND = 4  # px around the background where partial alpha and despill apply


def key_badge(rgb: np.ndarray) -> np.ndarray:
    """Return an RGBA array with the badge isolated and magenta removed."""
    dist = np.linalg.norm(rgb - MAGENTA, axis=2)
    near = dist < BG_DISTANCE
    labels, _ = ndimage.label(near)
    border = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    background = np.isin(labels, border[border > 0])
    # Magenta enclosed by the badge (a pink motif) stays foreground because it never touches the border.

    foreground = ~background
    foreground = ndimage.binary_opening(foreground, iterations=2)
    labels, count = ndimage.label(foreground)
    if count == 0:
        sys.exit("no badge found: is the background #FF00FF?")
    sizes = ndimage.sum(foreground, labels, range(1, count + 1))
    badge = ndimage.binary_fill_holes(labels == (int(np.argmax(sizes)) + 1))

    # Soft edge: inside the band next to the removed background, estimate coverage from
    # the magenta contamination (min(R,B) - G) and un-mix the colour.
    band = badge & (ndimage.distance_transform_edt(badge) <= EDGE_BAND)
    contamination = np.clip((np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1]) / 255.0, 0, 1)
    alpha = np.where(band, 1.0 - contamination, 1.0)
    alpha = np.where(badge, alpha, 0.0)
    safe = np.maximum(alpha, 1e-3)[..., None]
    colour = np.where(band[..., None], (rgb - (1 - alpha)[..., None] * MAGENTA) / safe, rgb)
    rgba = np.dstack([np.clip(colour, 0, 255), alpha * 255])
    return rgba.astype(np.uint8)


def place(rgba: np.ndarray) -> Image.Image:
    ys, xs = np.where(rgba[..., 3] > 128)
    crop = Image.fromarray(rgba).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    scale = BADGE_WIDTH / crop.width
    crop = crop.resize((BADGE_WIDTH, round(crop.height * scale)), Image.LANCZOS)
    out = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    out.paste(crop, ((CANVAS - crop.width) // 2, (CANVAS - crop.height) // 2), crop)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("raw", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--preview", type=Path, help="write a 3-background contact sheet to check edges")
    args = parser.parse_args()

    rgb = np.asarray(Image.open(args.raw).convert("RGB"), dtype=np.float64)
    result = place(key_badge(rgb))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.out, optimize=True)

    alpha = np.asarray(result)[..., 3]
    ys, xs = np.where(alpha > 128)
    magenta_left = int(((np.asarray(result)[..., 0] > 200) & (np.asarray(result)[..., 1] < 80)
                        & (np.asarray(result)[..., 2] > 200) & (alpha > 0)).sum())
    print(f"{args.out}: {result.size[0]}x{result.size[1]} badge {xs.max() - xs.min() + 1}x{ys.max() - ys.min() + 1} "
          f"centre ({(xs.min() + xs.max()) / 2:.0f},{(ys.min() + ys.max()) / 2:.0f}) "
          f"corner alpha {alpha[0, 0]} magenta-like px {magenta_left}")

    if args.preview:
        sheet = Image.new("RGB", (3 * 512, 512))
        thumb = result.resize((512, 512), Image.LANCZOS)
        for i, colour in enumerate([(255, 255, 255), (24, 24, 28), (200, 200, 200)]):
            tile = Image.new("RGB", (512, 512), colour)
            tile.paste(thumb, mask=thumb.getchannel("A"))
            sheet.paste(tile, (i * 512, 0))
        sheet.save(args.preview)


if __name__ == "__main__":
    main()
