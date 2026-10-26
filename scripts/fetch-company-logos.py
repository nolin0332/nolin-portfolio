#!/usr/bin/env python3
"""Download real company logos for experience/education slides.

Logos come from Wikimedia Commons (rendered as PNG via ?width=) or a site
favicon. Companies without a public logo get a clean typographic wordmark
rendered with the site font so nothing is misrepresented.
"""

from __future__ import annotations

import urllib.request
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "assets" / "logos" / "companies"
FONT = ROOT / "public" / "assets" / "fonts" / "Aptos-Bold.ttf"
USER_AGENT = (
    "Mozilla/5.0 (compatible; PortfolioLogoFetcher/1.0; +https://localhost)"
)

COMMONS = "https://commons.wikimedia.org/wiki/Special:FilePath/"

LOGOS = {
    # Small companies without a public vector logo -> rendered wordmark.
    "novawave.png": {"wordmark": "Novawave", "color": (31, 78, 160), "max_height": 56},
    "larynx.png": {"wordmark": "Larynx", "color": (20, 20, 20), "max_height": 56},
    "nextera.png": {
        "url": COMMONS + "NextEra_Energy_logo_(1).svg?width=600",
        "max_height": 56,
        "white_pad": True,
        "max_width": 260,
    },
    # datexcorp.com — Datex Corporation (FootPrint WMS), Clearwater FL.
    "datex.png": {
        "url": "https://www.google.com/s2/favicons?domain=datexcorp.com&sz=128",
        "max_height": 56,
        "white_pad": True,
    },
    "fis.png": {
        "url": COMMONS + "FIS_logo.svg?width=600",
        "max_height": 56,
        "white_pad": True,
        "max_width": 200,
    },
    "microsoft.png": {
        "url": COMMONS + "Microsoft_logo_(2012).svg?width=600",
        "max_height": 48,
        "white_pad": True,
        "max_width": 260,
    },
    "google.png": {
        "url": COMMONS + "Google_2015_logo.svg?width=600",
        "max_height": 48,
        "white_pad": True,
        "max_width": 200,
    },
    "uw.png": {
        "url": COMMONS + "University_of_Washington_signature.svg?width=600",
        "max_height": 56,
        "white_pad": True,
        "max_width": 300,
    },
}


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def normalize(
    data: bytes, *, max_height: int, white_pad: bool, max_width: int | None
) -> bytes:
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


def wordmark(text: str, color: tuple[int, int, int], max_height: int) -> bytes:
    from PIL import Image, ImageDraw, ImageFont

    scale = 4
    size = max_height * scale
    font = ImageFont.truetype(str(FONT), int(size * 0.62))
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bbox = probe.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = int(size * 0.22)
    img = Image.new("RGBA", (tw + pad * 2, size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((pad - bbox[0], (size - th) // 2 - bbox[1]), text, font=font, fill=color + (255,))
    img = img.resize((img.width // scale, max_height), Image.Resampling.LANCZOS)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for filename, spec in LOGOS.items():
        dest = OUT / filename
        if "wordmark" in spec:
            data = wordmark(spec["wordmark"], spec["color"], spec["max_height"])
        else:
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
