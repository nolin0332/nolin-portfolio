from pathlib import Path

js = Path("public/_astro/hoisted.jm-mpcuc8bi.js").read_text(encoding="utf-8")
for term in [
    "scroll-indicator-bar",
    "domScrollIndicatorBar",
    "scrollIndicatorActiveRatio",
    "class Loader",
    "hasStarted",
    "properties.hasStarted",
    "--jlp",
    "julio-loader",
    "loadProgress",
    "footer-hero-button",
]:
    i = js.find(term)
    if i >= 0:
        print("===", term, "===")
        print(js[max(0, i - 80) : i + 400])
        print()
