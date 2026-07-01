from html import escape


class HtmlService:
    """
    Génération du HTML affiché dans le panneau de prévisualisation.
    """

    @staticmethod
    def render_entry(
        code: str,
        content: str,
        catalogue: str,
        source_type: str,
        theme: dict
    ) -> str:
        
        css = "katex.min.css"
        js = "katex.min.js"
        render = "contrib/auto-render.min.js"

        content = escape(content)

        t = theme

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
    renderMathInElement(document.body, {{
        delimiters: [
            {{ left: "$$", right: "$$", display: true }},
            {{ left: "$", right: "$", display: false }},
            {{ left: "\\\\(", right: "\\\\)", display: false }},
            {{ left: "\\\\[", right: "\\\\]", display: true }}
        ]
    }});
}};
</script>

<style>
body {{
    background: {t['bg']};
    color: {t['fg']};
    font-family: "Latin Modern Roman", serif;
    padding: 20px;
    font-size: 18px;
}}

.code {{
    color: {t['accent']};
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 10px;
}}

.meta {{
    color: {t['fg']};
    margin-bottom: 20px;
}}

.content {{
    line-height: 1.6;
}}
hr {{
    border: none;
    border-top: 1px solid {t["border"]};
    margin: 20px 0;
}}
</style>

</head>

<body>
<div class="code">{code}</div>

<div class="meta">
<b>Catalogue :</b> {catalogue}<br>
<b>Type :</b> {source_type}
</div>

<hr>

<div class="content">{content}</div>
</body>
</html>
"""

    @staticmethod
    def render_list(
        content: str,
        theme: dict
    ) -> str:

        css = "katex.min.css"
        js = "katex.min.js"
        render = "contrib/auto-render.min.js"

        t = theme

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
    renderMathInElement(document.body, {{
        delimiters: [
            {{ left: "$$", right: "$$", display: true }},
            {{ left: "$", right: "$", display: false }},
            {{ left: "\\\\(", right: "\\\\)", display: false }},
            {{ left: "\\\\[", right: "\\\\]", display: true }}
        ]
    }});
}};
</script>

<style>
body {{
    background: {t['bg']};
    color: {t['fg']};
    font-family: "{t['font']}", serif;
    padding: 20px;
    font-size: 18px;
}}

.item {{
    line-height: 1.6;
}}

b {{
    color: {t['accent']};
}}

hr {{
    border: none;
    border-top: 1px solid {t["border"]};
    margin: 10px 0;
}}
</style>

</head>

<body>
<div class="item">{content}</div>
</body>
</html>
"""