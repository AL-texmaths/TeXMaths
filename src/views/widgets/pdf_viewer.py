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

    def __init__(self, parent=None):
        super().__init__(parent)
        self._wheel_acc = 0.0

    # -------------------------
    # API unique
    # -------------------------

    def set_zoom(self, factor: float):
        factor = max(self.MIN_ZOOM, min(self.MAX_ZOOM, factor))
        self.setZoomMode(QPdfView.ZoomMode.Custom)
        self.setZoomFactor(factor)

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

    def __init__(self):

        super().__init__()

        self.document = QPdfDocument()

        self.view = ZoomablePdfView()

        self.view.setDocument(
            self.document
        )

        self.view.setPageMode(QPdfView.PageMode.MultiPage)
        self.view.setZoomMode(QPdfView.ZoomMode.FitToWidth)

        layout = QVBoxLayout(self)

        layout.addWidget(self.view)

    def load_pdf(self, pdf_path):
        self.document.load(pdf_path)

    def clear(self):
        self.document.close()