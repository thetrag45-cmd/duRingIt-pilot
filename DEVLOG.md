# duRingIt · Monie ID — Devlog

A chronological summary of how the project came together — what was built, what bugs got fixed, and what design decisions were made along the way.

---

## Phase 0 — Starting point

**Inheritance:** an existing single-file HTML quiz app (`duRingIt-pilot-quiz.html`) with a dark minimal UI, a compatibility page (`compatibility.html`), and 11 dark-themed archetype profile pages in `archetypes/`. The quiz logic, scoring, scale weights, tie-breaker logic, and bridge fallback were all working — but the visuals were generic and felt disconnected from the brand.

**Goal:** redesign the entire surface around a warm "Monie ID Intake / paper folder" visual system to match a new set of design references — without touching the underlying quiz logic.

---

## Phase 1 — Quiz redesign

**Visual system established:**
- Type pairing: **Bricolage Grotesque** (display) + **Lexend** (body) + **Caveat** (handwriting accents)
- Color tokens: cream paper, honey gold, sage green, brown ink, tan borders
- Components: washi-taped paper question cards, folder-tab progress (16 tabs in 2 rows of 8), gold-stamped checkmarks for selected answers, coin buttons for the 1–5 scale, ambient SVG doodles (paperclip, stamp, coins, receipt)
- Phone frame: full-bleed on mobile (≤540px), dark device bezel on desktop

**New screens introduced:**
- A **chapter intro pill** ("Money Meaning", "Drive & Decisions", "Reality Check", "Identity Calibration") replacing generic phase labels
- A **loading / compiling screen** between Q16 and the result, with 4 animated checklist rows ("Reading money meaning", "Checking decision pattern", "Matching stress behavior", "Preparing your result card")
- An **Identity Calibration** screen for the tie-breaker, with two folder-tab option cards (honey and sage)

**Preserved verbatim:**
- All quiz data (`ARC`, `MAIN_QS`, `SCALE_QS`, `TB`)
- Scoring (`scoreChoice`, `SCALE_WEIGHTS`, `applyScaleScores`)
- Tie-breaker + bridge logic
- WhatsApp share, compatibility link, validation form, copy-to-clipboard, sessionStorage state persistence

---

## Phase 2 — BEGA result cards

11 BEGA cards (Aggressive Builder, Freedom Chaser, Wealth Architect, The Optimizer, Status Strategist, Lifestyle Inflator, Lifestyle Romantic, Steady Guardian, Anxious Achiever, Emotional Escapist, The Free Spirit) were dropped into `cards/<CODE>.jpg`.

A `CARD_ASSETS` mapping was added at the top of the quiz script. The result page renders the BEGA card image at top with a graceful SVG placeholder fallback if the file is missing. Image aspect ratio set to **948 / 1659** (the actual portrait ratio of the BEGA art) so each card displays in full without cropping.

Bridge result page renders **two BEGA cards** side-by-side with an × separator.

---

## Phase 3 — Compatibility page rebuild

The dark compat page was rebuilt in the warm paper system with **four routed modes** controlled by URL params:

| URL | View |
|---|---|
| `?a=X` | **Picker** — user's BEGA hero card + grid of the other 10 cards to compare |
| `?a=X&compare=Y` | **Pair result** — meters card (Money Sync, Spending Rhythm, Planning Style, Stress Response), 4 section cards (Money Chemistry, Friction Point, Best Together For, Watch Out For) |
| `?a=X&b=Y` | **Bridge result** — two "You" cards + side-A/side-B blurbs + 4 bridge-tuned sections |
| `?view=map&a=X` | **Compatibility Map** — all 10 other archetypes grouped by label around the user's card |

**Compatibility labels** derived from existing score field:
- 75+ → Easy Sync
- 60+ → Good Balance
- 50+ → Productive Tension
- 40+ → Needs Care
- <40 → High Friction

**Bridge context threading** via `&from=` param: when a bridge user navigates Bridge → Picker → Pair, the bridge partner is preserved so back-navigation correctly returns to the bridge result.

---

## Phase 4 — Archetype profile redesign

All 11 archetype pages at `archetypes/<slug>.html` rebuilt in the paper system:
- BEGA card image hero on the left
- Family pill (Builders / Experiencers / Guardians / Avoiders) themed per family
- Big Bricolage title + type code chip + tagline pull quote
- Dashed-bordered table of contents
- 14 paper-section cards with washi tape, §-numbered eyebrows, and original content preserved verbatim (`.prose`, `.b-list`, `.sub-h`, `.pull-q` classes restyled, not renamed)
- Footer card with "Back to my result" + "See your compatibility" CTAs

Generated in one batch via a script that read each source page, extracted the family/title/tagline/sections, and rewrapped each in the new template.

---

## Phase 5 — Archetypes index

`archetypes/index.html` — a grid view of all 11 BEGA cards organised by the four families with hand-written taglines and a CTA back to the quiz. Fixed the broken "← All archetypes" link that was 404-ing on every archetype profile page.

---

## Phase 6 — Landing page

`index.html` — marketing page (max-width 1180px, not phone-shaped) with:
- Brand nav + "Take the quiz" CTA
- Hero: "What kind of money person are you really?" headline with honey-highlighted word + collaged BEGA cards + MONIE ID VERIFIED stamp
- Stats row (11 / 16 / ~91% / ~4 min)
- "How it works" 3-step section
- 11-archetype gallery grouped by family
- Email capture (Formspree-ready)
- Compatibility teaser
- FAQ accordion
- Big closing CTA
- Footer with site links

---

## Phase 7 — Blog

- `blog/index.html` — Blog landing in the same paper system
- `blog/_template.html` — Ready-to-write starter template
- **3 real posts:**
  1. *Why most money personality quizzes are wrong about you* — behaviour vs. self-description
  2. *How the Bridge result actually works* — explainer for the rare 8% case
  3. *Aggressive Builder vs Wealth Architect* — comparison piece for the two most-confused Builder archetypes

---

## Phase 8 — About / Privacy

`about.html` — combined About + Privacy page in a single-column paper layout. Sections: what duRingIt is, why we built it, how the quiz works, is this science, privacy & data handling, contact. Linked from landing nav and every page footer.

---

## Phase 9 — Polish

- **`404.html`** — paper-style "this page isn't in the cabinet" with a "FILE 404 MISSING" stamp and CTAs back to home/quiz
- **`favicon.svg`** — honey coin with stamped "M" — replaces the blank browser tab
- **`og-cover.png`** (1200×630) — landscape paper banner with brand pill, 3-line headline, honey-highlighted "money" word, subhead, 4-dot meta row, 3 collaged BEGA cards, and Monie ID Verified stamp. Wired into `og:image` + `twitter:image` for landing, quiz, compat, blog, blog template, and archetypes index. Archetype profile pages use their own card image as og:image.
- **Print stylesheets** — added to quiz, compat, and all 11 archetype pages. On Cmd+P / Ctrl+P: cream bg becomes white, phone bezel disappears, nav/buttons/doodles hidden, cards full-width with simple borders, headings avoid breaking across pages.
- **`robots.txt` + `sitemap.xml`** — 19 URLs listed with priorities and changefreq hints. Pointed at the GitHub Pages domain.

---

## Phase 10 — Bug fixes

A series of real bugs surfaced and got fixed during testing:

1. **"duRingIt" rendered as three flex items** — Fixed by wrapping the brand name in a single `.brand-name` span.
2. **"Back to my result" loaded the home page instead of the result** — sessionStorage was being consumed on first read, so subsequent navigations lost state. **First fix:** added a `backToMyResult()` helper on compat + archetype pages that seeded sessionStorage before navigating. **Second fix (the real one):** seeding fake state confused users who arrived from the landing page. Changed to `history.back()` with a landing fallback — naturally returns the user to wherever they actually came from; the quiz's own sessionStorage handles result restoration for users who came from a real quiz.
3. **Bridge context lost when navigating Bridge → Picker → Pair** — Added a `&from=` URL param to thread the bridge partner through the picker and pair views.
4. **"Start over" produced a blank page** — Changed `restart()` to navigate to `./index.html` instead of trying to re-render in place.
5. **"Get my report" 404'd** — Replaced the literal `TALLY_FORM_URL` placeholder with a configurable variable that hides the block when empty.
6. **"Want to write your first post?" admin CTA shown on public blog** — Removed from public-facing pages.
7. **Archetype "← All archetypes" link 404'd** — Built `archetypes/index.html` to fix.
8. **Blog link 404'd under `file://`** — Changed `./blog/` to `./blog/index.html`.
9. **OG image cropped on social card** — Regenerated with text on the left half only and cards stacked on the right.

---

## Final inventory

**16 HTML files** across the site:

```
/
├── index.html                              # Landing page
├── duRingIt-pilot-quiz.html                # Quiz (full flow)
├── compatibility.html                       # Compatibility (4 modes)
├── about.html                               # About + Privacy
├── 404.html                                 # Paper-style 404
├── favicon.svg
├── og-cover.png                             # 1200×630 social card
├── robots.txt
├── sitemap.xml
├── cards/
│   └── AB.jpg, FC.jpg, WA.jpg, ST.jpg,
│       SS.jpg, LI.jpg, LR.jpg,
│       SG.jpg, AX.jpg,
│       EE.jpg, WN.jpg
├── archetypes/
│   ├── index.html                          # Grid of all 11 cards
│   ├── aggressive-builder.html
│   ├── freedom-chaser.html
│   ├── wealth-architect.html
│   ├── the-optimizer.html
│   ├── status-strategist.html
│   ├── lifestyle-inflator.html
│   ├── lifestyle-romantic.html
│   ├── steady-guardian.html
│   ├── anxious-achiever.html
│   ├── emotional-escapist.html
│   └── the-free-spirit.html
└── blog/
    ├── index.html                          # Blog landing
    ├── _template.html                      # Writing template (admin reference)
    ├── why-money-quizzes-are-wrong.html
    ├── how-the-bridge-result-works.html
    └── aggressive-builder-vs-wealth-architect.html
```

---

## Design system summary

If you need to add a new page later (with or without Claude), copy any existing page as a starting reference and reuse these tokens and patterns:

**Color tokens:**
```css
--bg-cream:    #FFF7EA;
--paper:       #FFF2D9;
--paper-light: #FFFBF3;
--paper-warm:  #FAE7C5;
--ink:         #2A170D;
--brown:       #6B3F22;
--caramel:     #A66A2E;
--honey:       #F6B638;
--honey-deep:  #D89724;
--sage:        #7F8F5A;
--border:      #D8B982;
```

**Family accents:**
- Builders: `#F6E2C2` / `#E2BE7B` / `#7A4B1C`
- Experiencers: `#F8D7C2` / `#E8B58E` / `#8C4626`
- Guardians: `#E6EBD3` / `#B7C28A` / `#5E6E3E`
- Avoiders: `#EADFEC` / `#C5A8CA` / `#6A4275`

**Patterns:** washi tape (`.tape`), folded-corner paper sections (`::after` triangle), paper card with `--shadow-paper`, dashed buttons (`.btn-secondary`), honey gradient primary buttons (`.btn-primary`), section eyebrow / title / sub pattern, "Caveat" handwriting accents.

**Reference pages** to copy from when adding new ones:
- Long-form content → `blog/_template.html`
- Marketing / multi-section → `index.html`
- Profile / explainer → any `archetypes/<slug>.html`

---

## What's left

Not design work — content + iteration:

1. **Push to main, deploy.**
2. **Replace `REPLACE_WITH_YOUR_FORM_ID`** in `index.html` once you have a real form endpoint (Formspree / Tally / MailerLite / ConvertKit).
3. **Submit sitemap to Google Search Console** once deployed.
4. **Test keyboard-only navigation** through the quiz one time before launch.
5. **Read pilot feedback exports** and tweak copy or scoring weights based on real mismatches.

Then ship and iterate based on what real users actually do.

🟢
