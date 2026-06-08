import re

h = open("public/index.html", encoding="utf-8").read()

sections = [
    ("story-gamification-hero", "story-gamification-battle-pass"),
    ("story-gamification-leaderboard", "story-gamification-leaderboard-content-wrapper"),
    ("story-airdrops-post-seasons", "story-airdrops-post-seasons-list"),
    ("story-airdrops-pre-end", "footer"),
]

for sid, end_marker in sections:
    start = h.find(f'id="{sid}"')
    if start < 0:
        print("MISSING", sid)
        continue
    if end_marker == "footer":
        end = start + 2000
    else:
        end = h.find(f'id="{end_marker}"', start + 10)
        if end < 0:
            end = start + 2000
    print("\n===", sid, "===\n", h[start:end][:1200])
