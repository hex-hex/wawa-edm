import re
from dataclasses import dataclass

from ..models import Company


ABOUT_PLACEHOLDERS = {"tbd", "n/a", "todo", "none", "unknown", "-", "—"}

ABOUT_MIN_WORDS = 90

_WORD_RE = re.compile(r"[A-Za-z]+")


@dataclass(frozen=True)
class InvestigationReport:
    waiting: bool
    no_contact: bool
    about_missing: bool
    about_too_short: bool
    about_invalid: bool

    def reasons(self) -> list[str]:
        out: list[str] = []
        if self.no_contact:
            out.append("no_contact")
        if self.about_missing:
            out.append("about_missing")
        if self.about_too_short:
            out.append("about_too_short")
        if self.about_invalid:
            out.append("about_invalid")
        return out


def _about_meaningful_words(about: str) -> list[str]:
    return _WORD_RE.findall(about or "")


def _about_is_invalid(about: str) -> bool:
    stripped = (about or "").strip()
    if not stripped:
        return False
    if stripped.lower() in ABOUT_PLACEHOLDERS:
        return True
    words = _about_meaningful_words(stripped)
    if not words:
        return True
    return False


def evaluate_company(company: Company) -> InvestigationReport:
    about = (company.about or "").strip()
    about_missing = not about
    words = _about_meaningful_words(about)
    about_too_short = (not about_missing) and len(words) < ABOUT_MIN_WORDS
    about_invalid = _about_is_invalid(about)
    no_contact = len(company.contacts.all()) == 0
    waiting = no_contact or about_missing or about_too_short or about_invalid
    return InvestigationReport(
        waiting=waiting,
        no_contact=no_contact,
        about_missing=about_missing,
        about_too_short=about_too_short,
        about_invalid=about_invalid,
    )