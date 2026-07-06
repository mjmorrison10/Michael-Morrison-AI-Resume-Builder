# ============================================================
# RESUME TEMPLATE SPEC - MICHAEL MORRISON "HOUSE STYLE"
# Paste this WITH the Master AI Dossier so any AI reproduces
# resumes that look and read like the base resume.
# ============================================================
# HOW TO USE:
# "Using the Master AI Dossier for facts and this Template Spec for format,
#  generate a resume for [JOB TITLE]. Output BOTH (a) clean copy-paste text
#  and (b) a single-file HTML using the layout and the color theme that
#  matches the company type below. No em dashes."
# Last updated: 2026-06-15
# ============================================================

## A. STRUCTURE (always, in this order)
1. HEADER BAND (colored): NAME (all caps, bold, large, letter-spaced) +
   role tagline (3 roles separated by bullets) + contact row.
2. PROFESSIONAL SUMMARY: 3-4 sentence paragraph, justified.
3. CORE SKILLS / TECHNICAL SKILLS: two-column grid, 10 items, square/diamond bullets.
4. (TECH track only) PROJECTS: bulleted, bold project name + description.
5. WORK EXPERIENCE: each role = bold "Title - Company, City, CA" on left,
   colored date "pill" on right, then 4-6 bullets. Left timeline rail with a dot.
6. EDUCATION: two columns (Cypress College | Cypress High School).

## B. FORMAT RULES
- One page. Letter size. ~0.45-0.65in margins.
- Fonts: clean sans-serif (Segoe UI / Helvetica / Arial). Body ~10.5px, name ~30px.
- NO em dashes anywhere (use "to" for ranges, commas or "(...)" for asides).
- Date ranges written like "Apr 2023 to Apr 2025" or "2020 to Present".
- DATES: use the DISPLAY/padded dates and PADDING RULES in Master Dossier section 3b by default.
  Default production dates: Hearthside Apr 2023 to Apr 2025; MeriCal May 2025 to May 2026 (no gap).
  Extend Hearthside's START earlier to meet any stated years-of-experience requirement.
  Use TRUE dates only when a "background-check-safe" version is explicitly requested.
- Bullets start with a strong past-tense action verb (Set up, Operated, Cross-trained,
  Trained, Maintained, Identified, Built, Grew, Processed).
- Numbers kept defensible (see dossier banned-stats list). Spell out "approximately"
  for soft numbers.
- City always shown as "City, CA" (or "City, PA" for Edinboro).
- HTML must be a SINGLE self-contained file with inline <style> (no external CSS/fonts/images),
  so it previews correctly in a sandboxed iframe. Use SVG icons inline if any.

## C. COLOR THEME BY COMPANY / ROLE TYPE
Pick the header-band + accent color based on where you're applying:

| Company / role type            | Header band  | Accent (pills/bullets) | Use for |
|--------------------------------|--------------|------------------------|---------|
| Production / Manufacturing / Warehouse | NAVY  #13344b | Blue #2e7fb8       | Machine op, line lead, material handler, food/supplement plants |
| Sales / Marketing / Media      | ROYAL BLUE #0b5394 | Blue #2e7fb8     | Sales, SMM, content, agency, anything where Tate/TRW is an asset |
| Tech / Data / Engineering      | FOREST GREEN #134e3a | Green #207a5c  | Developer, data entry, QA, automation, IT |
| Corporate / Office / Admin / Clerical | SLATE #34495e | Steel #5d7793 | Admin assistant, office, compliance, general corporate |
| Healthcare / Lab / Regulated   | TEAL #0e5b63 | Teal #1c8a94          | HIPAA-adjacent, lab, regulated environments |
| Conservative / unsure          | NAVY #13344b | Blue #2e7fb8          | Safe default |

Text colors stay constant: headings = band color; body = #33393f; company name = #46525c.

## D. CONTENT SELECTION BY TRACK (which jobs to show)
- PRODUCTION (default base): MeriCal + Hearthside + Valley View (bridge). Optionally swap in
  Kirkhill for the "honest" 2-real-jobs version. Drop Products & Go unless warehouse-specific.
- WAREHOUSE/MATERIAL HANDLING: MeriCal + Products & Go (as warehouse) + Hearthside.
- SALES: Valley View/TRW (hero) + Reselling + Gig (as customer/sales experiment) + Technical Edge line.
- TECH/DATA: Projects section + Cofiroute + UFCW + Edinboro IT + Valley View (digital).
- OFFICE/ADMIN/CLERICAL: EukonGroup (compliance) + UFCW + Cofiroute + WIS/RGIS + Valley View.
Always keep it to 3-4 roles for a one-page look. Use the gap-bridge note when there is a date gap.

## E. THE CANONICAL BASE LAYOUT (reference)
The file BASE_RESUME_production.html is the gold-standard reference. New resumes should match its:
- header band proportions, tagline style, contact row with small inline SVG icons,
- section headers with the two-tone underline (band-color chunk then light grey),
- two-column skills grid with small rotated-square bullets,
- experience timeline rail + dot + rounded date pill,
- two-column education footer.
When in doubt, copy BASE_RESUME_production.html and only swap colors (per section C) and content.

## F. QUICK PROMPT TEMPLATE (copy/paste)
"You have my Master AI Dossier (facts) and Resume Template Spec (format).
Generate a resume for this job: [PASTE JOB DESCRIPTION].
- Track: [production / warehouse / sales / tech-data / office].
- Color theme: [pick from section C based on the company].
- Use my facts/duties from the dossier; apply the section 3b DISPLAY dates and PADDING RULES
  (no gaps; extend Hearthside start to meet the years-of-experience requirement in this posting).
- No em dashes; one page; mirror 3-5 keywords from the posting naturally.
Output: (1) plain-text version, then (2) a single self-contained HTML file matching
BASE_RESUME_production.html with the chosen colors."
