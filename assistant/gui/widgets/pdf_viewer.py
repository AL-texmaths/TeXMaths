from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QWheelEvent, QNativeGestureEvent
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtPdf import QPdfDocument


class ZoomablePdfView(QPdfView):

    MIN_ZOOM = 0.2
    MAX_ZOOM = 5.0

    WHEEL_STEP = 1.12
    GESTURE_SENSITIVITY = 2.5  # ajuste si trop lent/rapide

    # Modes d'adaptation disponibles pour le zoom par défaut
    FIT_WIDTH = "fit_width"
    FIT_PAGE = "fit_page"

    _ZOOM_MODES = {
        FIT_WIDTH: QPdfView.ZoomMode.FitToWidth,
        FIT_PAGE: QPdfView.ZoomMode.FitInView,
    }

    def __init__(self, parent=None, fit_mode=FIT_WIDTH):
        super().__init__(parent)
        self._wheel_acc = 0.0
        self.fit_mode = fit_mode

    # -------------------------
    # API unique
    # -------------------------

    def set_zoom(self, factor: float):
        factor = max(self.MIN_ZOOM, min(self.MAX_ZOOM, factor))
        self.setZoomMode(QPdfView.ZoomMode.Custom)
        self.setZoomFactor(factor)

    def set_fit_mode(self, fit_mode: str):
        """Change le mode d'adaptation par défaut (largeur ou page entière) et l'applique."""
        self.fit_mode = fit_mode
        self.reset_zoom()

    def reset_zoom(self):
        """Réinitialise le zoom au mode d'adaptation configuré et vide l'accumulateur."""
        self._wheel_acc = 0.0
        self.setZoomMode(self._ZOOM_MODES.get(self.fit_mode, QPdfView.ZoomMode.FitToWidth))

    # -------------------------
    # Wheel (Ctrl + scroll)
    # -------------------------

    def wheelEvent(self, event: QWheelEvent):

        if not (event.modifiers() & Qt.ControlModifier):
            super().wheelEvent(event)
            return

        delta = event.angleDelta().y() or event.pixelDelta().y()

        if event.inverted():
            delta = -delta

        self._wheel_acc += delta

        if self._wheel_acc > 30:
            self.set_zoom(self.zoomFactor() * self.WHEEL_STEP)
            self._wheel_acc = 0

        elif self._wheel_acc < -30:
            self.set_zoom(self.zoomFactor() / self.WHEEL_STEP)
            self._wheel_acc = 0

        event.accept()

    # -------------------------
    # Native gestures (pinch Linux/Wayland)
    # -------------------------

    def event(self, event):

        if event.type() == QEvent.Type.NativeGesture:
            return self._native_gesture(event)

        return super().event(event)

    def _native_gesture(self, event: QNativeGestureEvent):

        if event.gestureType() != Qt.NativeGestureType.ZoomNativeGesture:
            return False

        value = event.value()

        # IMPORTANT :
        # valeur déjà normalisée et cumulative
        factor = 1.0 + (value * self.GESTURE_SENSITIVITY)

        self.set_zoom(self.zoomFactor() * factor)

        return True

class PdfViewerWidget(QWidget):

    def __init__(self, fit_mode=ZoomablePdfView.FIT_WIDTH):

        super().__init__()

        self.document = QPdfDocument()

        self.view = ZoomablePdfView(fit_mode=fit_mode)

        self.view.setDocument(self.document)

        # Connecter le signal du document pour réinitialiser le zoom à chaque chargement
        self.document.pageCountChanged.connect(self.view.reset_zoom)

        self.view.setPageMode(QPdfView.PageMode.MultiPage)
        self.view.reset_zoom()

        layout = QVBoxLayout(self)

        layout.addWidget(self.view)

    def load_pdf(self, pdf_path: str | Path):
        self.document.load(str(pdf_path))

    def set_fit_mode(self, fit_mode: str):
        """Change le mode d'adaptation du zoom (largeur de page ou page entière)."""
        self.view.set_fit_mode(fit_mode)

    def clear(self):
        self.document.close()