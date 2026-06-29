import re
import html
from pathlib import Path

from src.tools import KATEX_DIR

def _path_to_uri(path: str | Path) -> str | None:
    try:
        return Path(path).resolve().as_uri()
    except OSError:
        return None

class KatexService:
    
    def escape_and_render(self, text: str):
        """"""
        parts = re.split(r'(\$\$.*?\$\$|\$.+?\$)', text, flags=re.DOTALL)
        out = []
        for part in parts:
            if not part:
                continue
            if part.startswith('$$') and part.endswith('$$') and len(part) >= 4:
                expr = part[2:-2]
                out.append(f'<span class="katex-raw" data-expr="{html.escape(expr, quote=True)}" data-display="1"></span>')
            elif part.startswith('$') and part.endswith('$') and len(part) >= 2:
                expr = part[1:-1]
                out.append(f'<span class="katex-raw" data-expr="{html.escape(expr, quote=True)}" data-display="0"></span>')
            else:
                out.append(html.escape(part).replace('\n', '<br/>'))
        return ''.join(out)

    def wrap_with_katex(self, body_html: str, bg_color=None, fg_color=None) -> str:
        katex_dir = Path(KATEX_DIR)
        css_local = katex_dir / "katex.min.css"
        js_local = katex_dir / "katex.min.js"

        if css_local.exists():
            css_uri = _path_to_uri(css_local)
        else:
            css_uri = "https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css"

        if js_local.exists():
            js_uri = _path_to_uri(js_local)
        else:
            js_uri = "https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"

        bg_css = f"background-color: {bg_color};" if bg_color else ""
        fg_css = f"color: {fg_color};" if fg_color else ""

        return f"""<!doctype html>
    <html>
    <head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="{css_uri}">
    <style>
    /* Prefer Latin Modern if available, otherwise fall back to common serif fonts */
    @font-face {{
    font-family: 'Latin Modern';
    src: local('Latin Modern Roman'), local('Latin Modern'), local('LM Roman');
    font-style: normal;
    }}
    body {{ font-family: 'Latin Modern', 'Times New Roman', Times, serif; font-size:13px; line-height:1.25; margin:8px; {bg_css} {fg_css} }}
    b {{ color: {fg_color or 'inherit'}; }}
    .katex-raw {{ display: inline-block; vertical-align: middle; }}
    /* Make KaTeX rendered math follow surrounding font sizing */
    .katex {{ font-size: 1em; font-family: inherit !important; }}
    .katex * {{ font-family: inherit !important; }}
    </style>
    </head>
    <body>
    {body_html}
    <script src="{js_uri}"></script>
    <script>
    (function(){{
        function renderAll(){{
            document.querySelectorAll('.katex-raw').forEach(function(el){{
                var expr = el.getAttribute('data-expr') || '';
                var display = el.getAttribute('data-display') === '1';
                try {{
                    el.innerHTML = katex.renderToString(expr, {{throwOnError:false, displayMode:display}});
                }} catch(e) {{
                    el.textContent = expr;
                }}
            }});
        }}
        if (typeof katex !== 'undefined') {{
            renderAll();
        }} else {{
            window.addEventListener('load', renderAll);
        }}
    }})();
    </script>
    </body>
    </html>"""