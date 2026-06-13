"""Reusable admin helpers for rendering text fields as read-only previews.

`rendered_field` builds a read-only admin display callable that renders a model
text field as sanitized HTML — either from Markdown (`fmt="markdown"`) or from
raw HTML (`fmt="html"`). Output is always passed through ``nh3`` so untrusted
values (these fields are writable via the public API) can't inject scripts into
the staff admin.
"""

import markdown as _markdown
import nh3
from django.utils.safestring import mark_safe

# Theme-aware container (uses Django admin CSS vars, with safe fallbacks).
_PREVIEW_STYLE = (
    "max-width:48rem;padding:12px 16px;border:1px solid var(--border-color,#e0e0e0);"
    "border-radius:6px;background:var(--body-bg,#fff);color:var(--body-fg,#333);"
    "overflow:auto;"
)
_EMPTY = mark_safe('<span style="color:var(--body-quiet-color,#999)">—</span>')


def render_markdown(text: str) -> str:
    """Render Markdown to sanitized HTML."""
    html = _markdown.markdown(
        text or "",
        extensions=["extra", "sane_lists", "nl2br"],
    )
    return nh3.clean(html)


def render_html(text: str) -> str:
    """Sanitize raw HTML for safe display (scripts/handlers stripped)."""
    return nh3.clean(text or "")


_RENDERERS = {
    "markdown": render_markdown,
    "html": render_html,
}


def rendered_field(source: str, *, fmt: str = "markdown", label: str | None = None):
    """Build a read-only admin display that renders ``source`` as a preview.

    Usage in a ModelAdmin::

        about_preview = rendered_field("about", fmt="markdown", label="About")
        exclude = ("about",)
        readonly_fields = ("about_preview",)
    """
    renderer = _RENDERERS[fmt]

    def _display(self, obj=None):
        value = getattr(obj, source, "") if obj is not None else ""
        if not value:
            return _EMPTY
        return mark_safe(f'<div style="{_PREVIEW_STYLE}">{renderer(value)}</div>')

    _display.short_description = label or source.replace("_", " ").title()
    return _display
