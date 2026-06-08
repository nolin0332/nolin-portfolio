#!/usr/bin/env python3
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
h = (Path(__file__).resolve().parents[1] / "public" / "index.html").read_text(encoding="utf-8")
for eid in [
    "story-gamification-quests-quest-number",
    "story-gamification-quests-quest-desc",
    "story-gamification-quests-points",
    "story-gamification-quests-counter-1",
    "story-gamification-quests-counter-2",
    "story-gamification-quests-counter-3",
    "story-airdrops-post-seasons-title",
    "end-hero",
]:
    m = re.search(rf'id="{eid}"[^>]*>(.*?)(?=</)', h, re.DOTALL)
    print(eid, ":", re.sub(r"\s+", " ", (m.group(1) if m else "MISSING")[:120]))
