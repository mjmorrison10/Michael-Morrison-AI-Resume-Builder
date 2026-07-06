# HOW TO PROMPT AN AI WITH THIS SYSTEM
### Michael Morrison - Resume & Cover Letter Generation Kit
### Last updated: 2026-06-15

This file tells you (1) exactly which files to upload to an AI, and (2) the exact prompt
to paste. It is written so you can hand the AI a small, focused set of files and get a
tailored resume or cover letter with no confusion.

================================================================
## QUICK ANSWER TO YOUR QUESTION (do I upload the base resume or the .py?)
================================================================
- You do NOT need to upload the .py build scripts OR the finished resume files to
  GENERATE new tailored content. The AI reads the 3 TEXT dossiers and writes the resume.
- The .py scripts are only for re-rendering pretty PDF/Word files on THIS workspace.
  A normal chat AI cannot run them, so skip them for generation.
- DO upload ONE example resume so the AI can copy the look: upload
  **BASE_RESUME_production.html** (it is the visual gold standard and is plain text the AI can read).
  You do NOT also need build_base_resume.py - the HTML is enough.

================================================================
## THE MINIMAL UPLOAD SET (use this - only 4 files)
================================================================
Upload these 4 files, then paste "PROMPT A" (resume) or "PROMPT B" (cover letter):

1. MASTER_AI_DOSSIER.md        <- all your facts, dates, padding rules
2. RESUME_TEMPLATE_SPEC.md     <- the house style + color-by-company rules
3. COVER_LETTER_DOSSIER.md     <- cover letter rules, openings, examples
4. BASE_RESUME_production.html <- the visual reference to copy

That is the whole kit for generation. Four files. Nothing else is required.

If the AI limits you to FEWER files:
- Resume only: upload #1 + #2 + #4  (skip the cover letter dossier).
- Cover letter only: upload #1 + #3 + signature.png (so it can sign the letter).
- Absolute minimum (1 file): upload just #1 (MASTER_AI_DOSSIER.md). It still works;
  the layout/colors just will not be as polished.

FOR COVER LETTERS, ALSO UPLOAD:
- signature.png (found in the assets/ folder). The cover letter prompt tells the AI to
  embed it above my typed name. If you do not upload it, the AI will just use my typed name.

DO NOT upload (not needed for generation, and they eat your file limit):
- Any .py file (resume_engine, build_*, cover_letter_engine) - rendering tools only.
- The other finished resumes/cover letters (.pdf/.docx/.md) - they are OUTPUTS, not inputs.
- The dossier/ folder (01-08) - that is my internal working memory; the facts are already
  summarized inside MASTER_AI_DOSSIER.md. (Only upload a dossier/ file if the AI asks for
  deeper detail on one specific job.)

================================================================
## PROMPT A - GENERATE A TAILORED RESUME (copy/paste this)
================================================================
You are my resume writer. I have uploaded:
- MASTER_AI_DOSSIER.md (my facts + date/padding rules)
- RESUME_TEMPLATE_SPEC.md (my house style + color themes)
- BASE_RESUME_production.html (the visual look to copy)

Write a one-page resume tailored to the job below.

RULES:
- Use ONLY the facts, duties, and metrics in the dossier. Do not invent experience.
- DATES: follow the dossier section 3b "Display Dates + Padding Rules." Pad by default:
  no gap between Hearthside and MeriCal (MeriCal starts one month after Hearthside ends),
  and extend Hearthside's START date earlier if needed so my total production experience
  meets this posting's years-of-experience requirement.
- NO em dashes anywhere. Use "to" for date ranges.
- Pick the color theme from RESUME_TEMPLATE_SPEC.md section C based on this company type.
- Mirror 3 to 5 keywords from the posting naturally.
- Keep every claim defensible (I must be able to explain it in an interview).

OUTPUT (exactly two files, nothing else):
1. One HTML file: a single self-contained resume that matches BASE_RESUME_production.html
   (same layout, with the chosen color theme), with ALL CSS inline so it previews offline.
2. One PDF file: the same resume exported to PDF.
   - If you have a code/file tool, generate the PDF directly and give me the download.
   - If you cannot create a PDF file, tell me clearly and give me the HTML only, plus this
     one-line instruction: "Open the HTML in a browser and choose Print > Save as PDF."
Do NOT output a separate plain-text version unless I ask for it.

TRACK (pick one): [production / warehouse / sales / tech-data / office]
JOB POSTING:
[PASTE THE FULL JOB DESCRIPTION HERE]

================================================================
## PROMPT B - GENERATE A TAILORED COVER LETTER (copy/paste this)
================================================================
You are my cover letter writer. I have uploaded:
- MASTER_AI_DOSSIER.md (my facts + date/padding rules)
- COVER_LETTER_DOSSIER.md (my cover letter rules, openings, and examples)

Write a one-page cover letter for the job below, following COVER_LETTER_DOSSIER.md.

RULES:
- Use ONLY facts from the dossiers. No em dashes.
- Match my locked preferences: city only (Cypress, CA) + phone + email, no street address;
  greeting "Dear Hiring Manager," if no name; never mention salary or availability.
- SIGNATURE: sign off "Sincerely," then place my signature, then my typed name.
  Check whether a file named "signature.png" was uploaded. If yes, insert that image
  above my typed name "Michael Morrison." If signature.png was NOT uploaded, just use the
  typed name and add a blank line for a handwritten signature.
- DATES must match my resume's padded dates (dossier section 3b). If unsure, refer to
  experience in general terms instead of specific years.
- Tone by track: production = warm and humble; sales = confident and direct;
  tech-data = sharp and technical.
- Mirror 2 to 4 keywords from the posting. One page.

OUTPUT (exactly two files, nothing else):
1. One HTML file: a single self-contained cover letter with all CSS inline. If signature.png
   was uploaded, embed it above the typed name.
2. One PDF file: the same cover letter exported to PDF.
   - If you cannot create a PDF, give me the HTML only plus: "Open the HTML in a browser and
     choose Print > Save as PDF."

MY CHOICES FOR THIS JOB:
- Track: [production / sales / tech-data]
- Opening style: [gap-addressing / no-mention]
- Length: [short / standard]
- Emphasize: [anything specific, e.g. "they stress safety" - or write "nothing specific"]
- Company / hiring manager name: [name if known, else "unknown"]

JOB POSTING:
[PASTE THE FULL JOB DESCRIPTION HERE]

================================================================
## AFTER THE AI GIVES YOU THE RESULT
================================================================
- You should get exactly TWO files: one HTML and one PDF.
- If the AI could not make the PDF itself, open the HTML in a browser and use
  Print > Save as PDF to create it.
- If you forgot to upload signature.png for a cover letter, either re-run with it attached
  or paste the signature in above the typed name yourself.
- Always sanity-check that the dates on the resume and the cover letter MATCH for the
  same application.

================================================================
## REMINDER: TWO DATE MODES
================================================================
- DEFAULT = padded display dates (gap-free, meets experience requirements). Use for most
  quick-apply production jobs.
- If a job runs a deep background / employment-verification check, ask the AI for the
  "background-check-safe version" - it will switch to my true dates and bridge the gap
  honestly with Valley View Media (2020-present) and Kirkhill (2019-2020).
