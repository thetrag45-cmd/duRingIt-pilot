#!/usr/bin/env python3
"""Build 11 archetype blog HTML files from the official Monie ID PDF text."""

import re
from pathlib import Path

# ─────────────────────────────────────────────
# Archetype metadata
# ─────────────────────────────────────────────
ARCHETYPES = [
    ('WA', 'wealth-architect',     'The Wealth Architect',      'Builders'),
    ('SA', 'silent-accumulator',   'The Silent Accumulator',    'Guardians'),
    ('LI', 'lifestyle-inflator',   'The Lifestyle Inflator',    'Experiencers'),
    ('SS', 'status-strategist',    'The Status Strategist',     'Experiencers'),
    ('FC', 'freedom-chaser',       'The Freedom Chaser',        'Builders'),
    ('AX', 'anxious-achiever',     'The Anxious Achiever',      'Guardians'),
    ('LR', 'lifestyle-romantic',   'The Lifestyle Romantic',    'Experiencers'),
    ('EE', 'emotional-escapist',   'The Emotional Escapist',    'Avoiders'),
    ('ST', 'calculated-optimizer', 'The Calculated Optimizer',  'Builders'),
    ('AB', 'aggressive-builder',   'The Aggressive Builder',    'Builders'),
    ('FD', 'financial-drifter',    'The Financial Drifter',     'Avoiders'),
]

SECTIONS = [
    'Archetype Overview',
    'Core Strengths',
    'Core Weaknesses',
    'Spending Habits',
    'Investing Style',
    'Relationship With Money',
    'Career Behavior',
    'Emotional Triggers',
    'Common Mistakes',
    'Growth Path',
    'Ideal Partner',
    'Stress Behavior',
    'Financial Fear',
    'Financial Superpower',
]

BULLET_CHAR = '●'  # ●


# ─────────────────────────────────────────────
# Parser
# ─────────────────────────────────────────────
def is_bullet_line(line: str) -> bool:
    """A bullet marker line — starts with ● optionally followed by content."""
    s = line.strip()
    return s.startswith(BULLET_CHAR)


def bullet_content(line: str) -> str:
    """Extract content from a bullet line (handles 'BULLET content' format)."""
    s = line.strip()
    # Remove bullet char and any zero-width chars
    s = s.lstrip(BULLET_CHAR).strip('​').strip()
    return s


def clean_bullet(s: str) -> str:
    """Normalize a bullet's content: strip trailing punctuation and leading connectors."""
    s = s.strip()
    # Strip trailing comma/period (but preserve content like "rich.")
    s = s.rstrip(',').rstrip('.')
    # Strip leading "and " / "or " connectors (substring match, not character set)
    low = s.lower()
    for prefix in ('and ', 'or '):
        if low.startswith(prefix):
            s = s[len(prefix):]
            break
    return s


def parse_archetype(filepath: Path):
    """Return (tagline, [(section_name, raw_lines), ...])."""
    text = filepath.read_text()
    lines = text.split('\n')

    # Find tagline — collect lines starting with curly opening quote until closing curly quote
    tagline = ''
    for idx, line in enumerate(lines[:20]):
        s = line.strip()
        if s.startswith('“'):
            buf = [s]
            # Continue collecting until closing quote appears
            if '”' not in s:
                j = idx + 1
                while j < min(idx + 5, len(lines)):
                    nxt = lines[j].strip()
                    if not nxt:
                        break
                    buf.append(nxt)
                    if '”' in nxt:
                        break
                    j += 1
            tagline = ' '.join(buf).strip('“”').strip()
            # Clean up any trailing dot/comma
            break

    # Split into sections
    sections = []
    current_name = None
    current_lines = []
    for line in lines:
        s = line.strip()
        # Skip archetype name repeats (matches title in first few lines)
        if s in SECTIONS:
            if current_name:
                sections.append((current_name, current_lines))
            current_name = s
            current_lines = []
        elif current_name is not None:
            current_lines.append(line)

    if current_name:
        sections.append((current_name, current_lines))

    return tagline, sections


def parse_section_content(raw_lines):
    """
    Parse a section's raw lines into structured items.
    Returns list of items where each item is one of:
      ('h3', 'Subheading Text')
      ('p',  'paragraph text')
      ('ul', ['bullet 1', 'bullet 2', ...])
      ('quote', 'quote text')
    """
    items = []
    i = 0
    n = len(raw_lines)

    while i < n:
        line = raw_lines[i]
        s = line.strip()

        # Skip blank lines
        if not s:
            i += 1
            continue

        # Sub-heading detection: "1. Title" or short Title-Case label without trailing punctuation
        # within Emotional Triggers / Common Mistakes etc.
        if re.match(r'^\d+\.\s+[A-Z]', s):
            items.append(('h3', s))
            i += 1
            continue

        # Bullets: collect a run of bullet lines
        if is_bullet_line(s):
            bullets, i = collect_bullets(raw_lines, i)
            items.append(('ul', bullets))
            continue

        # Curly-quoted quote
        if s.startswith('“') and (s.endswith('”') or s.endswith('”.') or s.endswith('”,')):
            items.append(('quote', s.strip('“”.,').strip()))
            i += 1
            continue

        # Short bold-style mini-heading (no period at end, Title Case, not too long)
        if (len(s) < 50
            and s[0].isupper()
            and not s.endswith(('.', ',', ':', '?', '!'))
            and re.match(r'^[A-Z][A-Za-z][A-Za-z\s\-]+$', s)):
            items.append(('h3', s))
            i += 1
            continue

        # Default: paragraph — collect until next blank or special line
        para, i = collect_paragraph(raw_lines, i)
        if para:
            items.append(('p', para))

    return items


def collect_bullets(raw_lines, start):
    """
    Collect a run of bullets. Handles two PDF patterns:
      A) Inline: "● content"
      B) Stacked: 4 lines of "●" then 4 lines of content
    Returns (list_of_bullet_strings, next_index).
    """
    i = start
    n = len(raw_lines)
    bullets = []

    # Detect pattern: count consecutive bare bullets
    bare_run = 0
    j = i
    while j < n:
        ls = raw_lines[j].strip()
        if ls == BULLET_CHAR or ls.startswith(BULLET_CHAR + '​'):
            # Check if there is content after the bullet char
            content_after = bullet_content(raw_lines[j])
            if not content_after:
                bare_run += 1
                j += 1
                continue
            else:
                break
        else:
            break

    if bare_run >= 2:
        # Stacked pattern: collect bare bullets, then skip blanks, then content lines
        i = start + bare_run
        # Skip blank lines
        while i < n and not raw_lines[i].strip():
            i += 1
        # Collect bare_run content lines
        contents = []
        while i < n and len(contents) < bare_run:
            ls = raw_lines[i].strip()
            if not ls:
                i += 1
                continue
            # Stop if we hit a section header or another bullet block
            if ls in SECTIONS or is_bullet_line(ls):
                break
            contents.append(clean_bullet(ls))
            i += 1
        bullets.extend(contents)
        return bullets, i

    # Inline pattern: each line is "● content"
    while i < n:
        ls = raw_lines[i].strip()
        if not ls:
            i += 1
            # Continue if next non-empty is also bullet
            j = i
            while j < n and not raw_lines[j].strip():
                j += 1
            if j < n and is_bullet_line(raw_lines[j]):
                i = j
                continue
            else:
                break
        if is_bullet_line(ls):
            content = bullet_content(ls)
            if content:
                bullets.append(clean_bullet(content))
                i += 1
            else:
                # Bare bullet inside inline run — switch strategy: collect remaining bare bullets
                # then their content lines below
                bare = 1
                k = i + 1
                while k < n and raw_lines[k].strip() == BULLET_CHAR:
                    bare += 1
                    k += 1
                # Skip blanks
                while k < n and not raw_lines[k].strip():
                    k += 1
                contents = []
                while k < n and len(contents) < bare:
                    ls2 = raw_lines[k].strip()
                    if not ls2:
                        k += 1
                        continue
                    if ls2 in SECTIONS or is_bullet_line(ls2):
                        break
                    contents.append(clean_bullet(ls2))
                    k += 1
                bullets.extend(contents)
                i = k
                continue
        else:
            break

    return bullets, i


def collect_paragraph(raw_lines, start):
    """Collect consecutive text lines into one paragraph."""
    i = start
    n = len(raw_lines)
    parts = []
    while i < n:
        ls = raw_lines[i].strip()
        if not ls:
            i += 1
            break
        if ls in SECTIONS:
            break
        if is_bullet_line(ls):
            break
        if re.match(r'^\d+\.\s+[A-Z]', ls):
            break
        parts.append(ls)
        i += 1
    return ' '.join(parts), i


# ─────────────────────────────────────────────
# Renderer
# ─────────────────────────────────────────────
def esc(s: str) -> str:
    return (s.replace('&', '&amp;')
             .replace('<', '&lt;')
             .replace('>', '&gt;'))


def render_items(items):
    out = []
    for kind, payload in items:
        if kind == 'h3':
            out.append(f'<h3 class="sub-h">{esc(payload)}</h3>')
        elif kind == 'p':
            out.append(f'<p class="prose">{esc(payload)}</p>')
        elif kind == 'ul':
            lis = ''.join(f'<li>{esc(b)}</li>' for b in payload if b)
            out.append(f'<ul class="b-list">{lis}</ul>')
        elif kind == 'quote':
            out.append(f'<blockquote class="pull-q">&ldquo;{esc(payload)}&rdquo;</blockquote>')
    return '\n      '.join(out)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} &mdash; duRingIt Monie ID</title>
<meta name="description" content="{name} &mdash; one of 11 Monie ID financial archetypes. {tagline}">
<meta property="og:title" content="{name} &mdash; duRingIt Monie ID">
<meta property="og:description" content="{tagline}">
<meta property="og:type" content="article">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  background: #0D0D0D; color: #E8E8E8;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  line-height: 1.6;
}}
.wrap {{ max-width: 720px; margin: 0 auto; padding: 24px 20px 80px; }}
.brand {{ font-size: 13px; letter-spacing: 0.15em; text-transform: uppercase; color: #888; margin-bottom: 32px; }}
.brand span {{ color: #F5C842; }}
.brand a {{ color: inherit; text-decoration: none; }}
.fam {{ font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: #F5C842; margin-bottom: 10px; }}
h1 {{
  font-size: 44px; font-weight: 900; line-height: 1.05;
  margin-bottom: 14px; letter-spacing: -0.02em;
}}
.tagline {{
  font-size: 19px; font-style: italic; color: #F5C842;
  border-left: 3px solid #F5C842; padding: 4px 0 4px 16px;
  margin-bottom: 40px; line-height: 1.5;
}}
.section {{
  margin-bottom: 44px;
}}
.section h2 {{
  font-size: 13px; letter-spacing: 0.14em; text-transform: uppercase;
  color: #F5C842; margin-bottom: 16px; font-weight: 700;
  padding-bottom: 8px; border-bottom: 1px solid #2A2A2A;
}}
.sub-h {{
  font-size: 17px; font-weight: 700; color: #FFFFFF;
  margin-top: 22px; margin-bottom: 8px;
}}
.prose {{
  font-size: 16px; color: #C8C8C8; margin-bottom: 14px; line-height: 1.7;
}}
.b-list {{
  list-style: none; padding: 0; margin: 0 0 16px 0;
}}
.b-list li {{
  font-size: 15px; color: #B0B0B0; line-height: 1.6;
  padding: 6px 0 6px 22px; position: relative;
}}
.b-list li::before {{
  content: "—"; position: absolute; left: 0; color: #F5C842;
}}
.pull-q {{
  font-size: 18px; font-style: italic; color: #D4AA40;
  background: #161616; border-left: 3px solid #F5C842;
  padding: 14px 18px; border-radius: 0 10px 10px 0;
  margin: 18px 0;
}}
hr.divider {{
  border: 0; border-top: 1px solid #2A2A2A; margin: 28px 0;
}}
.foot-card {{
  background: #1A1A1A; border: 1px solid #2A2A2A; border-radius: 14px;
  padding: 24px; margin-top: 48px; text-align: center;
}}
.foot-card h3 {{
  font-size: 22px; font-weight: 800; margin-bottom: 8px; color: #FFF;
}}
.foot-card p {{ color: #888; font-size: 14px; margin-bottom: 16px; }}
.cta {{
  display: inline-block;
  background: #F5C842; color: #000; text-decoration: none;
  padding: 14px 24px; border-radius: 10px;
  font-weight: 700; font-size: 15px;
  transition: background 0.12s;
}}
.cta:hover {{ background: #FFD700; }}
.nav-prev {{
  display: flex; justify-content: space-between; gap: 12px; margin-top: 24px;
  font-size: 13px;
}}
.nav-prev a {{ color: #666; text-decoration: none; padding: 8px 12px; border: 1px solid #2A2A2A; border-radius: 8px; }}
.nav-prev a:hover {{ color: #F5C842; border-color: #F5C842; }}
@media (max-width: 520px) {{
  h1 {{ font-size: 34px; }}
  .tagline {{ font-size: 17px; }}
  .wrap {{ padding: 20px 16px 60px; }}
}}
</style>
</head>
<body>
<div class="wrap">

<div class="brand"><a href="../duRingIt-pilot-quiz.html">du<span>Ring</span>It &mdash; Monie ID</a></div>

<div class="fam">{family}</div>
<h1>{name}</h1>
<div class="tagline">&ldquo;{tagline}&rdquo;</div>

{sections_html}

<div class="foot-card">
  <h3>Don&rsquo;t know your Monie ID yet?</h3>
  <p>Take the 4-minute quiz to discover which of 11 archetypes you are.</p>
  <a class="cta" href="../duRingIt-pilot-quiz.html">Take the quiz &rarr;</a>
</div>

<div class="nav-prev">
  <a href="./index.html">&larr; All archetypes</a>
  <a href="../duRingIt-pilot-quiz.html">Take the quiz &rarr;</a>
</div>

</div>
</body>
</html>
"""


def render_sections_html(sections):
    out = []
    for name, raw in sections:
        items = parse_section_content(raw)
        body = render_items(items)
        out.append(f'<section class="section" id="{slugify(name)}">\n  <h2>{esc(name)}</h2>\n  {body}\n</section>')
    return '\n\n'.join(out)


def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


# ─────────────────────────────────────────────
# Index page (lists all 11 with taglines)
# ─────────────────────────────────────────────
INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The 11 Monie ID Archetypes &mdash; duRingIt</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: #0D0D0D; color: #E8E8E8; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; }}
.wrap {{ max-width: 720px; margin: 0 auto; padding: 24px 20px 80px; }}
.brand {{ font-size: 13px; letter-spacing: 0.15em; text-transform: uppercase; color: #888; margin-bottom: 32px; }}
.brand span {{ color: #F5C842; }}
.brand a {{ color: inherit; text-decoration: none; }}
h1 {{ font-size: 40px; font-weight: 900; line-height: 1.1; margin-bottom: 8px; letter-spacing: -0.02em; }}
.intro {{ font-size: 16px; color: #888; margin-bottom: 40px; }}
.fam-group {{ margin-bottom: 36px; }}
.fam-label {{ font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase; color: #F5C842; margin-bottom: 14px; font-weight: 700; }}
.arch-card {{
  display: block; background: #1A1A1A; border: 1px solid #2A2A2A;
  border-radius: 12px; padding: 18px 20px; margin-bottom: 12px;
  text-decoration: none; color: inherit; transition: all 0.12s;
}}
.arch-card:hover {{ border-color: #F5C842; background: #1E1E1E; }}
.arch-name {{ font-size: 19px; font-weight: 700; color: #FFF; margin-bottom: 4px; }}
.arch-tag {{ font-size: 14px; font-style: italic; color: #D4AA40; line-height: 1.5; }}
.cta-wrap {{ text-align: center; margin-top: 40px; }}
.cta {{ display: inline-block; background: #F5C842; color: #000; text-decoration: none; padding: 14px 24px; border-radius: 10px; font-weight: 700; font-size: 15px; }}
.cta:hover {{ background: #FFD700; }}
</style>
</head>
<body>
<div class="wrap">
<div class="brand"><a href="../duRingIt-pilot-quiz.html">du<span>Ring</span>It &mdash; Monie ID</a></div>
<h1>The 11 Monie ID Archetypes</h1>
<p class="intro">Which one are you? Read all 11 financial identities below, or take the quiz to find out.</p>
{groups_html}
<div class="cta-wrap">
  <a class="cta" href="../duRingIt-pilot-quiz.html">Take the quiz &rarr;</a>
</div>
</div>
</body>
</html>
"""


def render_index(archetype_meta):
    fam_order = ['Builders', 'Experiencers', 'Guardians', 'Avoiders']
    by_fam = {f: [] for f in fam_order}
    for code, slug, name, fam, tag in archetype_meta:
        by_fam[fam].append((slug, name, tag))

    groups = []
    for fam in fam_order:
        cards = []
        for slug, name, tag in by_fam[fam]:
            cards.append(
                f'<a class="arch-card" href="./{slug}.html">'
                f'<div class="arch-name">{esc(name)}</div>'
                f'<div class="arch-tag">&ldquo;{esc(tag)}&rdquo;</div>'
                f'</a>'
            )
        groups.append(
            f'<div class="fam-group">\n'
            f'  <div class="fam-label">{fam}</div>\n'
            f'  {"".join(cards)}\n'
            f'</div>'
        )
    return INDEX_TEMPLATE.format(groups_html='\n'.join(groups))


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main():
    out_dir = Path('/Users/zekelim/Gary Tan YC/archetypes')
    out_dir.mkdir(parents=True, exist_ok=True)

    meta_with_tag = []

    for code, slug, name, fam in ARCHETYPES:
        src = Path(f'/tmp/arc_{code}.txt')
        tagline, sections = parse_archetype(src)
        meta_with_tag.append((code, slug, name, fam, tagline))

        sections_html = render_sections_html(sections)
        html = HTML_TEMPLATE.format(
            name=esc(name),
            family=esc(fam),
            tagline=esc(tagline),
            sections_html=sections_html,
        )
        out_path = out_dir / f'{slug}.html'
        out_path.write_text(html)
        print(f'wrote {out_path} ({len(html):,} chars)')

    # Index page
    idx_html = render_index(meta_with_tag)
    idx_path = out_dir / 'index.html'
    idx_path.write_text(idx_html)
    print(f'wrote {idx_path} ({len(idx_html):,} chars)')


if __name__ == '__main__':
    main()
