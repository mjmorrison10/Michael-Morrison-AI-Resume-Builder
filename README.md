# Michael Morrison AI Resume Builder

A small, self-contained kit for generating tailored resumes and cover letters with AI. All facts live in one canonical dossier; all formatting rules live in a spec file; the generator and validator keep output consistent and safe.

## What is in this repo

| File | Purpose |
|------|---------|
| `MASTER_AI_DOSSIER.md` | The single source of truth for work history, skills, metrics, dates, and rules. |
| `RESUME_TEMPLATE_SPEC.md` | House style: structure, colors, fonts, date formats, and track-specific rules. |
| `COVER_LETTER_DOSSIER.md` | Cover-letter rules, openings, tone, and locked preferences. |
| `BASE_RESUME_production.html` | Visual gold-standard template for production/warehouse roles. |
| `BASE_RESUME_sales.html` | Template for sales/marketing roles. |
| `BASE_RESUME_tech.html` | Template for tech/data roles. |
| `BASE_RESUME_office.html` | Template for office/admin roles. |
| `signature.png` | Signature image for cover letters. |
| `DATE_PROFILE.json` | Canonical padded and true dates, shared by resume and cover letter. |
| `resume_qa.py` | Validator that catches banned stats, alias misuse, em dashes, date conflicts, and missing sections. |
| `generate_resume.py` | Automation script that assembles the prompt, optionally calls an LLM, and validates the result. |

## Quick start: paste-ready prompt

Upload these four files to any AI chat, then paste:

```text
You are my resume writer. I have uploaded:
- MASTER_AI_DOSSIER.md
- RESUME_TEMPLATE_SPEC.md
- BASE_RESUME_production.html

Write a one-page production resume for this job. Use the dossier facts, apply the padded date rules, no em dashes, and mirror 3-5 keywords from the posting.

[paste job description here]
```

For a cover letter, upload:

- `MASTER_AI_DOSSIER.md`
- `COVER_LETTER_DOSSIER.md`
- `signature.png`

## Quick start: automation script

```bash
# Paste-ready prompt
python3 generate_resume.py --job job_description.txt --track production --prompt-only

# Full automation (requires an OpenAI or Anthropic API key)
python3 generate_resume.py --job job_description.txt --track production \
    --provider openai --model gpt-4o --api-key $OPENAI_API_KEY

# Cover letter
python3 generate_resume.py --job job_description.txt --track sales --type cover-letter \
    --provider anthropic --model claude-3-5-sonnet-20241022
```

Tracks: `production`, `warehouse`, `sales`, `tech-data`, `office`.

## Date modes

- **padded** (default): gap-free display dates that meet the posting's experience requirement. Use this for most quick-apply production and warehouse jobs.
- **true**: background-check-safe dates with an honest gap bridge through Valley View Media. Use this when you know the employer runs deep employment verification.

Set the mode with `--date-mode` in `generate_resume.py`. The same mode is automatically shared with the cover letter so both documents match.

## Validate output

```bash
python3 resume_qa.py generated_resume.html --track production --type resume \
    --date-profile DATE_PROFILE.json --date-mode padded
```

This catches:

- Banned stats and inflated metrics
- Sales-only aliases on non-sales tracks
- Em/en dashes
- Bad date formats (`-` instead of `to`)
- Conflicting dates from the opposite mode
- Missing required sections
- Street addresses or salary/availability mentions in cover letters

## The one rule

**Do not invent facts.** The AI must use only what is in the dossier. Dates, titles, employers, metrics, and duties must be defensible in an interview.

## Modular dossier (advanced)

`MASTER_AI_DOSSIER.md` is assembled from smaller files in `dossier/`:

| File | Contents |
|------|----------|
| `dossier/rules.md` | Rules of engagement, padding rules, do-not-disclose list. |
| `dossier/identity.md` | Contact info and one-line positioning options. |
| `dossier/timeline.md` | Master timeline and display/true date padding rules. |
| `dossier/roles.md` | Role details, achievement bank, skills, and narrative threads. |
| `dossier/ventures.md` | Valley View Media, flipping/reselling, and tech projects. |
| `dossier/sales_history.md` | Deeper sales background for sales-focused resumes. |

After editing any modular file, rebuild the master dossier:

```bash
python3 assemble_dossier.py
```

## License

Use this however you want. It is personal tooling.
