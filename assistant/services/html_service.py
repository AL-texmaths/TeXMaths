from html import escape

def format_locations(locations: list[str]) -> str:
        if not locations:
            return ""

        return "<br>".join(
            f"<span class='location'>{loc.replace('/', ' › ')}</span>"
            for loc in locations
        )

class HtmlService:
    """
    Génération du HTML affiché dans le panneau de prévisualisation.
    """
    def __init__(self):
        self.css = "katex.min.css"
        self.js = "katex.min.js"
        self.render = "contrib/auto-render.min.js"

    def render_catalogue_entry(
        self,
        code: str,
        content: str,
        catalogue: str,
        source_type: str,
        theme: dict,
        locations:list=[]
    ) -> str:
        
        css = self.css
        js = self.js
        render = self.render

        content = escape(content)

        colors = theme.colors

        locations_html = format_locations(locations)

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
    background: {colors.bg};
    color: {colors.fg};
    font-family: "Latin Modern Roman", serif;
    padding: 20px;
    font-size: 18px;
}}

.code {{
    color: {colors.accent};
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 10px;
}}

.meta {{
    color: {colors.fg};
    margin-bottom: 20px;
}}

.content {{
    line-height: 1.6;
}}
hr {{
    border: none;
    border-top: 1px solid {colors.border};
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

<hr>

<div class="locations">
    <b>Emplacements :</b><br>
    {locations_html}
</div>

</body>
</html>
"""

    def render_catalogue_list(
        self,
        content: str,
        theme: dict
    ) -> str:

        colors = theme.colors

        return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">

<link rel="stylesheet" href="{self.css}">
<script src="{self.js}"></script>
<script src="{self.render}"></script>

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
    background: {colors.bg};
    color: {colors.fg};
    font-family: "{colors.font}", serif;
    padding: 20px;
    font-size: 18px;
}}

.item {{
    line-height: 1.6;
}}

b {{
    color: {colors.accent};
}}

hr {{
    border: none;
    border-top: 1px solid {colors.border};
    margin: 10px 0;
}}
</style>

</head>

<body>
<div class="item">{content}</div>
</body>
</html>
"""
    
    def render_document_metadata(
        self,
        body_html: str,
        bg_color=None,
        fg_color=None,
        font=None
    ) -> str:
        
        bg = bg_color or "#ffffff"
        fg = fg_color or "#000000"
        font_family = font.family if font else "Latin Modern Roman"

        return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">

<link rel="stylesheet" href="{self.css}">
<script src="{self.js}"></script>
<script src="{self.render}"></script>

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