### Task: Upgrade MEDTRIX to the Dynamic "Grand Unified Map" Study & Quiz Architecture

Refactor/build the **MEDTRIX** application into a modular, offline-capable medical knowledge base, MCQ engine, and clinical mastery tracker. Rather than hardcoding single-subject HTML, dynamically render any medical subject (e.g., Psychiatry, Medicine, Pharmacology, Pathology) from structured JSON files while strictly preserving the exact editorial dark-mode design system defined below.

---

#### 1. Exact Design Tokens & CSS Variables
Import Google Fonts:
`https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600&family=Fira+Mono:wght@400;700&family=Nunito:wght@700;800&display=swap`

Apply these exact CSS custom properties globally:
```css
:root {
  /* Core Surfaces & Ink */
  --bg: #0a0a14;
  --card: #14141f;
  --card-nested: #1b1b2a;
  --table-head: #1c1c2c;
  --table-hover: #171724;
  --certifiable-row: #1f1a1a;
  --line: #26263a;
  --ink: #e6eaf0;
  --ink-secondary: #cfd7e2;
  --ink-hero: #c3ccd8;
  --dim: #9aa5b4;
  --muted-index: #6b7789;
  --link: #8fb6d9;

  /* 7-Pillar Semantic Palette (Dynamic per pillar index/color) */
  --p1: #C0392B; /* Crimson Red */
  --p2: #1A5276; /* Deep Ocean Blue */
  --p3: #117A65; /* Emerald Teal */
  --p4: #884EA0; /* Royal Purple */
  --p5: #D4AC0D; /* Mustard Gold */
  --p6: #5D7A96; /* Slate Steel Blue */
  --p7: #D35400; /* Burnt Orange */

  /* Typography Families */
  --serif: 'Playfair Display', Georgia, serif;
  --sans: 'Inter', -apple-system, 'Segoe UI', Roboto, Arial, sans-serif;
  --mono: 'Fira Mono', ui-monospace, Consolas, monospace;
  --disp: 'Nunito', var(--sans);
}
```

2. Visual Styling & Layout Rules
Global Layout: body uses background: var(--bg), color: var(--ink), font-family: var(--sans), line-height: 1.62, scroll-behavior: smooth. Wrap content in .wrap (max-width: 1180px; margin: 0 auto; padding: 0 26px). Each <section> uses padding: 52px 0; border-bottom: 1px solid var(--line).
Hero Section:
Background: linear-gradient(135deg, #0a0a14 0%, #1a1a2e 40%, #2c1a3e 100%), padding: 70px 0 56px, border-bottom: 1px solid var(--line).
Top Badge: font-family: var(--mono); font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; background: rgba(255,255,255,0.1); padding: 6px 14px; border-radius: 3px.
Title (h1): font-family: var(--serif); font-size: 52px; line-height: 1.08 (34px below 760px) with text gradient linear-gradient(100deg, #C0392B, #884EA0 35%, #1A5276 60%, #117A65 85%, #D4AC0D) clipped to text.
Telemetry Stats Row: Flex container (gap: 26px) showing live counts for Pillars, Sub-modules, Questions, Clinical Cases, CBME Competencies, and Atomic Facts (28px bold --mono #fff numbers over 11.5px uppercase --dim labels).
Inline Elements:
.pill badges: font-family: var(--mono); font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 3px; color: #fff with background dynamically set to the Pillar's hex color.
<mark>: background: rgba(255, 220, 90, 0.16); color: #ffe9a8; padding: 1px 4px; border-radius: 2px.
<code>: font-family: var(--mono); font-size: 0.9em; background: #1c1c2c; color: #ffb9a8; padding: 2px 5px; border-radius: 3px.

3. Dynamic UI Components to Implement
Render each subject dashboard from JSON (data/subjects/<subject_id>.json) with these interactive views:
Mechanism Pillar Cards Grid (repeat(auto-fill, minmax(320px, 1fr)), gap: 17px):
Surface var(--card), border: 1px solid var(--line), border-radius: 9px, padding: 19px, and a 4px solid top accent border in the Pillar's color.
Displays Pillar title (--serif, 19px), italic --mono pathogenetic quote (12px), interactive sub-module tag chips (10px --mono, rgba(255,255,255,0.07)), and bottom metadata (11px --mono showing MCQ count, chapters, CBME codes, and user mastery %).
Interactive Hook: Clicking a Pillar card or sub-module chip opens either the Concept Reader Drawer (rendering Markdown notes, tables, extracted First Aid/Marrow images, and Mermaid flowcharts) or launches a Filtered MCQ Session in MEDTRIX.
Interactive SVG Hub-and-Spoke Network (viewBox="0 0 940 620"):
Dynamically compute radial (x, y) coordinates around (470, 300) for N pillars so it works whether a subject has 5, 7, or 10 pillars.
Center hub (r="74", radial gradient #3a3a5c to #16162a, stroke #4a4a70) + outer pillar nodes (r="46", fill #14141f, 2.5px pillar-colored stroke).
Draw cross-pillar discrimination lines (#2b2b42, 1.3px) that highlight on node hover and filter the Cross-Pillar table below when clicked.
Cross-Pillar Connections Table & CBME Competency Matrix:
Styled <table> (border-radius: 8px, border: 1px solid var(--line), th in --disp 800 12.5px on #1c1c2c, hover #171724).
Highlight certifiable CBME rows with #1f1a1a background, <mark>CERTIFIABLE</mark>, and an interactive skill-verification toggle persisted to local storage / IndexedDB.
Integration Case Chains (.chain):
Cards with border-left: 4px solid [pillar-color], border-radius: 9px, padding: 18px.
Horizontal flex .steps (flex: 1 1 150px, background: #1b1b2a, border-radius: 6px, switching to flex-direction: column under 760px), each showing P# · SM-## in bold 9.5px --mono above the clinical step.
Drug/Intervention Map (.rx) & Speed Reference / Operating Rules (.speed):
.rx grid (minmax(255px, 1fr), gap: 13px) showing intervention name, mechanism summary, and multi-pillar .pill tags.
.speed grid (minmax(300px, 1fr), gap: 15px) with border-top: 3px solid [pillar-color] rendering the 8-item rapid-recall <ol> list and the single-sentence Operating Rules.
Integrated MEDTRIX Quiz & Progress Tracking:
Connect MCQs (data/mcqs/<subject_id>.json) to Pillar IDs, Sub-module IDs, and CBME codes.
Persist question attempts, accuracy %, bookmark flags, spaced-repetition intervals, and read sub-modules locally (IndexedDB / localStorage with JSON export/import backup) so the entire app works 100% offline as an installable PWA.
