import re
from dataclasses import dataclass

from ..models import Contact


STORY_PLACEHOLDERS = {"tbd", "n/a", "todo", "none", "unknown", "-", "—"}

STORY_MIN_CHARS = 80
BEHAVIOR_MIN_CHARS = 30


@dataclass(frozen=True)
class ContactInvestigationReport:
    waiting: bool
    story_missing: bool
    story_too_short: bool
    story_invalid: bool
    behavior_missing: bool
    behavior_too_short: bool

    def reasons(self) -> list[str]:
        out: list[str] = []
        if self.story_missing:
            out.append("story_missing")
        if self.story_too_short:
            out.append("story_too_short")
        if self.story_invalid:
            out.append("story_invalid")
        if self.behavior_missing:
            out.append("behavior_missing")
        if self.behavior_too_short:
            out.append("behavior_too_short")
        return out


def _stripped(text: str | None) -> str:
    return (text or "").strip()


def _story_is_invalid(story: str) -> bool:
    stripped = _stripped(story)
    if not stripped:
        return False
    if stripped.lower() in STORY_PLACEHOLDERS:
        return True
    return False


def evaluate_contact(contact: Contact) -> ContactInvestigationReport:
    story = _stripped(contact.story)
    behavior = _stripped(contact.behavior)

    story_missing = not story
    story_too_short = (not story_missing) and len(story) < STORY_MIN_CHARS
    story_invalid = _story_is_invalid(story)

    behavior_missing = not behavior
    behavior_too_short = (
        (not behavior_missing) and len(behavior) < BEHAVIOR_MIN_CHARS
    )

    waiting = (
        story_missing
        or story_too_short
        or story_invalid
        or behavior_missing
        or behavior_too_short
    )
    return ContactInvestigationReport(
        waiting=waiting,
        story_missing=story_missing,
        story_too_short=story_too_short,
        story_invalid=story_invalid,
        behavior_missing=behavior_missing,
        behavior_too_short=behavior_too_short,
    )