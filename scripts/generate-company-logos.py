#!/usr/bin/env python3
"""Fetch real company logos (alias for fetch-company-logos.py)."""

from __future__ import annotations

import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("fetch-company-logos.py")), run_name="__main__")
