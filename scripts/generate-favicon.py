#!/usr/bin/env python3
"""Generate site favicon assets with a monogram letter."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "favicon"
LETTER = "M"
ORANGE_LIGHT = (255, 176, 60)
ORANGE_DARK = (232, 93, 40)
FONT_CANDIDATES = (
    Path(r"C:\Windows\Fonts\arialbd.ttf"),
    Path(r"C:\Windows\Fonts\segoeuib.ttf"),
    Path(r"C:\Windows\Fonts\calibrib.ttf"),
)


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _in_rounded_rect(x: int, y: int, size: int, radius: float) -> bool:
    r = radius
    if x < r and y < r:
        return (x - r) ** 2 + (y - r) ** 2 <= r**2
    if x > size - 1 - r and y < r:
        return (x - (size - 1 - r)) ** 2 + (y - r) ** 2 <= r**2
    if x < r and y > size - 1 - r:
        return (x - r) ** 2 + (y - (size - 1 - r)) ** 2 <= r**2
    if x > size - 1 - r and y > size - 1 - r:
        return (x - (size - 1 - r)) ** 2 + (y - (size - 1 - r)) ** 2 <= r**2
    return True


def make_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    radius = size * 0.22
    for y in range(size):
        for x in range(size):
            if not _in_rounded_rect(x, y, size, radius):
                continue
            t = (x + y) / max(2 * (size - 1), 1)
            rgb = tuple(
                int(ORANGE_LIGHT[i] * (1 - t) + ORANGE_DARK[i] * t) for i in range(3)
            )
            px[x, y] = rgb + (255,)

    draw = ImageDraw.Draw(img)
    font = _font(max(12, int(size * 0.56)))
    bbox = draw.textbbox((0, 0), LETTER, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (size - tw) // 2 - bbox[0]
    ty = (size - th) // 2 - bbox[1]
    draw.text((tx, ty), LETTER, fill=(0, 0, 0, 255), font=font)
    return img


def write_svg() -> None:
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
        "<rect width='100' height='100' rx='22'/>"
        f"<text x='50' y='52' font-family='Arial, Helvetica, sans-serif' "
        f"font-size='58' font-weight='800' fill='#fff' text-anchor='middle' "
        f"dominant-baseline='central'>{LETTER}</text></svg>"
    )
    (OUT / "safari-pinned-tab.svg").write_text(svg, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    icon16 = make_icon(16)
    icon32 = make_icon(32)
    icon180 = make_icon(180)

    icon16.save(OUT / "favicon-16x16.png")
    icon32.save(OUT / "favicon-32x32.png")
    icon180.save(OUT / "apple-touch-icon.png")
    icon16.save(
        OUT / "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32)],
        append_images=[icon32],
    )
    write_svg()
    print(f"Wrote favicon assets with letter {LETTER!r} to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
