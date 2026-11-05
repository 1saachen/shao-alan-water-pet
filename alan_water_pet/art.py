"""Generated character sprite, with the original Qt drawing retained as a fallback."""
import math
from pathlib import Path

from PySide6.QtCore import QPoint, QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QWidget


def bottle(p: QPainter, x: float, y: float, scale: float = 1.0):
    p.save()
    p.translate(x, y)
    p.scale(scale, scale)
    p.setPen(QPen(QColor("#1d5656"), 2.6))
    p.setBrush(QColor("#dcf5f4"))
    p.drawRoundedRect(QRectF(3, 14, 48, 70), 12, 12)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#86cbd5"))
    p.drawRoundedRect(QRectF(6, 39, 42, 42), 9, 9)
    p.setBrush(QColor("#effcfb"))
    p.drawRoundedRect(QRectF(0, 43, 54, 22), 4, 4)
    p.setPen(QColor("#1d5656"))
    p.setFont(QFont("Microsoft YaHei UI", 8, QFont.Weight.Bold))
    p.drawText(QRectF(0, 43, 54, 22), Qt.AlignmentFlag.AlignCenter, "大 水")
    p.setPen(QPen(QColor("#1d5656"), 2.6))
    p.setBrush(QColor("#c5ed9b"))
    p.drawRoundedRect(QRectF(15, 5, 25, 13), 4, 4)
    p.setPen(QPen(QColor("#ffffff"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawLine(QPointF(13, 25), QPointF(13, 35))
    p.restore()


def draw_character(p: QPainter, rect: QRectF, phase: float = 0, mood: str = "idle"):
    p.save()
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    scale = min(rect.width() / 220, rect.height() / 240)
    p.translate(rect.center().x() - 110 * scale, rect.bottom() - 240 * scale)
    p.scale(scale, scale)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(22, 60, 53, 25))
    p.drawEllipse(QRectF(45, 222, 140, 12))
    p.translate(0, math.sin(phase) * 2)
    outline = QColor("#233732")
    skin = QColor("#f2c1a2")
    p.setPen(QPen(outline, 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                  Qt.PenJoinStyle.RoundJoin))
    # Shoes and trousers.
    p.setBrush(QColor("#687a70"))
    p.drawRoundedRect(QRectF(76, 165, 32, 55), 10, 10)
    p.drawRoundedRect(QRectF(113, 165, 32, 55), 10, 10)
    p.setBrush(QColor("#f8f7ed"))
    p.drawRoundedRect(QRectF(65, 211, 45, 15), 6, 6)
    p.drawRoundedRect(QRectF(114, 211, 43, 15), 6, 6)
    p.setBrush(skin)
    p.drawRoundedRect(QRectF(50, 126, 24, 57), 12, 12)
    # Tee silhouette.
    tee = QPainterPath()
    tee.moveTo(87, 107)
    tee.quadTo(64, 108, 52, 131)
    tee.lineTo(67, 144)
    tee.lineTo(72, 179)
    tee.quadTo(107, 189, 148, 177)
    tee.lineTo(149, 142)
    tee.lineTo(163, 132)
    tee.quadTo(155, 110, 130, 108)
    tee.closeSubpath()
    p.setBrush(QColor("#303b37"))
    p.drawPath(tee)
    p.setPen(QColor("#bce499"))
    p.setFont(QFont("Arial", 8, QFont.Weight.Bold))
    p.drawText(QRectF(80, 143, 54, 18), Qt.AlignmentFlag.AlignCenter, "ALAN")
    p.setPen(QPen(outline, 3.5))
    p.setBrush(skin)
    p.drawRoundedRect(QRectF(96, 91, 29, 29), 10, 10)
    p.drawEllipse(QRectF(58, 54, 19, 26))
    p.drawEllipse(QRectF(143, 54, 18, 26))
    p.drawRoundedRect(QRectF(68, 23, 83, 80), 32, 32)
    # Swept short hair.
    hair = QPainterPath()
    hair.moveTo(68, 66)
    hair.cubicTo(49, 14, 84, 2, 110, 11)
    hair.cubicTo(153, 0, 166, 39, 147, 67)
    hair.lineTo(139, 39)
    hair.quadTo(114, 48, 91, 33)
    hair.quadTo(86, 54, 68, 66)
    p.setBrush(QColor("#30342e"))
    p.drawPath(hair)
    p.setPen(QPen(QColor("#636b5d"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawLine(QPointF(84, 24), QPointF(105, 20))
    p.setPen(QPen(outline, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawLine(QPointF(84, 58), QPointF(97, 56))
    p.drawLine(QPointF(120, 56), QPointF(133, 58))
    blink = math.sin(phase / 3) > .992
    if blink or mood == "happy":
        p.drawArc(QRectF(85, 63, 11, 8), 0, 180 * 16)
        p.drawArc(QRectF(120, 63, 11, 8), 0, 180 * 16)
    else:
        p.drawLine(QPointF(91, 63), QPointF(91, 68))
        p.drawLine(QPointF(125, 63), QPointF(125, 68))
    p.setPen(QPen(QColor("#b37d64"), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawLine(QPointF(108, 68), QPointF(106, 76))
    p.setPen(QPen(outline, 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawArc(QRectF(98, 78, 23, 12), 190 * 16, 150 * 16)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#d5a089"))
    p.drawEllipse(QRectF(81, 75, 10, 5))
    p.drawEllipse(QRectF(128, 75, 10, 5))
    p.setBrush(QColor("#e7eaca"))
    p.drawEllipse(QRectF(61, 73, 4, 4))
    # Big water, slightly lifted on reminder / acknowledgement.
    lift = 10 + math.sin(phase * 2) * 4 if mood in ("drink", "happy") else 0
    bottle(p, 139, 111 - lift, .92)
    p.setPen(QPen(outline, 3.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.setBrush(skin)
    p.drawRoundedRect(QRectF(127, 143 - lift / 2, 34, 19), 9, 9)
    p.restore()


def app_icon() -> QIcon:
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#1768d5"))
    p.drawRoundedRect(QRectF(0, 0, 64, 64), 16, 16)
    bottle(p, 14, 3, .66)
    p.end()
    return QIcon(pixmap)


class Avatar(QWidget):
    clicked = Signal()
    double_clicked = Signal()
    drag_delta = Signal(QPoint)
    drag_finished = Signal()
    context_requested = Signal(QPoint)
    scale_requested = Signal(int)

    def __init__(self, parent=None, interactive=False):
        super().__init__(parent)
        self.phase = 0.0
        self.mood = "idle"
        self.interactive = interactive
        self.sprite = QPixmap(str(Path(__file__).with_name("assets") / "alan-chibi-v1.png"))
        self._wheel_remainder = 0
        self._origin = self._last = None
        self._dragged = False
        self._single = QTimer(self)
        self._single.setSingleShot(True)
        self._single.timeout.connect(self.clicked)
        self._animation = QTimer(self)
        self._animation.timeout.connect(self.animate)
        self._animation.start(70)
        if interactive:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            self.setToolTip("滚轮缩放 · 拖动搬家 · 点击换句话 · 双击面板 · 右键菜单")

    def animate(self):
        if self.isVisible():
            self.phase += .13
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        if self.sprite.isNull():
            draw_character(p, QRectF(self.rect()), self.phase, self.mood)
            return
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        bounds = QRectF(self.rect()).adjusted(5, 6, -5, -5)
        size = self.sprite.size().scaled(bounds.size().toSize(), Qt.AspectRatioMode.KeepAspectRatio)
        lift = math.sin(self.phase * 2) * 3 if self.mood in ("drink", "happy") else 0
        p.translate(bounds.center().x(), bounds.bottom() - size.height() / 2 + math.sin(self.phase) * 2 - lift)
        p.rotate(math.sin(self.phase / 2) * .7)
        p.drawPixmap(QRectF(-size.width() / 2, -size.height() / 2, size.width(), size.height()),
                     self.sprite, QRectF(self.sprite.rect()))

    def wheelEvent(self, event):
        if not self.interactive:
            event.ignore()
            return
        self._wheel_remainder += event.angleDelta().y()
        steps = int(self._wheel_remainder / 120)
        if steps:
            self._wheel_remainder -= steps * 120
            self.scale_requested.emit(steps * 10)
        event.accept()

    def mousePressEvent(self, event):
        if self.interactive and event.button() == Qt.MouseButton.LeftButton:
            self._origin = self._last = event.globalPosition().toPoint()
            self._dragged = False

    def mouseMoveEvent(self, event):
        if self._last is not None:
            current = event.globalPosition().toPoint()
            if self._dragged or (current - self._origin).manhattanLength() > 6:
                self._dragged = True
                self.drag_delta.emit(current - self._last)
                self._last = current

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._last is not None:
            if self._dragged:
                self.drag_finished.emit()
            else:
                self._single.start(250)
            self._last = None

    def mouseDoubleClickEvent(self, event):
        if self.interactive and event.button() == Qt.MouseButton.LeftButton:
            self._single.stop()
            self._last = None
            self.double_clicked.emit()

    def contextMenuEvent(self, event):
        if self.interactive:
            self.context_requested.emit(event.globalPos())
