#!/usr/bin/env python3
"""Install user-provided HQ skill logos into public/assets/logos/."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Local folder holding the original high-resolution logo downloads.
ASSETS = ROOT / "assets-src"
OUT = ROOT / "public" / "assets" / "logos"

# Order: Python, PyTorch, AWS, LLM, Azure AI, MLOps
HQ_SOURCES = {
    "python": "image-53ee3fc1-d51c-43d1-8436-7a900133f7a4.png",
    "pytorch": "image-157b2e81-6085-4e3f-8081-fee7aa158460.png",
    "aws": "image-1b6f2dbd-d781-4088-bd80-ff60c00e456c.png",
    "rag": "image-1680c385-3fd5-4cef-9a24-e5cd466d7e07.png",
    "azure-ai": "image-7054b1a6-e20c-4d5d-859e-cd127fc81427.png",
    "aws-mlops": "image-4f0ad015-8741-481c-baa3-d3cb4419e834.png",
}


def find_source(filename: str) -> Path:
    matches = list(ASSETS.glob(f"*{filename}"))
    if matches:
        return matches[0]
    raise FileNotFoundError(f"Missing HQ logo: {filename}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for key, filename in HQ_SOURCES.items():
        src = find_source(filename)
        dest = OUT / f"{key}.png"
        shutil.copy2(src, dest)
        print(f"  {key}.png <- {src.name}")
    print("Done.")


if __name__ == "__main__":
    main()
