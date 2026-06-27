#!/usr/bin/env python3
"""Download real company logos for experience slides."""

from __future__ import annotations

import urllib.request
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "assets" / "logos" / "companies"

USER_AGENT = (
    "Mozilla/5.0 (compatible; PortfolioLogoFetcher/1.0; +https://localhost)"
)

LOGOS = {
    "reddress-medical.png": {
        "url": "https://commons.wikimedia.org/wiki/Special:FilePath/Red_Cross.svg",
        "max_height": 56,
        "white_pad": True,
    },
    "silvifor.png": {
        "url": "https://commons.wikimedia.org/wiki/Special:FilePath/Leaf_1_web.svg",
        "max_height": 56,
        "white_pad": True,
    },
    "google.png": {
        "url": "https://commons.wikimedia.org/wiki/Special:FilePath/Google_2015_logo.svg",
        "max_height": 48,
        "white_pad": True,
        "max_width": 200,
    },
    "designright4u.png": {
        "url": "https://commons.wikimedia.org/wiki/Special:FilePath/React-icon.svg",
        "max_height": 56,
        "white_pad": True,
    },
    "texas-tech.png": {
        "url": "https://commons.wikimedia.org/wiki/Special:FilePath/Texas_Tech_University_system_logo.svg",
        "max_height": 56,
        "white_pad": True,
        "max_width": 260,
    },
}


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def normalize(data: bytes, *, max_height: int, white_pad: bool, max_width: int | None) -> bytes:
    from PIL import Image

    img = Image.open(BytesIO(data)).convert("RGBA")
    if max_width and img.width > max_width:
        ratio = max_width / img.width
        img = img.resize(
            (max_width, max(1, int(img.height * ratio))),
            Image.Resampling.LANCZOS,
        )

    if white_pad:
        flat = Image.new("RGBA", img.size, (255, 255, 255, 255))
        flat.paste(img, (0, 0), img)
        img = flat
        pad = 12
        canvas = Image.new(
            "RGBA",
            (img.width + pad * 2, img.height + pad * 2),
            (255, 255, 255, 255),
        )
        canvas.paste(img, (pad, pad))
        img = canvas

    w, h = img.size
    if h > max_height:
        nw = max(1, int(w * max_height / h))
        img = img.resize((nw, max_height), Image.Resampling.LANCZOS)

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for filename, spec in LOGOS.items():
        dest = OUT / filename
        data = normalize(
            download(spec["url"]),
            max_height=spec["max_height"],
            white_pad=spec["white_pad"],
            max_width=spec.get("max_width"),
        )
        dest.write_bytes(data)
        print(f"  wrote {dest.relative_to(ROOT)} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
