from __future__ import annotations
import re


class KatexService:
    """
    Service KaTeX basé sur auto-render (comme ton HtmlService).
    """

    _INLINE_PATTERN = re.compile(r"\$(.+?)\$", re.DOTALL)

    def __init__(self, katex_base_path):
        self.base_path = katex_base_path

    def wrap_with_katex(
        self,
        body_html: str,
        bg_color=None,
        fg_color=None,
        font=None
    ) -> str:

        css = "katex.min.css"
        js = "katex.min.js"
        render = "contrib/auto-render.min.js"

        bg = bg_color or "#ffffff"
        fg = fg_color or "#000000"
        font_family = font.family if font else "Latin Modern Roman"

        return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">

<link rel="stylesheet" href="{css}">
<script src="{js}"></script>
<script src="{render}"></script>

<script>
window.onload = function() {{
    if (window.renderMathInElement) {{
        renderMathInElement(document.body, {{
            delimiters: [
                {{ left: "$$", right: "$$", display: true }},
                {{ left: "$", right: "$", display: false }},
                {{ left: "\\\\(", right: "\\\\)", display: false }},
                {{ left: "\\\\[", right: "\\\\]", display: true }}
            ]
        }});
    }} else {{
        console.error("KaTeX not loaded");
    }}
}};
</script>

<style>
body {{
    background: {bg};
    color: {fg};
    font-family: {font_family};
    padding: 12px;
    font-size: 16px;
}}

.katex {{
    font-size: 1.1em;
}}

.item {{
    margin-bottom: 10px;
}}
</style>

</head>

<body>
{body_html}
</body>
</html>
"""