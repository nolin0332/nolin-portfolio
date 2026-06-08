from pathlib import Path

h = Path("public/index.html").read_text(encoding="utf-8")
start = h.find('id="story-rewards-referral"')
end = h.find('id="story-rewards-cashback"')
print(h[start:end])
