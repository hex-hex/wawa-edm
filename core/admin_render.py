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

# Scoped stylesheet so the rendered content uses normal content typography
# instead of inheriting the Django admin's global element styles (e.g. the blue
# bar the admin paints behind every <h2>). All rules are namespaced to the
# preview container; theme-aware via admin CSS vars with safe fallbacks.
_PREVIEW_CSS = mark_safe(
    "<style>"
    ".wawa-preview{max-width:48rem;padding:12px 16px;line-height:1.5;overflow:auto;"
    "border:1px solid var(--border-color,#ccc);border-radius:6px;"
    "background:var(--body-bg,#fff);color:var(--body-fg,#333);}"
    ".wawa-preview>:first-child{margin-top:0;}.wawa-preview>:last-child{margin-bottom:0;}"
    ".wawa-preview h1,.wawa-preview h2,.wawa-preview h3,.wawa-preview h4,"
    ".wawa-preview h5,.wawa-preview h6{background:none;margin:.7em 0 .3em;padding:0;"
    "color:inherit;font-weight:600;line-height:1.25;}"
    ".wawa-preview h1{font-size:1.6em;}.wawa-preview h2{font-size:1.35em;}"
    ".wawa-preview h3{font-size:1.15em;}.wawa-preview h4{font-size:1em;}"
    ".wawa-preview p{margin:.5em 0;}"
    ".wawa-preview ul,.wawa-preview ol{margin:.5em 0;padding-left:1.5em;}"
    ".wawa-preview li{margin:.2em 0;}"
    ".wawa-preview a{color:var(--link-fg,#447e9b);}"
    ".wawa-preview code{background:var(--darkened-bg,#f5f5f5);padding:.1em .3em;border-radius:3px;}"
    ".wawa-preview pre{background:var(--darkened-bg,#f5f5f5);padding:.6em .8em;border-radius:4px;overflow:auto;}"
    ".wawa-preview pre code{background:none;padding:0;}"
    ".wawa-preview blockquote{margin:.5em 0;padding-left:1em;color:var(--body-quiet-color,#666);"
    "border-left:3px solid var(--border-color,#ccc);}"
    ".wawa-preview img{max-width:100%;height:auto;}"
    ".wawa-preview table{border-collapse:collapse;}"
    ".wawa-preview th,.wawa-preview td{border:1px solid var(--border-color,#ccc);padding:.3em .6em;}"
    "</style>"
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
        return mark_safe(f'{_PREVIEW_CSS}<div class="wawa-preview">{renderer(value)}</div>')

    _display.short_description = label or source.replace("_", " ").title()
    return _display
