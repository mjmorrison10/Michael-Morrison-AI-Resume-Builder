#!/usr/bin/env python3
"""
Resume QA Validator for Michael Morrison AI Resume Builder
==========================================================
Validates generated resumes and cover letters against the canonical rules in:
  - MASTER_AI_DOSSIER.md (Rules of Engagement, dates, banned stats, alias rules)
  - RESUME_TEMPLATE_SPEC.md (format, structure, color/theme rules)
  - COVER_LETTER_DOSSIER.md (cover letter locked preferences, date consistency)

Usage:
  python resume_qa.py BASE_RESUME_production.html --track production --type resume
  python resume_qa.py cover_letter.html --track sales --type cover-letter
  python resume_qa.py resume.html --track production --date-profile DATE_PROFILE.json --date-mode padded

Exit codes:
  0 = all checks passed
  1 = one or more ERROR-level checks failed
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

TRACKS = ["production", "warehouse", "sales", "tech-data", "office"]


# ---------------------------------------------------------------------------
# Rule catalogs (derived from the dossier files)
# ---------------------------------------------------------------------------

# Banned exact phrases / stats. Source: MASTER_AI_DOSSIER.md:10
BANNED_SUBSTRINGS = [
    "1.2M followers",
    "$20k generated",
    "$20,000 generated",
    "$10k",
    "$10,000",
    "110/90 ppm",
    "30-40 bpm",
    "15% incident reduction",
    "8,000/day",
    "8000/day",
    # Internal-only sources that should not appear on resumes
    "20 miles",   # Apple Watch metric source
    "Apple Watch",
]

# Sales-only aliases. Source: MASTER_AI_DOSSIER.md:5 + 10
SALES_ONLY_ALIASES = [
    "wudan",
    "the real world",
    "trw",
    "tate",
    "top g",
    "cobra tate",
    "andrew tate",
    "real world university",
    "wudan industries",
]

# Required resume sections. Source: RESUME_TEMPLATE_SPEC.md:A
RESUME_REQUIRED_SECTIONS = [
    "professional summary",
    "core skills",
    "work experience",
    "education",
]


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# Em dash (—) or en dash (–). Source: RESUME_TEMPLATE_SPEC.md:B
EM_DASH_RE = re.compile(r"[—–]")

# Bad date formats such as "2023 - 2025" or "Jan 2023–Jan 2025".
# Good format is "Apr 2023 to Apr 2025". Source: RESUME_TEMPLATE_SPEC.md:B
BAD_DATE_RE = re.compile(
    r"\b(?:\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})"
    r"\s*[-–—]\s*"
    r"(?:\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}|Present)\b",
    re.IGNORECASE,
)

# Salary / availability phrases. Source: COVER_LETTER_DOSSIER.md: locked preferences
SALARY_RE = re.compile(
    r"\b(?:salary|compensation|pay rate|hourly rate|available immediately|"
    r"start immediately|available to start|notice period)\b",
    re.IGNORECASE,
)

# Street address heuristic. Source: COVER_LETTER_DOSSIER.md: locked preferences
# Matches a number followed by up to 4 words and a street suffix. Keeps false
# positives low by not allowing long spans of text between the number and suffix.
STREET_ADDRESS_RE = re.compile(
    r"\b\d{3,5}\s+[A-Za-z0-9]+(?:\s+[A-Za-z0-9]+){0,3}\s+"
    r"(?:Avenue|Ave|Street|St|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|"
    r"Court|Ct|Place|Pl|Circle|Cir)\b",
    re.IGNORECASE,
)

# Canonical phone format. Source: MASTER_AI_DOSSIER.md:1
PHONE_RE = re.compile(r"\(\d{3}\)\s*\d{3}-\d{4}")


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Issue:
    severity: str
    rule: str
    message: str
    location: str = ""


class ResumeValidator:
    def __init__(self, file_path: str, track: str, doc_type: str = "resume"):
        self.file_path = Path(file_path)
        self.track = track.lower()
        self.doc_type = doc_type.lower()
        self.text = ""
        self.issues: List[Issue] = []
        self._load()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _load(self) -> None:
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        self.text = self.file_path.read_text(encoding="utf-8")

    def _plain_text(self) -> str:
        """Return visible text with tags and excessive whitespace collapsed."""
        t = re.sub(r"<[^>]+>", " ", self.text)
        t = re.sub(r"&nbsp;", " ", t)
        t = re.sub(r"\s+", " ", t)
        return t.strip()

    def _find_offsets(self, phrase: str) -> List[int]:
        """Return all character offsets where phrase appears in plain text."""
        pt = self._plain_text().lower()
        target = phrase.lower()
        offsets = []
        start = 0
        while True:
            idx = pt.find(target, start)
            if idx == -1:
                break
            offsets.append(idx)
            start = idx + 1
        return offsets

    # ------------------------------------------------------------------
    # Checks
    # ------------------------------------------------------------------
    def check_banned_stats(self) -> None:
        """Source: MASTER_AI_DOSSIER.md:10"""
        for phrase in BANNED_SUBSTRINGS:
            for offset in self._find_offsets(phrase):
                self.issues.append(
                    Issue(
                        severity="ERROR",
                        rule="MASTER_AI_DOSSIER.md:10",
                        message=f"Banned stat/phrase found: {phrase!r}",
                        location=f"plain-text offset ~{offset}",
                    )
                )

    def check_alias_usage(self) -> None:
        """Source: MASTER_AI_DOSSIER.md:5 + 10"""
        if self.track == "sales":
            return  # Sales track is allowed to use these names
        pt = self._plain_text().lower()
        for alias in SALES_ONLY_ALIASES:
            # Build a whole-word/phrase regex so "tate" does not match "rotate" or "certificate".
            words = alias.lower().split()
            if len(words) == 1:
                pattern = rf"\b{re.escape(words[0])}\b"
            else:
                pattern = r"\b" + r"\s+".join(re.escape(w) for w in words) + r"\b"
            for m in re.finditer(pattern, pt):
                self.issues.append(
                    Issue(
                        severity="ERROR",
                        rule="MASTER_AI_DOSSIER.md:5 + 10",
                        message=(
                            f"Sales-only alias '{alias}' found on {self.track} track. "
                            "Use 'Valley View Media' for neutral/production applications."
                        ),
                        location=f"plain-text offset ~{m.start()}",
                    )
                )

    def check_em_dashes(self) -> None:
        """Source: RESUME_TEMPLATE_SPEC.md:B"""
        for m in EM_DASH_RE.finditer(self.text):
            self.issues.append(
                Issue(
                    severity="ERROR",
                    rule="RESUME_TEMPLATE_SPEC.md:B",
                    message=(
                        "Em dash or en dash found. Use 'to' for ranges or "
                        "commas/parentheses for asides."
                    ),
                    location=f"file position {m.start()}",
                )
            )

    def check_date_format(self) -> None:
        """Source: RESUME_TEMPLATE_SPEC.md:B"""
        pt = self._plain_text()
        for m in BAD_DATE_RE.finditer(pt):
            self.issues.append(
                Issue(
                    severity="ERROR",
                    rule="RESUME_TEMPLATE_SPEC.md:B",
                    message=(
                        f"Date range uses '-' or dash instead of 'to': {m.group(0)!r}"
                    ),
                    location=f"plain-text offset {m.start()}",
                )
            )

    def check_date_profile(self, profile_path: str, mode: str) -> None:
        """Validate document dates against DATE_PROFILE.json."""
        p = Path(profile_path)
        if not p.exists():
            self.issues.append(
                Issue(
                    severity="WARNING",
                    rule="DATE_PROFILE.json",
                    message=f"Date profile not found: {profile_path}",
                )
            )
            return
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            self.issues.append(
                Issue(
                    severity="WARNING",
                    rule="DATE_PROFILE.json",
                    message=f"Could not parse date profile: {exc}",
                )
            )
            return

        selected = data.get("modes", {}).get(mode)
        if not selected:
            self.issues.append(
                Issue(
                    severity="WARNING",
                    rule="DATE_PROFILE.json",
                    message=f"Mode '{mode}' not found in date profile.",
                )
            )
            return

        pt = self._plain_text()

        # Check for conflicting dates from the opposite mode. A document should
        # never contain a date that belongs to the opposite mode unless it is
        # identical in both modes.
        opposite = "true" if mode == "padded" else "padded"
        opposite_dates = data.get("modes", {}).get(opposite, {})
        for role, conflict in opposite_dates.items():
            if conflict in pt and selected.get(role) != conflict:
                self.issues.append(
                    Issue(
                        severity="ERROR",
                        rule="DATE_PROFILE.json",
                        message=(
                            f"Conflicting date found: '{conflict}' ({role}) matches "
                            f"opposite mode '{opposite}' instead of selected '{mode}'."
                        ),
                    )
                )

    def check_required_sections(self) -> None:
        """Source: RESUME_TEMPLATE_SPEC.md:A (resume) / COVER_LETTER_DOSSIER.md (letter)"""
        pt = self._plain_text().lower()
        if self.doc_type == "resume":
            for section in RESUME_REQUIRED_SECTIONS:
                if section.lower() not in pt:
                    self.issues.append(
                        Issue(
                            severity="ERROR",
                            rule="RESUME_TEMPLATE_SPEC.md:A",
                            message=f"Missing required resume section: {section.title()}",
                        )
                    )
        elif self.doc_type == "cover-letter":
            if not re.search(r"\bdear\b", pt):
                self.issues.append(
                    Issue(
                        severity="ERROR",
                        rule="COVER_LETTER_DOSSIER.md: locked preferences",
                        message="Missing greeting. Expected 'Dear Hiring Manager,' or known hiring manager name.",
                    )
                )
            if "sincerely" not in pt:
                self.issues.append(
                    Issue(
                        severity="ERROR",
                        rule="COVER_LETTER_DOSSIER.md: locked preferences",
                        message="Missing sign-off. Expected 'Sincerely,'.",
                    )
                )

    def check_salary_availability(self) -> None:
        """Source: COVER_LETTER_DOSSIER.md: locked preferences"""
        if self.doc_type != "cover-letter":
            return
        pt = self._plain_text()
        for m in SALARY_RE.finditer(pt):
            self.issues.append(
                Issue(
                    severity="ERROR",
                    rule="COVER_LETTER_DOSSIER.md: locked preferences",
                    message=f"Salary/availability phrase found: {m.group(0)!r}",
                    location=f"plain-text offset {m.start()}",
                )
            )

    def check_street_address(self) -> None:
        """Source: COVER_LETTER_DOSSIER.md: locked preferences"""
        pt = self._plain_text()
        for m in STREET_ADDRESS_RE.finditer(pt):
            self.issues.append(
                Issue(
                    severity="ERROR",
                    rule="COVER_LETTER_DOSSIER.md: locked preferences",
                    message=f"Street address found (only city should be shown): {m.group(0)!r}",
                    location=f"plain-text offset {m.start()}",
                )
            )

    def check_inline_css(self) -> None:
        """Source: RESUME_TEMPLATE_SPEC.md:B"""
        if self.doc_type != "resume":
            return
        if not re.search(r"<style[^>]*>.*?</style>", self.text, re.DOTALL | re.IGNORECASE):
            self.issues.append(
                Issue(
                    severity="WARNING",
                    rule="RESUME_TEMPLATE_SPEC.md:B",
                    message="No inline <style> block found. HTML should be self-contained with inline CSS.",
                )
            )

    def check_phone(self) -> None:
        """Source: MASTER_AI_DOSSIER.md:1"""
        pt = self._plain_text()
        if not PHONE_RE.search(pt):
            self.issues.append(
                Issue(
                    severity="WARNING",
                    rule="MASTER_AI_DOSSIER.md:1",
                    message="Canonical phone number (714) 310-1369 not found in expected format.",
                )
            )

    # ------------------------------------------------------------------
    # Runner
    # ------------------------------------------------------------------
    def validate(self) -> List[Issue]:
        self.check_banned_stats()
        self.check_alias_usage()
        self.check_em_dashes()
        self.check_date_format()
        self.check_required_sections()
        self.check_salary_availability()
        self.check_street_address()
        self.check_inline_css()
        self.check_phone()
        return self.issues

    def report(self) -> int:
        print(f"QA Report for: {self.file_path}")
        print(f"Track: {self.track} | Doc type: {self.doc_type}")
        print("-" * 60)
        if not self.issues:
            print("✅ All checks passed.")
            return 0

        errors = [i for i in self.issues if i.severity == "ERROR"]
        warnings = [i for i in self.issues if i.severity == "WARNING"]
        for issue in self.issues:
            print(f"{issue.severity}: [{issue.rule}] {issue.message}")
            if issue.location:
                print(f"       Location: {issue.location}")
        print("-" * 60)
        print(f"Summary: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1 if errors else 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a generated Michael Morrison resume or cover letter."
    )
    parser.add_argument("file", help="Path to the HTML or markdown file to validate.")
    parser.add_argument(
        "--track",
        choices=TRACKS,
        required=True,
        help="Target track for this application.",
    )
    parser.add_argument(
        "--type",
        choices=["resume", "cover-letter"],
        default="resume",
        help="Document type (default: resume).",
    )
    parser.add_argument(
        "--date-profile",
        help="Path to DATE_PROFILE.json for date consistency checks.",
    )
    parser.add_argument(
        "--date-mode",
        choices=["padded", "true"],
        help="Date mode to validate against the profile.",
    )
    args = parser.parse_args()

    validator = ResumeValidator(args.file, args.track, args.type)
    validator.validate()
    if args.date_profile and args.date_mode:
        validator.check_date_profile(args.date_profile, args.date_mode)
    return validator.report()


if __name__ == "__main__":
    sys.exit(main())
