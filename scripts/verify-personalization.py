#!/usr/bin/env python3
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

h = open("public/index.html", encoding="utf-8").read()

errors = []
for bad in [
    r"<h1[^>]*>[^<]*</div>",
    r"<h2[^>]*>[^<]*</div>",
    r"<h4[^>]*>[^<]*</div>",
]:
    if re.search(bad, h):
        errors.append(f"broken tag pattern: {bad}")

print("title:", re.search(r"<title>([^<]+)", h).group(1))
print("HTML integrity:", "OK" if not errors else errors)

checks = {
    "story-gamification-hero": ("AI / ML", "12+ years building production LLM"),
    "story-gamification-leaderboard": ("Top Skills", "Python, RAG/LLM engineering"),
    "story-rewards-referral": ("Healthcare RAG", "LangChain"),
    "story-gamification-quests-quest-number": ("Python", None),
    "end-hero": ("Let's", "michael.trent039@gmail.com"),
}

for sid, (need_title, need_desc) in checks.items():
    if sid.startswith("story-"):
        m = re.search(
            rf'id="{sid}".*?story-feature-title">([^<]+(?:<[^>]+>[^<]*)*)',
            h,
            re.DOTALL,
        )
        title = re.sub(r"<[^>]+>", " ", m.group(1)).strip() if m else None
    else:
        title = None
    if sid.endswith("quest-number"):
        m = re.search(rf'id="{sid}"[^>]*>([^<]+)', h)
        title = m.group(1).strip() if m else None
    if sid == "end-hero":
        m = re.search(r'id="end-hero".*?story-feature-title">([^<]+)', h, re.DOTALL)
        title = m.group(1).strip() if m else None
        m2 = re.search(r'id="end-hero".*?story-feature-desc">(.{0,200})', h, re.DOTALL)
        desc = m2.group(1) if m2 else ""
    else:
        m2 = re.search(
            rf'id="{sid}".*?story-feature-desc">(.{{0,160}})',
            h,
            re.DOTALL,
        )
        desc = re.sub(r"<[^>]+>", " ", m2.group(1)).strip() if m2 else ""

    ok = (not need_title or (title and need_title in title)) and (
        not need_desc or need_desc in desc
    )
    print(f"{sid}: {'OK' if ok else 'FAIL'} | {title or '-'} | {desc[:80] if desc else '-'}")

js = open("public/_astro/hoisted.jm-mpcuc8bi.js", encoding="utf-8").read()
print("NAMES", re.search(r"NAMES=(\[[^\]]+\])", js).group(1))
print("SEASONS", re.search(r"getHTMLCard\((\[[^\]]+\])\[o\]", js).group(1)[:120])
