#!/usr/bin/env python3

"""Personalize portfolio from scripts/resume-profile.json."""

from __future__ import annotations



import json

import re

from html import escape as html_escape

import subprocess

from pathlib import Path



ROOT = Path(__file__).resolve().parents[1]

INDEX = ROOT / "public" / "index.html"

REFERENCE = ROOT / "public" / "index.reference.html"

HOISTED = ROOT / "public" / "_astro" / "hoisted.jm-mpcuc8bi.js"

MANIFEST = ROOT / "public" / "favicon" / "site.webmanifest"

PACKAGE = ROOT / "package.json"

README = ROOT / "README.md"

PROFILE_PATH = ROOT / "scripts" / "resume-profile.json"

OVERRIDES = ROOT / "scripts" / "julio-overrides.css"



TITLE_RE = re.compile(

    r'(<(?:h1|h2)[^>]*class="story-feature-title"[^>]*>)(.*?)(</(?:h1|h2)>)',

    re.DOTALL,

)

DESC_RE = re.compile(

    r'(<h4[^>]*class="story-feature-desc"[^>]*>)(.*?)(</h4>)',

    re.DOTALL,

)





def load_profile() -> dict:

    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))





def section_slice(html: str, section_id: str, max_len: int = 12000) -> tuple[str, int, int] | None:

    marker = f'id="{section_id}"'

    start = html.find(marker)

    if start < 0:

        return None

    child_prefix = f"{section_id}-"

    pos = start + len(marker)

    end = min(len(html), start + max_len)

    while True:

        next_story = html.find('id="story-', pos)

        if next_story < 0:

            break

        id_end = html.find('"', next_story + 4)

        next_id = html[next_story + 4 : id_end]

        if next_id != section_id and not next_id.startswith(child_prefix):

            end = next_story

            break

        pos = next_story + 10

    return html[start:end], start, end





def patch_section(html: str, section_id: str, replacers: list[tuple[re.Pattern[str], str]]) -> str:

    sliced = section_slice(html, section_id)

    if not sliced:

        print(f"  WARN missing section {section_id}")

        return html

    chunk, start, end = sliced

    original = chunk

    for pattern, replacement in replacers:

        chunk, count = pattern.subn(replacement, chunk, count=1)

        if count == 0:

            print(f"  WARN no match in {section_id}: {pattern.pattern[:60]}")

    if chunk != original:

        print(f"  section {section_id}")

    return html[:start] + chunk + html[end:]





def set_title(html: str, section_id: str, title_html: str) -> str:
    return patch_section(
        html,
        section_id,
        [
            (
                TITLE_RE,
                lambda m, t=title_html: f"{m.group(1)}{t}{m.group(3)}",
            )
        ],
    )


def set_desc(html: str, section_id: str, desc_html: str) -> str:
    return patch_section(
        html,
        section_id,
        [
            (
                DESC_RE,
                lambda m, d=desc_html: f"{m.group(1)}{d}{m.group(3)}",
            )
        ],
    )





def set_element_text(html: str, element_id: str, text: str) -> str:
    pattern = re.compile(
        rf'(<[^>]*\bid="{re.escape(element_id)}"[^>]*>)([^<]*)(</)',
        re.DOTALL,
    )

    def repl(m: re.Match[str]) -> str:
        return f"{m.group(1)}{text}{m.group(3)}"

    new_html, count = pattern.subn(repl, html, count=1)

    if count:

        print(f"  element {element_id}")

    else:

        print(f"  WARN missing element {element_id}")

    return new_html





def replace_div_inner(html: str, section_id: str, marker: str, inner_html: str) -> str:
    sliced = section_slice(html, section_id)
    if not sliced:
        print(f"  WARN missing section {section_id} for {marker}")
        return html

    chunk, start, end = sliced
    pos = chunk.find(marker)
    if pos < 0:
        print(f"  WARN missing {marker} in {section_id}")
        return html

    inner_start = pos + len(marker)
    depth = 1
    i = inner_start
    close_pos = -1
    while i < len(chunk):
        if chunk.startswith("<div", i):
            depth += 1
            gt = chunk.find(">", i)
            i = (gt + 1) if gt >= 0 else (i + 1)
        elif chunk.startswith("</div>", i):
            depth -= 1
            if depth == 0:
                close_pos = i
                break
            i += 6
        else:
            i += 1

    if close_pos < 0:
        print(f"  WARN could not close {marker} in {section_id}")
        return html

    new_chunk = chunk[:inner_start] + inner_html + chunk[close_pos:]
    print(f"  list {section_id}")
    return html[:start] + new_chunk + html[end:]


def set_xp_list(html: str, items: list[str]) -> str:
    items_html = "".join(f"<div>{item}</div>" for item in items)
    return replace_div_inner(
        html,
        "story-gamification-xp",
        '<div class="story-feature-list bullet-list">',
        items_html,
    )


def set_bullet_list(html: str, section_id: str, items: list[str]) -> str:
    items_html = "".join(f"<div>{item}</div>" for item in items)
    return replace_div_inner(
        html,
        section_id,
        '<div class="story-feature-list bullet-list">',
        items_html,
    )


def ensure_bullet_list(html: str, section_id: str, items: list[str]) -> str:
    sliced = section_slice(html, section_id)
    if not sliced:
        return html
    chunk, start, end = sliced
    if "story-feature-list" in chunk:
        return set_bullet_list(html, section_id, items)
    items_html = "".join(f"<div>{item}</div>" for item in items)
    block = f'<div class="story-feature-list bullet-list">{items_html}</div>'
    new_chunk, count = re.subn(r"(</h4>)", rf"\1 {block}", chunk, count=1)
    if count:
        print(f"  added bullets {section_id}")
        return html[:start] + new_chunk + html[end:]
    print(f"  WARN could not add bullets in {section_id}")
    return html


EXPERIENCE_SECTIONS = frozenset(
    {
        "story-rewards-hero",
        "story-rewards-referral",
        "story-rewards-cashback",
        "story-rewards-staking",
        "story-rewards-community",
    }
)

EXPERIENCE_BULLET_SECTIONS = frozenset(
    {
        "story-rewards-referral",
        "story-rewards-cashback",
        "story-rewards-staking",
    }
)

EDUCATION_SECTIONS = frozenset(
    {
        "story-airdrops-pre-hero",
        "story-airdrops-pre-engagement",
    }
)


def experience_desc(section_id: str, content: dict) -> str:
    chips = " · ".join(content["metaChips"]) if content.get("metaChips") else ""
    desc = content.get("descHtml", "")
    bullets = content.get("bullets", [])

    if section_id == "story-rewards-hero":
        return chips or desc

    if section_id in EXPERIENCE_BULLET_SECTIONS:
        return chips or desc

    parts = [p for p in [chips, desc] if p]
    return "<br>".join(parts) if len(parts) > 1 else (parts[0] if parts else "")


def restore_experience_shell(html: str, section_id: str) -> str:
    if not REFERENCE.exists():
        print(f"  WARN missing reference html for {section_id}")
        return html
    ref_html = REFERENCE.read_text(encoding="utf-8")
    ref_slice = section_slice(ref_html, section_id)
    cur_slice = section_slice(html, section_id)
    if not ref_slice or not cur_slice:
        print(f"  WARN could not restore shell {section_id}")
        return html
    ref_chunk, _, _ = ref_slice
    _, start, end = cur_slice
    print(f"  restore experience shell {section_id}")
    return html[:start] + ref_chunk + html[end:]


def inject_experience_meta(html: str, section_id: str, chips: list[str]) -> str:
    sliced = section_slice(html, section_id)
    if not sliced:
        return html
    chunk, start, end = sliced
    chips_html = "".join(
        f'<span class="exp-meta-chip">{chip}</span>' for chip in chips
    )
    block = f'<div class="exp-meta">{chips_html}</div>'
    chunk = _remove_balanced_div_block(chunk, '<div class="exp-meta">')
    new_chunk, count = re.subn(
        r"(</(?:h1|h2)>)",
        rf"\1 {block}",
        chunk,
        count=1,
    )
    if count:
        print(f"  experience meta {section_id}")
        return html[:start] + new_chunk + html[end:]
    print(f"  WARN could not inject meta in {section_id}")
    return html


def wrap_experience_panel(html: str, section_id: str) -> str:
    sliced = section_slice(html, section_id)
    if not sliced:
        return html
    chunk, start, end = sliced
    if "exp-panel" in chunk:
        return html
    new_chunk = chunk
    if section_id == "story-rewards-hero":
        new_chunk = re.sub(
            r'(<img class="exp-company-logo"[^>]*>)',
            r'<div class="exp-panel exp-panel--hero">\1',
            chunk,
            count=1,
        )
        new_chunk = new_chunk.replace(
            '<div class="scroll-down-cta"',
            '</div> <div class="scroll-down-cta"',
            1,
        )
    elif '<div class="story-feature-content"> <div>' in chunk:
        new_chunk = chunk.replace(
            '<div class="story-feature-content"> <div>',
            '<div class="story-feature-content"> <div class="exp-panel">',
            1,
        )
    else:
        new_chunk = re.sub(
            r'(<img class="exp-company-logo"[^>]*>)',
            r'<div class="exp-panel">\1',
            chunk,
            count=1,
        )
        for anchor in (
            '<img class="story-feature-image-shadow"',
            '<div class="scroll-down-cta"',
        ):
            if anchor in new_chunk:
                new_chunk = new_chunk.replace(anchor, f"</div> {anchor}", 1)
                break
    if new_chunk != chunk:
        print(f"  experience panel {section_id}")
        return html[:start] + new_chunk + html[end:]
    print(f"  WARN could not wrap panel in {section_id}")
    return html


def format_edu_card(item: dict) -> str:
    logo = item.get("logo", "")
    school = item.get("school", "")
    img = ""
    if logo:
        src = f"assets/logos/companies/{logo}"
        img = f'<img class="edu-logo" src="{src}" alt="{school}" loading="lazy">'
    badge = ""
    if item.get("badge"):
        badge = f'<span class="edu-badge">{item["badge"]}</span>'
    return (
        '<div class="edu-card">'
        f"{img}"
        '<div class="edu-card-body">'
        f'<div class="edu-school">{school}</div>'
        f'<div class="edu-degree">{item.get("degree", "")}</div>'
        f'<div class="edu-years">{item.get("years", "")}{badge}</div>'
        "</div></div>"
    )


def _remove_balanced_div_block(chunk: str, marker: str) -> str:
    pos = chunk.find(marker)
    if pos < 0:
        return chunk
    inner_start = pos + len(marker)
    depth = 1
    i = inner_start
    while i < len(chunk):
        if chunk.startswith("<div", i):
            depth += 1
            gt = chunk.find(">", i)
            i = (gt + 1) if gt >= 0 else (i + 1)
        elif chunk.startswith("</div>", i):
            depth -= 1
            if depth == 0:
                tail = i + 6
                while tail < len(chunk) and chunk[tail] in " \t\n\r":
                    tail += 1
                return chunk[:pos] + chunk[tail:]
            i += 6
        else:
            i += 1
    return chunk


def inject_education_timeline(
    html: str, section_id: str, items: list[dict]
) -> str:
    sliced = section_slice(html, section_id)
    if not sliced:
        return html
    chunk, start, end = sliced
    cards = "".join(format_edu_card(item) for item in items)
    block = f'<div class="edu-timeline">{cards}</div>'
    chunk = _remove_balanced_div_block(
        chunk, '<div class="edu-timeline">'
    )
    if "</h4>" in chunk:
        new_chunk = chunk.replace("</h4>", f"</h4> {block}", 1)
    elif "</h1>" in chunk or "</h2>" in chunk:
        new_chunk, count = re.subn(
            r"(</(?:h1|h2)>)",
            rf"\1 {block}",
            chunk,
            count=1,
        )
        if not count:
            print(f"  WARN could not inject education in {section_id}")
            return html
    else:
        print(f"  WARN could not inject education in {section_id}")
        return html
    if new_chunk != chunk:
        print(f"  education timeline {section_id}")
    return html[:start] + new_chunk + html[end:]


def strip_all_experience_achievements(html: str) -> str:
    new_html = re.sub(
        r'<p class="exp-achievement">.*?</p>\s*',
        "",
        html,
        flags=re.DOTALL,
    )
    if new_html != html:
        print("  stripped all exp-achievement blocks")
    return new_html


def inject_experience_logo(
    html: str, section_id: str, logo_file: str, alt: str
) -> str:
    sliced = section_slice(html, section_id)
    if not sliced:
        return html
    chunk, start, end = sliced
    src = f"assets/logos/companies/{logo_file}"
    img = (
        f'<img class="exp-company-logo" src="{src}" alt="{alt}" loading="lazy">'
    )
    if "exp-company-logo" in chunk:
        new_chunk = re.sub(
            r'<img class="exp-company-logo"[^>]*>',
            img,
            chunk,
            count=1,
        )
    elif section_id == "story-rewards-hero":
        new_chunk = re.sub(
            r'(<div class="story-feature-chapter">[^<]*</div>)\s*',
            rf"\1 {img} ",
            chunk,
            count=1,
        )
    elif re.search(
        r'<div class="story-feature-content">\s*<div>',
        chunk,
    ):
        new_chunk = re.sub(
            r'(<div class="story-feature-content">\s*<div>)',
            rf"\1{img}",
            chunk,
            count=1,
        )
    else:
        new_chunk = re.sub(
            r'(<div class="story-feature-content">)\s*',
            rf"\1 {img} ",
            chunk,
            count=1,
        )
    if new_chunk != chunk:
        print(f"  logo {section_id}")
    return html[:start] + new_chunk + html[end:]


def strip_experience_achievement(html: str, section_id: str) -> str:
    sliced = section_slice(html, section_id)
    if not sliced:
        return html
    chunk, start, end = sliced
    new_chunk = re.sub(
        r'<p class="exp-achievement">.*?</p>\s*',
        "",
        chunk,
        count=1,
        flags=re.DOTALL,
    )
    if new_chunk != chunk:
        print(f"  removed achievement {section_id}")
    return html[:start] + new_chunk + html[end:]


def inject_experience_achievement(
    html: str, section_id: str, achievement_html: str
) -> str:
    sliced = section_slice(html, section_id)
    if not sliced:
        return html
    chunk, start, end = sliced
    block = (
        '<p class="exp-achievement"><span class="exp-achievement-label">'
        f"Proudest achievement</span>{achievement_html}</p>"
    )
    chunk = re.sub(
        r'<p class="exp-achievement">.*?</p>\s*',
        "",
        chunk,
        count=1,
        flags=re.DOTALL,
    )
    if '<div class="scroll-down-cta">' in chunk:
        new_chunk = chunk.replace(
            '<div class="scroll-down-cta">',
            f"{block} <div class=\"scroll-down-cta\">",
            1,
        )
    elif '<img class="story-feature-image-shadow"' in chunk:
        new_chunk = chunk.replace(
            '<img class="story-feature-image-shadow"',
            f"{block} <img class=\"story-feature-image-shadow\"",
            1,
        )
    elif "</div> </div> </div> <div" in chunk:
        new_chunk = chunk.replace(
            "</div> </div> </div> <div",
            f"{block} </div> </div> </div> <div",
            1,
        )
    else:
        new_chunk = re.sub(
            r"(</h4>)",
            rf"\1 {block}",
            chunk,
            count=1,
        )
    if new_chunk != chunk:
        print(f"  achievement {section_id}")
    return html[:start] + new_chunk + html[end:]


def set_skills_cats(html: str, categories: list[dict[str, str]]) -> str:
    marker = '<div class="skills-cats">'
    start = html.find(marker)
    if start < 0:
        print("  WARN skills-cats missing")
        return html

    inner_start = start + len(marker)
    depth = 1
    i = inner_start
    end = -1
    while i < len(html):
        if html.startswith("<div", i):
            depth += 1
            gt = html.find(">", i)
            i = (gt + 1) if gt >= 0 else (i + 1)
        elif html.startswith("</div>", i):
            depth -= 1
            if depth == 0:
                end = i
                break
            i += 6
        else:
            i += 1

    if end < 0:
        print("  WARN skills-cats closing tag not found")
        return html

    inner = "".join(
        '<div class="skill-cat">'
        f'<span class="sc-label">{cat["label"]}</span>'
        f'<span class="sc-items">{cat["items"]}</span>'
        "</div>"
        for cat in categories
    )
    print("  skills-cats")
    return html[:inner_start] + inner + html[end:]


CONTACT_FORM_MARKER = 'id="contact-form"'
CONTACT_SCRIPT_MARKER = "contact-form.js"
JOTFORM_SCRIPT_MARKER = "jotform-agent.js"
CONTACT_LAYOUT_MARKER = 'class="contact-layout"'

EMAIL_ICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4-8 5-8-5V6l8 5 8-5v2z"/>'
    "</svg>"
)
LINKEDIN_ICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 114.126 0 2.063 2.063 0 01-2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>'
    "</svg>"
)
PHONE_ICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M6.62 10.79a15.05 15.05 0 006.59 6.59l2.2-2.2a1 1 0 011.01-.24c1.12.37 2.33.57 3.58.57a1 1 0 011 1V20a1 1 0 01-1 1C10.07 21 3 13.93 3 5a1 1 0 011-1h3.5a1 1 0 011 1c0 1.25.2 2.46.57 3.58a1 1 0 01-.24 1.01l-2.2 2.2z"/>'
    "</svg>"
)


def contact_form_html(
    email: str, web3_key: str = "", formsubmit_id: str = ""
) -> str:
    web3_attr = html_escape(web3_key) if web3_key else ""
    formsubmit_attr = html_escape(formsubmit_id) if formsubmit_id else ""
    return (
        f'<form id="contact-form" class="contact-form" data-recipient="{email}" '
        f'data-web3-key="{web3_attr}" data-formsubmit-id="{formsubmit_attr}" novalidate>'
        '<div class="contact-field">'
        '<label class="contact-label" for="contact-name">Your name</label>'
        '<input id="contact-name" name="name" type="text" autocomplete="name" '
        'placeholder="John Smith" required>'
        "</div>"
        '<div class="contact-field">'
        '<label class="contact-label" for="contact-email">Your email</label>'
        '<input id="contact-email" name="email" type="email" autocomplete="email" '
        'placeholder="you@example.com" required>'
        "</div>"
        '<div class="contact-field">'
        '<label class="contact-label" for="contact-message">Your message</label>'
        '<textarea id="contact-message" name="message" rows="5" '
        'placeholder="How can I help?" required></textarea>'
        "</div>"
        '<button type="submit" id="contact-submit" class="contact-submit">'
        "Send message</button>"
        '<p id="contact-form-status" class="contact-form-status" aria-live="polite">'
        "</p></form>"
    )


CONTACT_BUTTON_STUB = (
    '<button type="button" id="end-hero-button" class="contact-cta-stub" '
    'hidden aria-hidden="true" tabindex="-1">'
    '<div id="end-hero-button-bg"></div>'
    '<div id="end-hero-button-front">'
    '<span class="button-text-wrapper">'
    '<span class="button-text-01">CONTACT</span></span>'
    '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" '
    'viewbox="0 0 20 20" fill="none">'
    '<rect x="0" y="0" width="20" height="20" rx="10" fill="#FF421B"></rect>'
    '<path class="button-arrow-01" d="M7,13l6-6 M13,7H8.108 M13,7v4.892" '
    'stroke="white" stroke-width="1.5" stroke-linecap="round" '
    'stroke-linejoin="round"></path>'
    '<path class="button-arrow-02" d="M7,13l6-6 M13,7H8.108 M13,7v4.892" '
    'stroke="white" stroke-width="1.5" stroke-linecap="round" '
    'stroke-linejoin="round"></path></svg></div></button>'
)


def ensure_contact_button_stub(html: str) -> str:
    if 'id="end-hero-button"' in html:
        html, count = re.subn(
            r'<(?:a|button)[^>]*id="end-hero-button"[^>]*>.*?</(?:a|button)>',
            CONTACT_BUTTON_STUB,
            html,
            count=1,
            flags=re.DOTALL,
        )
        if count:
            print("  contact CTA stub ensured")
        return html

    if 'id="end-hero-ext-links"' in html:
        html = html.replace(
            'id="end-hero-ext-links"',
            f"{CONTACT_BUTTON_STUB} id=\"end-hero-ext-links\"",
            1,
        )
        print("  contact CTA stub injected")
        return html

    html = html.replace("</form>", f"</form> {CONTACT_BUTTON_STUB}", 1)
    print("  contact CTA stub after form")
    return html


def inject_contact_form(
    html: str, email: str, web3_key: str = "", formsubmit_id: str = ""
) -> str:
    form_block = contact_form_html(email, web3_key, formsubmit_id)

    if CONTACT_FORM_MARKER in html:
        html, count = re.subn(
            r'<form id="contact-form"[^>]*>.*?</form>',
            form_block,
            html,
            count=1,
            flags=re.DOTALL,
        )
        if count:
            print("  contact form updated")
    else:
        pattern = re.compile(
            r'(id="end-hero"[^>]*>.*?<h4[^>]*class="story-feature-desc"[^>]*>.*?</h4>)',
            re.DOTALL,
        )
        html, count = pattern.subn(rf"\1 {form_block}", html, count=1)
        if count:
            print("  contact form injected")
        else:
            print("  WARN could not inject contact form")

    return ensure_contact_button_stub(html)


def inject_contact_script(html: str) -> str:
    tag = '<script src="contact-form.js" defer></script>'
    if CONTACT_SCRIPT_MARKER in html:
        return html
    if "</body>" in html:
        html = html.replace("</body>", f"{tag}</body>", 1)
        print("  contact-form.js script")
    return html


def inject_jotform_agent_script(html: str) -> str:
    tag = '<script src="jotform-agent.js" defer></script>'
    if JOTFORM_SCRIPT_MARKER in html:
        return html
    if "</body>" in html:
        html = html.replace("</body>", f"{tag}</body>", 1)
        print("  jotform-agent.js script")
    return html


def build_contact_info_html(profile: dict) -> str:
    p = profile["profile"]
    email = html_escape(p["email"])
    phone = html_escape(p["phone"])
    linkedin = html_escape(p["linkedin"])
    phone_tel = re.sub(r"[^\d+]", "", p["phone"])

    return (
        '<div class="contact-info">'
        '<p class="contact-info-heading">Contact</p>'
        f'<a href="mailto:{email}" class="contact-info-item" '
        f'aria-label="Email" title="{email}">'
        f'<span class="contact-info-icon">{EMAIL_ICON_SVG}</span>'
        f'<span class="contact-info-text">{email}</span></a>'
        f'<a href="tel:{phone_tel}" class="contact-info-item" '
        f'aria-label="Phone" title="{phone}">'
        f'<span class="contact-info-icon">{PHONE_ICON_SVG}</span>'
        f'<span class="contact-info-text">{phone}</span></a>'
        f'<a href="{linkedin}" class="contact-info-item" target="_blank" '
        'rel="noopener noreferrer" aria-label="LinkedIn" title="LinkedIn">'
        f'<span class="contact-info-icon">{LINKEDIN_ICON_SVG}</span>'
        '<span class="contact-info-text">LinkedIn</span></a>'
        "</div>"
    )


def restructure_end_hero_layout(html: str, profile: dict) -> str:
    contact_info = build_contact_info_html(profile)

    if CONTACT_LAYOUT_MARKER in html:
        html, count = re.subn(
            r'<div class="contact-info">.*?</div>\s*(<form id="contact-form")',
            f"{contact_info} \\1",
            html,
            count=1,
            flags=re.DOTALL,
        )
        if count:
            print("  end-hero contact info updated")
        return html

    pattern = re.compile(
        r'(<div id="end-hero"[^>]*>\s*<div class="story-feature-content">)\s*'
        r'(<h1 class="story-feature-title">.*?</h1>)\s*'
        r'(<h4 class="story-feature-desc">.*?</h4>)\s*'
        r'(<form id="contact-form"[^>]*>.*?</form>)',
        re.DOTALL,
    )

    def wrap_end_hero(match: re.Match[str]) -> str:
        return (
            f'{match.group(1)}<div class="contact-layout">'
            f'<div class="contact-col contact-col-left">'
            f"{match.group(2)}{match.group(3)}"
            "</div>"
            f'<div class="contact-col contact-col-right">'
            f"{contact_info}{match.group(4)}"
            "</div></div>"
        )

    html, count = pattern.subn(wrap_end_hero, html, count=1)
    if count:
        print("  end-hero split layout")
    else:
        print("  WARN could not restructure end-hero layout")
    return html


def fix_footer_email_links(html: str, email: str) -> str:
    email_link = f'<a href="mailto:{email}">Email</a>'
    for container_id in ("menu-mobile__service-links", "footer-right"):
        pattern = re.compile(
            rf'(<div id="{container_id}">\s*)<a[^>]*>[^<]*</a>',
            re.DOTALL,
        )
        html, count = pattern.subn(rf"\1{email_link}", html, count=1)
        if count:
            print(f"  footer link -> Email ({container_id})")
    return html


def apply_contact_details(html: str, profile: dict) -> str:
    p = profile["profile"]
    email = p["email"]
    phone = p["phone"]

    legacy_emails = (
        "michael.trent039@gmail.com",
        "michael.trent.dev@gmail.com",
        "pzscvserpw080@hotmail.com",
    )
    for old_email in legacy_emails:
        html = html.replace(old_email, email)

    legacy_phones = (
        "+1 (720) 358-1119",
        "+1 (972) 301 7727",
    )
    for old_phone in legacy_phones:
        html = html.replace(old_phone, phone)

    html = html.replace(
        'href="https://discord.com/users/1504060746160537782"',
        f'href="mailto:{email}"',
    )
    html = html.replace(">Discord</a>", ">Email</a>")
    html = fix_footer_email_links(html, email)

    contact_cfg = profile.get("contactForm", {})
    web3_key = contact_cfg.get("web3formsAccessKey", "")
    formsubmit_id = contact_cfg.get("formsubmitFormId", "")
    html = inject_contact_form(html, email, web3_key, formsubmit_id)
    html = restructure_end_hero_layout(html, profile)
    html = inject_contact_script(html)
    html = inject_jotform_agent_script(html)
    return html


def strip_referral_overrides(css: str) -> str:
    return re.sub(r"/\*REF-FINAL\*/.*?(?=/\*MOB-ALL\*/)", "", css, flags=re.DOTALL)


def strip_tools_overrides(css: str) -> str:
    return css


def inject_julio_overrides(html: str) -> str:
    if not OVERRIDES.exists():
        return html
    css = strip_referral_overrides(
        strip_tools_overrides(OVERRIDES.read_text(encoding="utf-8").strip())
    )
    html = re.sub(
        r"</script><style>/\* julio-overrides \*/.*?</style></head>",
        f"</script><style>/* julio-overrides */\n{css}\n</style></head>",
        html,
        count=1,
        flags=re.DOTALL,
    )
    if "julio-overrides" not in html:
        html = html.replace(
            "</head>",
            f'<style>/* julio-overrides */\n{css}\n</style></head>',
            1,
        )
    print("  julio-overrides CSS")
    return html


def set_pre_end_cards(html: str, cards: list[dict[str, str]]) -> str:
    sliced = section_slice(html, "story-airdrops-pre-end")
    if not sliced:
        print("  WARN missing story-airdrops-pre-end")
        return html
    chunk, start, end = sliced
    title_pat = re.compile(
        r'(<div class="story-airdrops-pre-end-title"[^>]*>)(.*?)(</div>)',
        re.DOTALL,
    )
    desc_pat = re.compile(
        r'(<div class="story-airdrops-pre-end-desc"[^>]*>)(.*?)(</div>)',
        re.DOTALL,
    )
    titles = title_pat.findall(chunk)
    descs = desc_pat.findall(chunk)
    if len(titles) < len(cards) or len(descs) < len(cards):
        print("  WARN pre-end card count mismatch")
        return html
    for i, card in enumerate(cards):
        old_t = titles[i]
        chunk = chunk.replace(
            f"{old_t[0]}{old_t[1]}{old_t[2]}",
            f"{old_t[0]}{card['titleHtml']}{old_t[2]}",
            1,
        )
        old_d = descs[i]
        chunk = chunk.replace(
            f"{old_d[0]}{old_d[1]}{old_d[2]}",
            f"{old_d[0]}{card['descHtml']}{old_d[2]}",
            1,
        )
    print("  pre-end cards")
    return html[:start] + chunk + html[end:]


def validate_html(html: str) -> bool:
    open_div = len(re.findall(r"<div[\s>]", html))
    close_div = html.count("</div>")
    ok = True
    if open_div != close_div:
        print(f"  ERROR div imbalance: {open_div} open vs {close_div} close")
        ok = False
    for required_id in (
        "story-airdrops-post-seasons-title",
        "story-airdrops-post-seasons-number-wrapper",
        "story-airdrops-post-seasons-list",
    ):
        if f'id="{required_id}"' not in html:
            print(f"  ERROR missing #{required_id}")
            ok = False
    return ok





def apply_index(profile: dict) -> None:

    p = profile["profile"]

    html = INDEX.read_text(encoding="utf-8")



    html = re.sub(

        r"<title>[^<]+</title>",

        f"<title>{p['name']} | {p['title']}</title>",

        html,

        count=1,

    )

    html = re.sub(
        r'<meta[^>]*name="description"[^>]*content="[^"]*"[^>]*>',
        f'<meta name="description" content="{p["tagline"]}">',
        html,
        count=1,
    )
    if 'name="description"' in html and p["tagline"] not in html[:3000]:
        html = re.sub(
            r'(<meta[^>]*name="description"[^>]*content=")[^"]*(")',
            rf"\1{p['tagline']}\2",
            html,
            count=1,
        )

    for meta_pat in (
        r'(<meta[^>]*property="og:description"[^>]*content=")[^"]*(")',
        r'(<meta[^>]*name="twitter:description"[^>]*content=")[^"]*(")',
        r'(<meta[^>]*property="og:title"[^>]*content=")[^"]*(")',
        r'(<meta[^>]*name="twitter:title"[^>]*content=")[^"]*(")',
        r'(<meta[^>]*property="og:site_name"[^>]*content=")[^"]*(")',
        r'(<meta[^>]*property="og:image:alt"[^>]*content=")[^"]*(")',
        r'(<meta[^>]*name="twitter:image:alt"[^>]*content=")[^"]*(")',
    ):
        repl = (
            rf"\1{p['tagline']}\2"
            if "description" in meta_pat
            else rf"\1{p['name']} | {p['title']}\2"
            if "title" in meta_pat or "site_name" in meta_pat
            else rf"\1{p['name']} — {p['title']}\2"
        )
        html = re.sub(meta_pat, repl, html, count=1)

    if "intro_hero" in profile:
        html = set_element_text(html, "intro-hero-title", profile["intro_hero"])

    nav_replacements = [

        ("Chapter 01: About", "Chapter 01 · About"),

        ("Chapter 01 · Skills", "Chapter 01 · About"),

        ("Chapter 02: Experience", "Chapter 02 · Experience"),

        ("Chapter 03: Skills", "Chapter 03 · Tools"),

        ("Chapter 03: Education", "Chapter 03 · Education"),

        ("Navigation", "Profile"),

        ("Gamification", "About"),

        ("Rewards", "Experience"),

        ("Airdrops", "Education"),

        ("Enter the Arena", "Explore My Work"),

        ("Join the Arena", "View Contact"),

        ("Let's Build<br>Something Great", profile["end_hero"]["titleHtml"]),

        (">CONNECT<", ">CONTACT<"),

    ]

    for old, new in nav_replacements:

        html = html.replace(old, new)



    for section_id in EXPERIENCE_SECTIONS:
        if section_id in profile.get("sections", {}):
            html = restore_experience_shell(html, section_id)

    if "story-airdrops-pre-engagement" in profile.get("sections", {}):
        html = restore_experience_shell(html, "story-airdrops-pre-engagement")

    hero_slice = section_slice(html, "story-rewards-hero")
    if hero_slice:
        hero_chunk, hero_start, hero_end = hero_slice
        hero_chunk = re.sub(
            r'(<div class="story-feature-chapter">)[^<]*(</div>)',
            r"\1Chapter 02: Experience\2",
            hero_chunk,
            count=1,
        )
        html = html[:hero_start] + hero_chunk + html[hero_end:]

    for section_id, content in profile["sections"].items():
        if section_id == "story-airdrops-post-seasons":
            if "titleHtml" in content:
                html = set_element_text(
                    html,
                    "story-airdrops-post-seasons-title",
                    content["titleHtml"],
                )
            if "descHtml" in content:
                html = set_desc(html, section_id, content["descHtml"])
            continue
        if section_id in EXPERIENCE_SECTIONS:
            if "titleHtml" in content:
                html = set_title(html, section_id, content["titleHtml"])
            html = set_desc(html, section_id, experience_desc(section_id, content))
            if (
                section_id in EXPERIENCE_BULLET_SECTIONS
                and content.get("bullets")
            ):
                html = ensure_bullet_list(html, section_id, content["bullets"])
            continue
        if "titleHtml" in content:
            html = set_title(html, section_id, content["titleHtml"])
        if "descHtml" in content:
            html = set_desc(html, section_id, content["descHtml"])
        if section_id in EDUCATION_SECTIONS and content.get("education"):
            html = inject_education_timeline(
                html, section_id, content["education"]
            )
        elif "bullets" in content:
            html = ensure_bullet_list(html, section_id, content["bullets"])



    quests = profile["quests"]

    html = set_element_text(html, "story-gamification-quests-quest-number", quests["number"])

    html = set_element_text(html, "story-gamification-quests-quest-desc", quests["desc"])

    html = set_element_text(html, "story-gamification-quests-points", quests["points"])



    xp = profile["xp"]

    html = set_title(html, "story-gamification-xp", xp["titleHtml"])

    html = set_xp_list(html, xp["items"])



    html = set_skills_cats(html, profile["skills_cats"])

    if "pre_end_cards" in profile:
        html = set_pre_end_cards(html, profile["pre_end_cards"])

    end = profile["end_hero"]

    html = set_title(html, "end-hero", end["titleHtml"])

    html = set_desc(html, "end-hero", end["descHtml"])

    html = apply_contact_details(html, profile)

    html = re.sub(
        r'(<span class="jl-name">)[^<]*(</span>)',
        rf'\1{p["name"]}\2',
        html,
        count=1,
    )
    html = re.sub(
        r'(<span class="jl-role">)[^<]*(</span>)',
        rf'\1{p["title"]}\2',
        html,
        count=1,
    )
    html = re.sub(
        r'© 2026 [^<]+',
        f'© 2026 {p["name"]} · {p["title"]}',
        html,
    )

    for legacy_name in (
        "Julio Membreno",
        "Michael Membreno",
        "Michael Trent",
        "Timothy Calder",
        "Ochsner Health",
        "Venture For America",
        "Camberline Technologies",
        "Boston University",
        "NewGen Strategies",
    ):
        html = html.replace(legacy_name, p["name"] if legacy_name in (
            "Julio Membreno", "Michael Membreno", "Michael Trent", "Timothy Calder"
        ) else {
            "Ochsner Health": "RedDress Medical",
            "Venture For America": "Silvifor",
            "Camberline Technologies": "Google",
            "Boston University": "Texas Tech University",
            "NewGen Strategies": "RedDress Medical",
        }[legacy_name])

    html = html.replace("Senior Software Engineer", p["title"])
    html = html.replace("Distributed Systems & Backend Platforms", "GenAI, RAG & Production ML")
    html = html.replace("Miami, FL", p["location"])
    html = html.replace("Denver, CO", p["location"])
    html = html.replace("Parker, CO", p["location"])
    html = html.replace("pzscvserpw080@hotmail.com", p["email"])
    html = html.replace(
        'href="https://discord.com/users/1504060746160537782"',
        f'href="mailto:{p["email"]}"',
    )
    html = html.replace(
        'content="https://discord.com/users/1504060746160537782"',
        f'content="mailto:{p["email"]}"',
    )

    html = strip_all_experience_achievements(html)

    html = inject_julio_overrides(html)

    if not validate_html(html):
        raise SystemExit("Personalization aborted: HTML structure validation failed")

    INDEX.write_text(html, encoding="utf-8")

    print(f"Updated {INDEX}")





HERO_UPDATE_TAIL = (
    "let S=-a.screenY;"
    "S+=math.fit(g+p,0,2,100,0,ease.cubicOut),"
    "S+=math.fit(_+w,0,2,0,-15,ease.cubicIn),"
    'this.domContent.style.transform=`translateY(${S}px)`,'
    'this.domContent.style.visibility=p>0?"visible":"hidden",'
    "storyRewardsReferralVisual.isActive=l>0&&u<1,"
    "storyRewardsReferralVisual.showRatio=l;"
    "let M=-math.fit(g+p,0,2,100,0,ease.cubicOut);"
    "M-=math.fit(_+w,0,2,0,-15,ease.cubicIn),"
    'this.domScrollIndicator.style.transform=`translate(-50%, ${M}px)`,'
    "this.domScrollIndicator.style.opacity=x*(1-w);"
    "for(let R=0;R<this.domScrollIndicatorPaths.length;R++){"
    "const P=this.domScrollIndicatorPaths[R],"
    "I=properties.time-P._delay,"
    "F=math.fit(I%1,0,.55,1,0);"
    'P.setAttribute("opacity",F)}'
    "coinsRainVisual.hideRatio=math.fit(this.domRange.hideScreenOffset,0,.3,0,1),"
    "coinsRainVisual.isActive=coinsRainVisual.isActive&&this.domRange.hideScreenOffset<.3"
)

REFERRAL_UPDATE_TAIL = (
    "let S=-a.screenY;"
    "S+=math.fit(v,0,2,0,-42,ease.cubicOut),"
    "S+=math.fit(_+w,0,2,0,-15,ease.cubicIn),"
    'this.domContent.style.transform=`translateY(${S}px)`,'
    'this.domContent.style.visibility=p>0?"visible":"hidden",'
    "storyRewardsReferralVisual.isActive=l>0&&u<1,"
    "storyRewardsReferralVisual.showRatio=l,"
    "storyRewardsReferralVisual.hideRatio=u,"
    "storyRewardsReferralVisual.showScreenOffset=this.domRange.showScreenOffset,"
    "storyRewardsReferralVisual.hideScreenOffset=this.domRange.hideScreenOffset,"
    "storyRewardsReferralVisual.ratio=this.domRange.ratio"
)

REFERRAL_PREINIT_CANONICAL = (
    'preInit(o){this.domContainer=o.querySelector("#story-rewards-referral"),'
    "this.domContent=this.domContainer.querySelector("
    '".story-feature-content"),this.domTitle=this.domContainer.querySelector('
    '".story-feature-title"),this.domDesc=this.domContainer.querySelector('
    '".story-feature-desc")}init(){}'
)


def repair_exp_bullet_slides(js: str) -> str:
    items_range_targets = (
        "ITEMS_RANGE=[[.75,1],[1.75,2],[2.75,3]]",
        "ITEMS_RANGE=[[.75,1],[1.75,2],[2.75,3],[3.75,4]]",
        "ITEMS_RANGE=[[.75,1.35],[1.75,2.35],[2.75,3.35],[3.35,4.75]]",
        "ITEMS_RANGE=[[.75,1.35],[1.75,2.35],[2.75,3.35],[3.2,5.5]]",
    )
    items_range_new = "ITEMS_RANGE=[[.55,1.05],[1.2,1.7],[1.85,2.45],[2.5,4.5]]"
    for old in items_range_targets:
        if old in js and old != items_range_new:
            js = js.replace(old, items_range_new, 1)
            print("  experience ITEMS_RANGE (4 bullets, wider)")
            break

    steps_init_old = (
        "stepsRatio=[{dom:0,visual:0},{dom:0,visual:0},{dom:0,visual:0}]"
    )
    steps_init_new = (
        "stepsRatio=[{dom:0,visual:0},{dom:0,visual:0},{dom:0,visual:0},{dom:0,visual:0}]"
    )
    if steps_init_old in js:
        js = js.replace(steps_init_old, steps_init_new, 1)
        print("  cashback stepsRatio (4 bullets)")

    steps_assign_old = (
        "this.stepsRatio[0].visual=math.fit(this.domRange.ratio,-.9,-.5,0,1),"
        "this.stepsRatio[0].dom=math.fit(this.domRange.ratio,-.9,-.5,0,1),"
        "this.stepsRatio[1].visual=this.stepsRatio[1].dom=math.fit(this.domRange.ratio,-.25,0,0,1),"
        "this.stepsRatio[2].visual=this.stepsRatio[2].dom=math.fit(this.domRange.ratio,.25,.5,0,1);"
        "for(let S=0;S<3;S++){const M=ease.cubicInOut(this.stepsRatio[S].dom),"
        "R=this.domListItems[S];"
        "R.style.transform=`translateY(${(1-M)*50}%)`,"
        "R.style.opacity=p*M}"
    )
    steps_assign_prev = (
        "this.stepsRatio[0].visual=math.fit(this.domRange.ratio,-.9,-.55,0,1),"
        "this.stepsRatio[0].dom=math.fit(this.domRange.ratio,-.9,-.55,0,1),"
        "this.stepsRatio[1].visual=this.stepsRatio[1].dom=math.fit(this.domRange.ratio,-.35,-.05,0,1),"
        "this.stepsRatio[2].visual=this.stepsRatio[2].dom=math.fit(this.domRange.ratio,.15,.45,0,1),"
        "this.stepsRatio[3].visual=this.stepsRatio[3].dom=math.fit(this.domRange.ratio,.55,.85,0,1);"
        "for(let S=0;S<this.domListItems.length;S++){const M=ease.cubicInOut("
        "(this.stepsRatio[S]||this.stepsRatio[this.stepsRatio.length-1]).dom),"
        "R=this.domListItems[S];"
        "R&&(R.style.transform=`translateY(${(1-M)*50}%)`,"
        "R.style.opacity=p*M)}"
    )
    steps_assign_new = (
        "this.stepsRatio[0].visual=math.fit(this.domRange.ratio,-.95,-.62,0,1),"
        "this.stepsRatio[0].dom=math.fit(this.domRange.ratio,-.95,-.62,0,1),"
        "this.stepsRatio[1].visual=this.stepsRatio[1].dom=math.fit(this.domRange.ratio,-.48,-.12,0,1),"
        "this.stepsRatio[2].visual=this.stepsRatio[2].dom=math.fit(this.domRange.ratio,.02,.38,0,1),"
        "this.stepsRatio[3].visual=this.stepsRatio[3].dom=math.fit(this.domRange.ratio,.18,.85,0,1);"
        "for(let S=0;S<this.domListItems.length;S++){const M=ease.cubicInOut("
        "(this.stepsRatio[S]||this.stepsRatio[this.stepsRatio.length-1]).dom),"
        "R=this.domListItems[S];"
        "R&&(R.style.transform=`translateY(${(1-M)*50}%)`,"
        "R.style.opacity=p*M)}"
    )
    if steps_assign_old in js:
        js = js.replace(steps_assign_old, steps_assign_new, 1)
        print("  cashback list animation (4 bullets)")
    elif steps_assign_prev in js:
        js = js.replace(steps_assign_prev, steps_assign_new, 1)
        print("  cashback list animation timing widened")

    referral_offset_targets = (
        "S+=math.fit(v,0,2,50,0,ease.cubicOut),",
        "S+=math.fit(v,0,2,0,-42,ease.cubicOut),",
    )
    referral_offset_new = "S+=math.fit(v,0,2,0,-42,ease.cubicOut),"
    for old in referral_offset_targets:
        if old in js and old != referral_offset_new:
            js = js.replace(old, referral_offset_new, 1)
            print("  referral vertical center offset")
            break

    return js


def repair_staking_visibility(js: str) -> str:
    staking_fade_old = (
        "l=math.fit(this.domRange.showScreenOffset,.5,1,0,1),"
        "u=math.fit(this.domRange.ratio,0,.2,0,1),p=l*(1-u),"
        "v=math.fit(l,.1,1,0,1),g=math.fit(u,.2,1,0,1);"
        "this._titleTextAnimation(v,g);let _=math.fit(l,.15,.9,0,1),"
        "x=math.fit(u,.35,1,0,1);this._descTextAnimation(_,x),"
        "this.domListItems.forEach((S,M)=>{const ir=ITEMS_RANGE[M]"
    )
    staking_fade_new = (
        "l=math.fit(this.domRange.showScreenOffset,.5,1,0,1),"
        "u=math.fit(this.domRange.hideScreenOffset,-1,-.5,0,1),p=l*(1-u),"
        "v=math.fit(l,.1,1,0,1),g=math.fit(u,.2,1,0,1);"
        "this._titleTextAnimation(v,g);let _=math.fit(l,.15,.9,0,1),"
        "x=math.fit(u,.35,1,0,1);this._descTextAnimation(_,x),"
        "this.domListItems.forEach((S,M)=>{const ir=ITEMS_RANGE[M]"
    )
    if staking_fade_old in js:
        js = js.replace(staking_fade_old, staking_fade_new, 1)
        print("  staking visibility fade fixed")

    return js


def repair_experience_slides(js: str) -> str:
    markers = (
        "u<1S+=",
        "}init()init()",
        "this.domListItems&&this.domListItems.forEach",
        "hideScreenOffset<.3_chapterTextAnimation",
        "domRange.ratio_titleTextAnimation",
    )
    if not any(marker in js for marker in markers):
        return js

    js = js.replace("}init()init(){}", "}init(){}")

    referral_pre_patched = (
        'preInit(o){this.domContainer=o.querySelector("#story-rewards-referral"),'
        "this.domContent=this.domContainer.querySelector("
        '".story-feature-content"),this.domTitle=this.domContainer.querySelector('
        '".story-feature-title"),this.domDesc=this.domContainer.querySelector('
        '".story-feature-desc"),this.domList=this.domContainer.querySelector('
        '".story-feature-list"),this.domListItems=Array.from('
        'this.domContainer.querySelectorAll(".story-feature-list > div")),'
        "this._listStep=76}init(){}"
    )
    if referral_pre_patched in js:
        js = js.replace(referral_pre_patched, REFERRAL_PREINIT_CANONICAL, 1)

    hero_pre_patched = (
        'querySelector("#story-rewards-hero"),this.domContent=this.domContainer.querySelector(".story-feature-content"),'
        "this.domChapter=this.domContainer.querySelector("
        '".story-feature-chapter"),this.domTitle=this.domContainer.querySelector('
        '".story-feature-title"),this.domDesc=this.domContainer.querySelector(".story-feature-desc"),'
        'this.domList=this.domContainer.querySelector(".story-feature-list"),'
        "this.domListItems=Array.from("
        'this.domContainer.querySelectorAll(".story-feature-list > div")),'
        "this._listStep=72,"
        "this.domScrollIndicator=this.domContainer.querySelector("
        '".scroll-down-cta")'
    )
    hero_pre_original = (
        'querySelector("#story-rewards-hero"),this.domContent=this.domContainer.querySelector(".story-feature-content"),'
        "this.domChapter=this.domContainer.querySelector("
        '".story-feature-chapter"),this.domTitle=this.domContainer.querySelector('
        '".story-feature-title"),this.domDesc=this.domContainer.querySelector(".story-feature-desc"),'
        "this.domScrollIndicator=this.domContainer.querySelector("
        '".scroll-down-cta")'
    )
    if hero_pre_patched in js:
        js = js.replace(hero_pre_patched, hero_pre_original, 1)

    hero_new, hero_count = re.subn(
        r"(class StoryRewardsHeroSlide\{.*?this\._descTextAnimation\(x,w\);).*?"
        r"(_chapterTextAnimation\(o,a\))",
        rf"\1{HERO_UPDATE_TAIL}}}\2",
        js,
        count=1,
        flags=re.DOTALL,
    )
    if hero_count:
        js = hero_new
        print("  repaired StoryRewardsHeroSlide update")

    referral_new, referral_count = re.subn(
        r"(class StoryRewardsReferralSlide\{.*?this\._descTextAnimation\(x,w\);).*?"
        r"(_titleTextAnimation\(o,a\))",
        rf"\1{REFERRAL_UPDATE_TAIL}}}\2",
        js,
        count=1,
        flags=re.DOTALL,
    )
    if referral_count:
        js = referral_new
        print("  repaired StoryRewardsReferralSlide update")

    js = js.replace(
        "hideScreenOffset<.3_chapterTextAnimation",
        "hideScreenOffset<.3}_chapterTextAnimation",
    )
    js = js.replace(
        "domRange.ratio_titleTextAnimation",
        "domRange.ratio}_titleTextAnimation",
    )

    return js


BATTLEPASS_UPDATE_TAIL = (
    "let w=-a.screenY;"
    "w+=math.fit(v,0,1,50,0,ease.cubicOut),"
    "w+=math.fit(g+x,0,2,0,-25,ease.cubicIn),"
    'this.domContent.style.transform=`translateY(${w}px)`,'
    'this.domContent.style.visibility=p>0?"visible":"hidden",'
    "l>0&&(storyAirdropPostAvatarsVisual.stateIndex=1,"
    "storyAirdropPostAvatarsVisual.ratio=math.fit(this.domRange.showScreenOffset,.5,2,0,1));"
    "let S=math.fit(this.domRange.hideScreenOffset,-1,1,0,1);"
    "u>0&&(storyAirdropPostAvatarsVisual.stateIndex=2,"
    "storyAirdropPostAvatarsVisual.ratio=S),"
    "storyAirdropPostAvatarsVisual.rotationRatio=S"
)

BATTLEPASS_PREINIT_ORIGINAL = (
    'preInit(o){this.domContainer=o.querySelector("#story-airdrops-post-battlepass"),'
    "this.domContent=this.domContainer.querySelector("
    '".story-feature-content"),this.domTitle=this.domContainer.querySelector('
    '".story-feature-title"),this.domDesc=this.domContainer.querySelector('
    '".story-feature-desc")}init(){}'
)


def repair_tools_slide(js: str) -> str:
    markers = (
        "domSkillsTrack",
        "skills-ticker-track",
        'this.domContent.style.transform="none"',
    )
    if not any(marker in js for marker in markers):
        return js

    bp_pre_patched = (
        'preInit(o){this.domContainer=o.querySelector("#story-airdrops-post-battlepass"),'
        "this.domContent=this.domContainer.querySelector("
        '".story-feature-content"),this.domTitle=this.domContainer.querySelector('
        '".story-feature-title"),this.domDesc=this.domContainer.querySelector('
        '".story-feature-desc"),this.domSkillsTrack='
        'this.domContainer.querySelector(".skills-ticker-track")}init(){}'
    )
    if bp_pre_patched in js:
        js = js.replace(bp_pre_patched, BATTLEPASS_PREINIT_ORIGINAL, 1)
        print("  revert tools preInit")

    js = js.replace(
        "resize(o,a){this._splitText(),this.domSkillsTrack&&"
        "(this._skillsShift=Math.max(0,this.domSkillsTrack.scrollWidth-"
        "(properties.viewportWidth||o)*.9))}update(o)",
        "resize(o,a){this._splitText()}update(o)",
        1,
    )

    bp_new, bp_count = re.subn(
        r"(class StoryAirdropsPostBattlepassSlide\{.*?this\._descTextAnimation\(_,x\);).*?"
        r"(_titleTextAnimation\(o,a\))",
        rf"\1{BATTLEPASS_UPDATE_TAIL}}}\2",
        js,
        count=1,
        flags=re.DOTALL,
    )
    if bp_count:
        js = bp_new
        print("  revert tools slide update")

    return js


def verify_hoisted_syntax(js_path: Path) -> None:
    result = subprocess.run(
        ["node", "--check", str(js_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "hoisted.js syntax check failed:\n"
            + (result.stderr or result.stdout or "unknown error")
        )


def apply_hoisted(profile: dict) -> None:

    js = HOISTED.read_text(encoding="utf-8")

    lb = profile["leaderboard"]

    names_js = json.dumps(lb["names"], ensure_ascii=False)

    scores_js = json.dumps(sorted(lb["scores"], reverse=True))



    js, n1 = re.subn(r"NAMES=\[[^\]]+\]", f"NAMES={names_js}", js, count=1)

    js, n2 = re.subn(

        r"SCORES=\[[^\]]+\]\.sort\(\)\.reverse\(\)",

        f"SCORES={scores_js}.sort().reverse()",

        js,

        count=1,

    )



    seasons_js = json.dumps(profile["seasons"], ensure_ascii=False)

    js, n3 = re.subn(

        r"getHTMLCard\(\[[^\]]+\]\[o\]\|\|",

        f"getHTMLCard({seasons_js}[o]||",

        js,

        count=1,

    )



    if n1 and n2:

        print("  leaderboard NAMES/SCORES")

    else:

        print("  WARN leaderboard arrays not updated")

    if n3:

        print("  education seasons")

    else:

        print("  WARN seasons not updated")

    seasons_count = len(profile["seasons"])
    js, loop_count = re.subn(
        r"for\(let o=0;o<\d+;o\+\+\)\{const a=getHTMLCard\(",
        f"for(let o=0;o<{seasons_count};o++){{const a=getHTMLCard(",
        js,
        count=1,
    )
    if loop_count:
        print(f"  seasons card count {seasons_count}")

    js = repair_experience_slides(js)

    old_hide = (
        "document.querySelectorAll("
        '"#story-rewards-hero .exp-achievement,#story-rewards-referral .exp-achievement"'
        ").forEach(H=>H.style.display=l>0&&u<1?\"none\":\"\"),"
        "storyRewardsReferralVisual.isActive=l>0&&u<1,"
        "storyRewardsReferralVisual.showRatio=l"
    )
    clean_hide = (
        "storyRewardsReferralVisual.isActive=l>0&&u<1,"
        "storyRewardsReferralVisual.showRatio=l"
    )
    if old_hide in js:
        js = js.replace(old_hide, clean_hide, 1)
        print("  removed achievement hide hack")

    js = repair_tools_slide(js)

    seasons_scroll_3 = "const x=math.fit(this.domRange.showScreenOffset,1,7,0,3)"
    seasons_scroll_4 = "const x=math.fit(this.domRange.showScreenOffset,1,9,0,4)"
    seasons_num_3 = (
        "this.domSeasonNumber.style.transform="
        "`translate(-50%, ${math.clamp(Math.floor(x-1)+math.fit(S,0,.2,0,1),0,2)*-25}%)`"
    )
    seasons_num_4 = (
        "this.domSeasonNumber.style.transform="
        "`translate(-50%, ${math.clamp(Math.floor(x-1)+math.fit(S,0,.2,0,1),0,3)*-25}%)`"
    )
    seasons_card3_base = (
        "this.cards[2].style.opacity=this.globalOpacity*N}"
        "w!==this.currentSeasonInt"
    )
    seasons_card3_fourth = (
        "this.cards[2].style.opacity=this.globalOpacity*N;"
        "this.cards.length>3&&(F=math.fit(x,2.9,3.1,0,1),"
        "z=math.fit(x,3.9,4.1,0,1),"
        "G=-110*F-10,N=F,U=(F-1)*20,"
        "this.cards[3].style.transform="
        "`translate3d(-50%, calc(2rem + ${G}%), ${200*ease.cubicOut(N)}px)rotateX(${U}deg) `,"
        "this.cards[3].style.opacity=this.globalOpacity*N)}"
        "w!==this.currentSeasonInt"
    )
    if seasons_count >= 4:
        if seasons_scroll_3 in js:
            js = js.replace(seasons_scroll_3, seasons_scroll_4, 1)
            print("  seasons scroll range (4 cards)")
        if seasons_num_3 in js:
            js = js.replace(seasons_num_3, seasons_num_4, 1)
        if seasons_card3_base in js and "this.cards[3].style" not in js:
            js = js.replace(seasons_card3_base, seasons_card3_fourth, 1)
            print("  seasons 4th card animation")
    else:
        if seasons_scroll_4 in js:
            js = js.replace(seasons_scroll_4, seasons_scroll_3, 1)
            print("  seasons scroll range (3 cards)")
        if seasons_num_4 in js:
            js = js.replace(seasons_num_4, seasons_num_3, 1)
        if seasons_card3_fourth in js:
            js = js.replace(seasons_card3_fourth, seasons_card3_base, 1)
            print("  revert seasons 4th card animation")

    staking_items_old = (
        "const R=math.fit(this.domRange.showScreenOffset,"
        "ITEMS_RANGE[M][0],ITEMS_RANGE[M][1],0,1)"
    )
    staking_items_new = (
        "const ir=ITEMS_RANGE[M]||[.75+M,.75+M+1],"
        "R=math.fit(this.domRange.showScreenOffset,ir[0],ir[1],0,1)"
    )
    if staking_items_old in js:
        js = js.replace(staking_items_old, staking_items_new, 1)
        print("  staking list ITEMS_RANGE guard")

    js = repair_exp_bullet_slides(js)
    js = repair_staking_visibility(js)

    hero_btn_old = (
        "[this.endHeroButton,this.domHeroButton].forEach(u=>{u.addEventListener"
    )
    hero_btn_new = (
        "[this.endHeroButton,this.domHeroButton].forEach(u=>{u&&u.addEventListener"
    )
    if hero_btn_old in js and hero_btn_new not in js:
        js = js.replace(hero_btn_old, hero_btn_new, 1)
        print("  end-hero button null guard")

    HOISTED.write_text(js, encoding="utf-8")
    verify_hoisted_syntax(HOISTED)

    print(f"Updated {HOISTED}")





def apply_meta(profile: dict) -> None:

    p = profile["profile"]

    name = p["name"]

    if MANIFEST.exists():

        text = MANIFEST.read_text(encoding="utf-8")

        text = re.sub(r'"name"\s*:\s*"[^"]*"', f'"name": "{name}"', text)

        text = re.sub(

            r'"short_name"\s*:\s*"[^"]*"',

            f'"short_name": "{name.split()[0]}"',

            text,

        )

        MANIFEST.write_text(text, encoding="utf-8")

        print(f"Updated {MANIFEST}")



    if PACKAGE.exists():

        text = PACKAGE.read_text(encoding="utf-8")

        text = re.sub(

            r'"description"\s*:\s*"[^"]*"',

            f'"description": "Immersive WebGL portfolio — {name}, {p["title"]}"',

            text,

            count=1,

        )

        PACKAGE.write_text(text, encoding="utf-8")



    if README.exists():

        README.write_text(

            f"# {name} — Portfolio\n\n"

            f"Immersive WebGL portfolio personalized for **{p['title']}**.\n\n"

            f"## Personalize\n\n"

            f"```bash\nnpm run sync-assets\nnpm run personalize\n```\n",

            encoding="utf-8",

        )





def main() -> None:

    profile = load_profile()

    print("Personalizing portfolio for", profile["profile"]["name"])

    apply_index(profile)

    apply_hoisted(profile)

    apply_meta(profile)

    print("Done.")





if __name__ == "__main__":

    main()

