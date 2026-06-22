import os
import json
from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Signal


class LatexPreviewWidget(QWidget):
    """Widget léger pour prévisualiser rapidement du LaTeX via KaTeX.

    - Charge une page HTML minimale contenant KaTeX (locale si disponible,
      sinon CDN).
    - Expose `set_latex(latex_str)` qui met à jour le contenu via
      `runJavaScript`, sans recharger la page complète.
    """

    ready = Signal()

    def __init__(self, katex_path: str | Path | None = None, parent=None):
        super().__init__(parent)

        self.view = QWebEngineView(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        self._ready = False
        self._pending = None

        # Résolution du chemin KaTeX (si non fourni, lire CONFIG au runtime)
        if katex_path is None:
            try:
                from src.tools import CONFIG

                katex_cfg = CONFIG.get("katex", "")
            except Exception:
                katex_cfg = ""
            katex_path = Path(katex_cfg)

        if katex_path and not katex_path.is_absolute():
            katex_path = (Path(__file__).resolve().parent.parent / katex_path).resolve()

        use_local = katex_path and katex_path.exists()

        if use_local:
            base_url = QUrl.fromLocalFile(str(katex_path) + os.sep)
            css_href = "katex.min.css"
            katex_js = "katex.min.js"
            auto_js = "contrib/auto-render.min.js"
        else:
            base_url = QUrl("about:blank")
            css_href = "https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css"
            katex_js = "https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"
            auto_js = "https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="{css_href}">
<script defer src="{katex_js}"></script>
<script defer src="{auto_js}"></script>
<style>
  body {{ margin: 0; padding: 6px; font-size: 18px; color: #222; }}
  .katex-display {{ margin: 6px 0; }}
</style>
<script>
function renderLatex(latex) {{
    var container = document.getElementById('katex-container');
    container.innerHTML = latex || '';
    try {{
        renderMathInElement(container, {{
            delimiters: [
                {{left: '$$', right: '$$', display: true}},
                {{left: '$', right: '$', display: false}}
            ]
        }});
    }} catch (err) {{
        console.error('KaTeX render error', err);
        container.textContent = latex;
    }}
}}
document.addEventListener('DOMContentLoaded', function() {{ window._latex_ready = true; }});
</script>
</head>
<body>
<div id="katex-container"></div>
</body>
</html>
"""

        self.view.setHtml(html, base_url)
        self.view.loadFinished.connect(self._on_load_finished)

    def _on_load_finished(self, ok: bool):
        self._ready = ok
        if self._pending is not None:
            self.set_latex(self._pending)
            self._pending = None
        self.ready.emit()

    def set_latex(self, latex: str):
        """Met à jour l'énoncé LaTeX affiché.

        Si la page n'est pas encore prête, on met en file d'attente.
        """
        if not self._ready:
            self._pending = latex
            return

        payload = json.dumps(latex)
        js = f"renderLatex({payload});"
        try:
            self.view.page().runJavaScript(js)
        except Exception:
            # Ne pas planter l'application si JS échoue
            pass
