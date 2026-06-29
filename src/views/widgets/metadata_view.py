from __future__ import annotations

import html
import re

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
except Exception:
    QWebEngineView = None

from src.tools import camel_to_sentence
from src.services.katex_service import KatexService


class MetadataView(QWidget):
    """
    Widget responsable de l'affichage des métadonnées d'un document.

    API publique :
        metadata_view.show_document(document)
        metadata_view.refresh_theme()
    """

    def __init__(self, context, parent=None):
        super().__init__(parent)

        self.context = context

        self.katex_service = KatexService(
            self.context.config.get_path_by_key("katex")
        )

        self._last_body_html = None
        self.last_info_html = None

        layout = QVBoxLayout(self)

        if QWebEngineView is not None:
            self.info_view = QWebEngineView()
            self.info_view.loadFinished.connect(self._on_info_loaded)
            layout.addWidget(self.info_view)

        else:
            label = QLabel()
            label.setWordWrap(True)
            layout.addWidget(label)

            class LabelWrapper:

                def __init__(self, widget):
                    self.widget = widget

                def setHtml(self, html_content, base_url=None):
                    try:
                        self.widget.setText(html_content)
                    except Exception:
                        text = re.sub(r"<[^>]+>", "", html_content)
                        self.widget.setText(text)

            self.info_view = LabelWrapper(label)

    # ==========================================================
    # API PUBLIQUE
    # ==========================================================

    def show_document(self, document: dict):
        """
        Affiche les métadonnées d'un document.
        """

        html_parts = []

        for key, value in document.items():

            if key in {
                "type",
                "id",
                "pdf",
                "preview",
                "tex",
                "enonce",
            }:
                continue

            title = f"<b>{camel_to_sentence(key)} :</b>"

            if isinstance(value, str):

                content = self.katex_service.escape_and_render(value)

                html_parts.append(
                    f"<p>{title} {content}</p>"
                )

            elif isinstance(value, list):

                items = "".join(
                    f"<li>{self.katex_service.escape_and_render(str(v))}</li>"
                    for v in value
                )

                html_parts.append(
                    f"<p>{title}</p><ul>{items}</ul>"
                )

            else:

                html_parts.append(
                    f"<p>{title} {html.escape(str(value))}</p>"
                )

        self._last_body_html = (
            "\n".join(html_parts)
            if html_parts
            else "<p><i>Aucune information</i></p>"
        )

        self._refresh_view()

    def refresh_theme(self):
        """
        À appeler après un changement de thème.
        """
        QTimer.singleShot(0, self._refresh_view)

    # ==========================================================
    # INTERNE
    # ==========================================================

    def _refresh_view(self):

        if not self._last_body_html:
            return

        try:
            palette = self.palette()

            bg_color = (
                palette.color(QPalette.Window).name()
            )

            fg_color = (
                palette.color(QPalette.WindowText).name()
            )

        except Exception:
            bg_color = None
            fg_color = None

        full_html = self.katex_service.wrap_with_katex(
            self._last_body_html,
            bg_color,
            fg_color,
        )

        base = self.context.config.get_path_by_key("katex")

        try:
            base_url = QUrl.fromLocalFile(
                str(base.resolve())
            )
        except Exception:
            base_url = QUrl()

        self.last_info_html = full_html

        try:
            self.info_view.setHtml(
                full_html,
                base_url,
            )
        except Exception:
            pass

    def _on_info_loaded(self, ok: bool):

        if ok:
            return

        print(
            "[MetadataView] QWebEngineView failed to load HTML"
        )

        if self.last_info_html:
            print(self.last_info_html[:2000])