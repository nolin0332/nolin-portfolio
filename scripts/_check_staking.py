import re
from pathlib import Path

h = Path("public/index.html").read_text(encoding="utf-8")
idx = h.find('id="story-rewards-staking"')
chunk = h[idx : idx + 3000]
m = re.search(r"story-feature-list bullet-list\">(.*)</div> </div>", chunk, re.DOTALL)
if m:
    bullets = re.findall(r"<div>(.*?)</div>", m.group(1))
    print("staking bullets:", len(bullets))
    for b in bullets:
        print("-", b[:90])
