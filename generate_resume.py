#!/usr/bin/env python3
"""
generate_resume.py — Automated resume/cover letter generator
==========================================================
For the Michael Morrison AI Resume Builder.

Reads the canonical dossier, template spec, and the appropriate base HTML,
builds a focused LLM prompt, optionally calls an LLM, validates the result
with resume_qa.py, and renders a PDF if Chrome is available.

Usage examples:
  # Generate a resume for a production job (API call mode)
  python3 generate_resume.py --job job_description.txt --track production \
      --provider openai --model gpt-4o --api-key $OPENAI_API_KEY

  # Assemble the prompt only, for pasting into a chat UI
  python3 generate_resume.py --job job_description.txt --track production --prompt-only

  # Generate a cover letter
  python3 generate_resume.py --job job_description.txt --track sales \
      --type cover-letter --provider anthropic --model claude-3-5-sonnet-20241022

  # Use a custom OpenAI-compatible endpoint
  python3 generate_resume.py --job job_description.txt --track tech-data \
      --provider openai --api-base https://api.openai.com/v1 --model gpt-4o
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import Optional, Tuple


# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent
BUILDER_DIR = REPO_ROOT / "Michael Morrison AI Resume Builder"

DOSSIER = BUILDER_DIR / "MASTER_AI_DOSSIER.md"
RESUME_SPEC = BUILDER_DIR / "RESUME_TEMPLATE_SPEC.md"
COVER_SPEC = BUILDER_DIR / "COVER_LETTER_DOSSIER.md"
DATE_PROFILE = REPO_ROOT / "DATE_PROFILE.json"
QA_SCRIPT = REPO_ROOT / "resume_qa.py"

TRACK_TO_RESUME_BASE = {
    "production": "BASE_RESUME_production.html",
    "warehouse": "BASE_RESUME_production.html",
    "sales": "BASE_RESUME_sales.html",
    "tech-data": "BASE_RESUME_tech.html",
    "office": "BASE_RESUME_office.html",
}

VALID_TRACKS = list(TRACK_TO_RESUME_BASE.keys())
VALID_TYPES = ["resume", "cover-letter"]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a tailored Michael Morrison resume or cover letter.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(__doc__).split("===" * 10)[-1],
    )
    parser.add_argument(
        "--job",
        required=True,
        help="Path to a .txt file containing the job description, or '-' to read from stdin.",
    )
    parser.add_argument(
        "--track",
        choices=VALID_TRACKS,
        required=True,
        help="Target application track.",
    )
    parser.add_argument(
        "--type",
        choices=VALID_TYPES,
        default="resume",
        help="Document type (default: resume).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output directory (default: current working directory).",
    )
    parser.add_argument(
        "--date-mode",
        choices=["padded", "true"],
        default="padded",
        help="Date mode to use (default: padded). See DATE_PROFILE.json.",
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "anthropic"],
        default=None,
        help="LLM provider. Omit to use --prompt-only mode.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model name, e.g. gpt-4o or claude-3-5-sonnet-20241022.",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"),
        help="API key. Falls back to OPENAI_API_KEY or ANTHROPIC_API_KEY env vars.",
    )
    parser.add_argument(
        "--api-base",
        default=None,
        help="Custom API base URL for OpenAI-compatible endpoints.",
    )
    parser.add_argument(
        "--prompt-only",
        action="store_true",
        help="Only assemble and save the prompt; do not call an LLM.",
    )
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Skip PDF rendering even if Chrome is available.",
    )
    parser.add_argument(
        "--no-qa",
        action="store_true",
        help="Skip running resume_qa.py on the generated HTML.",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def read_file(path: Path) -> str:
    if not path.exists():
        print(f"Error: Required file not found: {path}", file=sys.stderr)
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def read_job(job_arg: str) -> str:
    if job_arg == "-":
        return sys.stdin.read().strip()
    p = Path(job_arg)
    if not p.exists():
        print(f"Error: Job description file not found: {p}", file=sys.stderr)
        sys.exit(1)
    return p.read_text(encoding="utf-8").strip()


def load_date_profile(mode: str) -> str:
    """Load DATE_PROFILE.json and return the selected mode as a formatted string."""
    if not DATE_PROFILE.exists():
        print(f"Warning: {DATE_PROFILE} not found; skipping date profile injection.", file=sys.stderr)
        return ""
    try:
        data = json.loads(DATE_PROFILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Error: {DATE_PROFILE} is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    dates = data.get("modes", {}).get(mode)
    if not dates:
        print(f"Error: Date mode '{mode}' not found in {DATE_PROFILE}", file=sys.stderr)
        sys.exit(1)

    lines = [
        f"DATE MODE: {mode}",
        "Use ONLY the dates below for this application. Extend Hearthside's start earlier if needed to meet the posting's years-of-experience requirement, but keep MeriCal start = Hearthside end + 1 month.",
        "",
    ]
    for key, value in dates.items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("Padding rules:")
    for key, value in data.get("padding_rules", {}).items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def make_output_paths(args: argparse.Namespace) -> Tuple[Path, Path, Path]:
    out_dir = Path(args.output) if args.output else Path.cwd()
    out_dir.mkdir(parents=True, exist_ok=True)
    base = f"{args.track}_{args.type}"
    html_path = out_dir / f"{base}.html"
    pdf_path = out_dir / f"{base}.pdf"
    prompt_path = out_dir / f"{base}.prompt.txt"
    return html_path, pdf_path, prompt_path


# ---------------------------------------------------------------------------
# Prompt assembly
# ---------------------------------------------------------------------------

def build_resume_prompt(track: str, job_description: str, date_profile: str) -> str:
    dossier = read_file(DOSSIER)
    spec = read_file(RESUME_SPEC)
    base_file = TRACK_TO_RESUME_BASE[track]
    base_template = read_file(BUILDER_DIR / base_file)

    date_section = f"\nCANONICAL DATES FOR THIS APPLICATION:\n---\n{date_profile}\n---\n" if date_profile else ""

    return f"""You are my resume writer. I have uploaded three reference documents below:

1. MASTER_AI_DOSSIER.md — my facts, dates, metrics, and rules.
2. RESUME_TEMPLATE_SPEC.md — my house style, color themes, and format rules.
3. {base_file} — the exact layout and visual style to copy.

Write a one-page resume tailored to the job description below.

TRACK: {track}

RULES:
- Use ONLY the facts, duties, and metrics in the dossier. Do not invent experience.
- DATES: use the canonical dates below. Follow the dossier section 3b "Display Dates + Padding Rules." Pad by default:
  no gap between Hearthside and MeriCal (MeriCal starts one month after Hearthside ends),
  and extend Hearthside's START date earlier if needed so total production experience
  meets this posting's years-of-experience requirement.
- NO em dashes anywhere. Use "to" for date ranges.
- Pick the color theme from RESUME_TEMPLATE_SPEC.md section C based on this company type.
- Mirror 3 to 5 keywords from the posting naturally.
- Keep every claim defensible.
- Output exactly one HTML file. The HTML must be a single self-contained file with
  ALL CSS inline so it previews offline. Match the structure and proportions of the
  {base_file} template provided below.

JOB DESCRIPTION:
---
{job_description}
---

MASTER_AI_DOSSIER.md:
---
{dossier}
---
{date_section}
RESUME_TEMPLATE_SPEC.md:
---
{spec}
---

{base_file} (copy this structure and colors, swap content):
---
{base_template}
---

Now produce the final HTML resume.
"""


def build_cover_letter_prompt(track: str, job_description: str, date_profile: str) -> str:
    dossier = read_file(DOSSIER)
    spec = read_file(COVER_SPEC)

    date_section = f"\nCANONICAL DATES FOR THIS APPLICATION:\n---\n{date_profile}\n---\n" if date_profile else ""

    return f"""You are my cover letter writer. I have uploaded two reference documents below:

1. MASTER_AI_DOSSIER.md — my facts, dates, and rules.
2. COVER_LETTER_DOSSIER.md — my cover letter rules, openings, examples, and locked preferences.

Write a one-page cover letter for the job below.

TRACK: {track}

RULES:
- Use ONLY facts from the dossiers. No em dashes.
- Match my locked preferences: city only (Cypress, CA) + phone + email, no street address;
  greeting "Dear Hiring Manager," if no name; never mention salary or availability.
- SIGNATURE: sign off "Sincerely," then my typed name. Leave a blank line for a handwritten signature.
- DATES: use the canonical dates below. They must match the resume exactly for this application.
- Tone by track: production = warm and humble; sales = confident and direct;
  tech-data = sharp and technical.
- Mirror 2 to 4 keywords from the posting. One page.

JOB DESCRIPTION:
---
{job_description}
---

MASTER_AI_DOSSIER.md:
---
{dossier}
---
{date_section}
COVER_LETTER_DOSSIER.md:
---
{spec}
---

Now produce the final HTML cover letter. All CSS must be inline.
"""


def build_prompt(doc_type: str, track: str, job_description: str, date_profile: str) -> str:
    if doc_type == "resume":
        return build_resume_prompt(track, job_description, date_profile)
    return build_cover_letter_prompt(track, job_description, date_profile)


# ---------------------------------------------------------------------------
# LLM calls
# ---------------------------------------------------------------------------

def extract_html(content: str) -> str:
    """Try to pull an HTML block out of a markdown-wrapped response."""
    # Look for ```html ... ```
    m = re.search(r"```html\s*(.*?)\s*```", content, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # Look for ``` ... ``` that contains HTML tags
    m = re.search(r"```\s*(.*?)\s*```", content, re.DOTALL)
    if m and "<html" in m.group(1).lower():
        return m.group(1).strip()
    # If it already starts with <html, return as-is
    if re.search(r"<html", content, re.IGNORECASE):
        return content.strip()
    return content.strip()


def call_openai(prompt: str, model: str, api_key: str, api_base: Optional[str]) -> str:
    try:
        import urllib.request
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("urllib is required for API calls") from exc

    base = (api_base or "https://api.openai.com/v1").rstrip("/")
    url = f"{base}/chat/completions"
    payload = {
        "model": model or "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a precise resume and cover letter writer."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result["choices"][0]["message"]["content"]


def call_anthropic(prompt: str, model: str, api_key: str) -> str:
    try:
        import urllib.request
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("urllib is required for API calls") from exc

    url = "https://api.anthropic.com/v1/messages"
    payload = {
        "model": model or "claude-3-5-sonnet-20241022",
        "max_tokens": 4096,
        "temperature": 0.3,
        "system": "You are a precise resume and cover letter writer.",
        "messages": [{"role": "user", "content": prompt}],
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result["content"][0]["text"]


def call_llm(args: argparse.Namespace, prompt: str) -> str:
    if args.provider == "openai":
        return call_openai(prompt, args.model, args.api_key, args.api_base)
    if args.provider == "anthropic":
        return call_anthropic(prompt, args.model, args.api_key)
    raise ValueError(f"Unknown provider: {args.provider}")


# ---------------------------------------------------------------------------
# QA and PDF rendering
# ---------------------------------------------------------------------------

def run_qa(html_path: Path, track: str, doc_type: str, date_mode: str) -> bool:
    if not QA_SCRIPT.exists():
        print(f"Warning: QA script not found at {QA_SCRIPT}, skipping validation.", file=sys.stderr)
        return True
    cmd = [
        sys.executable,
        str(QA_SCRIPT),
        str(html_path),
        "--track",
        track,
        "--type",
        doc_type,
    ]
    if DATE_PROFILE.exists():
        cmd.extend(["--date-profile", str(DATE_PROFILE), "--date-mode", date_mode])
    print(f"Running QA: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0


def find_chrome() -> Optional[str]:
    for name in ["google-chrome", "chromium", "chromium-browser", "chrome", "msedge"]:
        path = shutil.which(name)
        if path:
            return path
    return None


def render_pdf(html_path: Path, pdf_path: Path) -> bool:
    chrome = find_chrome()
    if not chrome:
        print("Chrome/Chromium not found; PDF rendering skipped.")
        return False

    with tempfile.TemporaryDirectory() as tmp:
        cmd = [
            chrome,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--run-all-compositor-stages-before-draw",
            "--print-to-pdf-no-header",
            f"--print-to-pdf={pdf_path}",
            f"file://{html_path.resolve()}",
        ]
        print(f"Rendering PDF: {chrome}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"PDF rendering failed: {result.stderr}", file=sys.stderr)
            return False
    if pdf_path.exists() and pdf_path.stat().st_size > 0:
        print(f"PDF saved: {pdf_path}")
        return True
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    args = parse_args()
    html_path, pdf_path, prompt_path = make_output_paths(args)

    # Validate required inputs
    for req in (DOSSIER, RESUME_SPEC, COVER_SPEC):
        if not req.exists():
            print(f"Error: missing {req}", file=sys.stderr)
            return 1

    job_description = read_job(args.job)
    if not job_description:
        print("Error: job description is empty.", file=sys.stderr)
        return 1

    date_profile = load_date_profile(args.date_mode)
    prompt = build_prompt(args.type, args.track, job_description, date_profile)
    prompt_path.write_text(prompt, encoding="utf-8")
    print(f"Prompt saved: {prompt_path}")

    if args.prompt_only:
        print("Prompt-only mode: no LLM call made. Paste the prompt into your preferred AI chat.")
        return 0

    if not args.provider:
        print("Error: --provider is required unless using --prompt-only.", file=sys.stderr)
        return 1

    if not args.api_key:
        print(
            "Error: API key is required. Set OPENAI_API_KEY / ANTHROPIC_API_KEY "
            "or pass --api-key.",
            file=sys.stderr,
        )
        return 1

    print(f"Calling {args.provider} ({args.model or 'default'})...")
    try:
        raw_output = call_llm(args, prompt)
    except Exception as exc:
        print(f"LLM call failed: {exc}", file=sys.stderr)
        return 1

    html = extract_html(raw_output)
    if not html.startswith("<"):
        # The model didn't return HTML; save raw response for debugging.
        debug_path = html_path.with_suffix(".raw.txt")
        debug_path.write_text(raw_output, encoding="utf-8")
        print(f"Warning: LLM did not return valid HTML. Raw response saved to {debug_path}", file=sys.stderr)
        return 1

    html_path.write_text(html, encoding="utf-8")
    print(f"HTML saved: {html_path}")

    qa_ok = True
    if not args.no_qa:
        qa_ok = run_qa(html_path, args.track, args.type, args.date_mode)

    pdf_ok = False
    if not args.no_pdf:
        pdf_ok = render_pdf(html_path, pdf_path)

    if not qa_ok:
        print("\nQA failed. Review the HTML before using it.", file=sys.stderr)
        return 1

    print("\n✅ Generation complete.")
    print(f"   HTML: {html_path}")
    if pdf_ok:
        print(f"   PDF:  {pdf_path}")
    else:
        print(f"   PDF:  not rendered (open the HTML in a browser and choose Print > Save as PDF)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
