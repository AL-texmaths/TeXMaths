from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout

class FlowLayout(QLayout):
    """A wrapping flow layout for PySide6: places widgets horizontally and wraps to new lines."""
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        self._items = []
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        effectiveSpacing = self.spacing() if self.spacing() >= 0 else 6
        for item in self._items:
            itemSize = item.sizeHint()
            nextX = x + itemSize.width() + effectiveSpacing
            if nextX - effectiveSpacing > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + effectiveSpacing
                nextX = x + itemSize.width() + effectiveSpacing
                lineHeight = 0
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), itemSize))
            x = nextX
            lineHeight = max(lineHeight, itemSize.height())
        return y + lineHeight - rect.y()
