"""
Modern flat vector icons for Volatility3 GUI.
Uses QPainter to render SVG-style paths as QIcon objects.
Designed to match Lucide icon aesthetic - simple, clean, 24x24 stroked paths.
"""

from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QPainterPath
from PyQt6.QtCore import Qt, QRectF, QPointF


class ModernIcons:
    """Modern flat icons using QPainter paths rendered to QIcon."""

    # Default colors from Tokyo Night theme
    DEFAULT_COLOR = "#c0caf5"
    ACCENT_COLOR = "#7aa2f7"

    @staticmethod
    def _create_icon_from_painter(paint_func, color: str = None, size: int = 20) -> QIcon:
        """Create a QIcon by painting with the given function."""
        if color is None:
            color = ModernIcons.DEFAULT_COLOR

        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor(color))
        pen.setWidthF(1.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Scale factor for drawing (leave padding)
        margin = 2
        scale = (size - margin * 2) / 24.0
        painter.translate(margin, margin)
        painter.scale(scale, scale)

        paint_func(painter)
        painter.end()

        return QIcon(pixmap)

    @staticmethod
    def folder_open(color: str = None) -> QIcon:
        """Folder open icon."""
        def paint(p: QPainter):
            # Folder back
            path = QPainterPath()
            path.moveTo(2, 6)
            path.lineTo(2, 18)
            path.lineTo(20, 18)
            path.lineTo(22, 8)
            path.lineTo(10, 8)
            path.lineTo(8, 6)
            path.closeSubpath()
            p.drawPath(path)
            # Tab
            p.drawLine(QPointF(2, 6), QPointF(8, 6))
            p.drawLine(QPointF(8, 6), QPointF(10, 8))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def file(color: str = None) -> QIcon:
        """File/document icon."""
        def paint(p: QPainter):
            path = QPainterPath()
            path.moveTo(6, 2)
            path.lineTo(6, 22)
            path.lineTo(18, 22)
            path.lineTo(18, 8)
            path.lineTo(12, 2)
            path.closeSubpath()
            p.drawPath(path)
            # Folded corner
            p.drawLine(QPointF(12, 2), QPointF(12, 8))
            p.drawLine(QPointF(12, 8), QPointF(18, 8))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def save(color: str = None) -> QIcon:
        """Save/disk icon."""
        def paint(p: QPainter):
            # Outer rectangle
            path = QPainterPath()
            path.addRoundedRect(QRectF(3, 3, 18, 18), 2, 2)
            p.drawPath(path)
            # Floppy slot
            p.drawRect(QRectF(7, 3, 10, 5))
            # Label area
            p.drawRect(QRectF(6, 12, 12, 6))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def settings(color: str = None) -> QIcon:
        """Settings/gear icon."""
        def paint(p: QPainter):
            # Simplified gear with 6 teeth
            import math
            center = QPointF(12, 12)
            outer_r = 9
            inner_r = 5

            # Draw gear teeth as lines radiating out
            for i in range(6):
                angle = i * math.pi / 3
                x1 = center.x() + inner_r * math.cos(angle)
                y1 = center.y() + inner_r * math.sin(angle)
                x2 = center.x() + outer_r * math.cos(angle)
                y2 = center.y() + outer_r * math.sin(angle)
                p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

            # Center circle
            p.drawEllipse(center, 4, 4)
            # Outer circle
            p.drawEllipse(center, 7, 7)
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def search(color: str = None) -> QIcon:
        """Search/magnifying glass icon."""
        def paint(p: QPainter):
            # Circle
            p.drawEllipse(QRectF(3, 3, 12, 12))
            # Handle
            p.drawLine(QPointF(14, 14), QPointF(21, 21))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def process(color: str = None) -> QIcon:
        """Process/CPU icon."""
        def paint(p: QPainter):
            # Center square (CPU)
            p.drawRect(QRectF(6, 6, 12, 12))
            # Pins - top
            p.drawLine(QPointF(9, 3), QPointF(9, 6))
            p.drawLine(QPointF(12, 3), QPointF(12, 6))
            p.drawLine(QPointF(15, 3), QPointF(15, 6))
            # Pins - bottom
            p.drawLine(QPointF(9, 18), QPointF(9, 21))
            p.drawLine(QPointF(12, 18), QPointF(12, 21))
            p.drawLine(QPointF(15, 18), QPointF(15, 21))
            # Pins - left
            p.drawLine(QPointF(3, 9), QPointF(6, 9))
            p.drawLine(QPointF(3, 12), QPointF(6, 12))
            p.drawLine(QPointF(3, 15), QPointF(6, 15))
            # Pins - right
            p.drawLine(QPointF(18, 9), QPointF(21, 9))
            p.drawLine(QPointF(18, 12), QPointF(21, 12))
            p.drawLine(QPointF(18, 15), QPointF(21, 15))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def network(color: str = None) -> QIcon:
        """Network/globe icon."""
        def paint(p: QPainter):
            # Outer circle
            p.drawEllipse(QRectF(2, 2, 20, 20))
            # Horizontal line
            p.drawLine(QPointF(2, 12), QPointF(22, 12))
            # Vertical ellipse
            p.drawEllipse(QRectF(8, 2, 8, 20))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def registry(color: str = None) -> QIcon:
        """Registry/database icon."""
        def paint(p: QPainter):
            # Three stacked ellipses (database cylinders)
            p.drawEllipse(QRectF(3, 3, 18, 6))
            p.drawEllipse(QRectF(3, 9, 18, 6))
            p.drawEllipse(QRectF(3, 15, 18, 6))
            # Side lines
            p.drawLine(QPointF(3, 6), QPointF(3, 18))
            p.drawLine(QPointF(21, 6), QPointF(21, 18))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def timeline(color: str = None) -> QIcon:
        """Timeline/calendar icon."""
        def paint(p: QPainter):
            # Calendar body
            p.drawRoundedRect(QRectF(3, 5, 18, 16), 2, 2)
            # Top line
            p.drawLine(QPointF(3, 9), QPointF(21, 9))
            # Hooks
            p.drawLine(QPointF(8, 3), QPointF(8, 7))
            p.drawLine(QPointF(16, 3), QPointF(16, 7))
            # Some dots for dates
            p.drawPoint(QPointF(7, 13))
            p.drawPoint(QPointF(12, 13))
            p.drawPoint(QPointF(17, 13))
            p.drawPoint(QPointF(7, 17))
            p.drawPoint(QPointF(12, 17))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def malware(color: str = None) -> QIcon:
        """Malware/bug icon."""
        def paint(p: QPainter):
            # Body (ellipse)
            p.drawEllipse(QRectF(7, 8, 10, 12))
            # Head
            p.drawEllipse(QRectF(9, 3, 6, 6))
            # Legs - left
            p.drawLine(QPointF(7, 11), QPointF(3, 8))
            p.drawLine(QPointF(7, 14), QPointF(3, 14))
            p.drawLine(QPointF(7, 17), QPointF(3, 20))
            # Legs - right
            p.drawLine(QPointF(17, 11), QPointF(21, 8))
            p.drawLine(QPointF(17, 14), QPointF(21, 14))
            p.drawLine(QPointF(17, 17), QPointF(21, 20))
            # Antennae
            p.drawLine(QPointF(10, 4), QPointF(7, 1))
            p.drawLine(QPointF(14, 4), QPointF(17, 1))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def ioc(color: str = None) -> QIcon:
        """IOC/target icon."""
        def paint(p: QPainter):
            # Concentric circles
            p.drawEllipse(QRectF(2, 2, 20, 20))
            p.drawEllipse(QRectF(6, 6, 12, 12))
            p.drawEllipse(QRectF(10, 10, 4, 4))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def virustotal(color: str = None) -> QIcon:
        """VirusTotal/shield-scan icon."""
        def paint(p: QPainter):
            # Shield shape
            path = QPainterPath()
            path.moveTo(12, 2)
            path.lineTo(20, 6)
            path.lineTo(20, 12)
            path.quadTo(20, 18, 12, 22)
            path.quadTo(4, 18, 4, 12)
            path.lineTo(4, 6)
            path.closeSubpath()
            p.drawPath(path)
            # Check mark inside
            p.drawLine(QPointF(8, 12), QPointF(11, 15))
            p.drawLine(QPointF(11, 15), QPointF(16, 9))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def logs(color: str = None) -> QIcon:
        """Logs/list icon."""
        def paint(p: QPainter):
            # Lines
            p.drawLine(QPointF(3, 6), QPointF(21, 6))
            p.drawLine(QPointF(3, 10), QPointF(21, 10))
            p.drawLine(QPointF(3, 14), QPointF(21, 14))
            p.drawLine(QPointF(3, 18), QPointF(21, 18))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def queue(color: str = None) -> QIcon:
        """Queue/layers icon."""
        def paint(p: QPainter):
            # Three stacked rectangles
            p.drawRect(QRectF(4, 2, 16, 4))
            p.drawRect(QRectF(4, 9, 16, 4))
            p.drawRect(QRectF(4, 16, 16, 4))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def chart(color: str = None) -> QIcon:
        """Chart icon."""
        def paint(p: QPainter):
            # Bars
            p.drawRect(QRectF(4, 14, 4, 7))
            p.drawRect(QRectF(10, 8, 4, 13))
            p.drawRect(QRectF(16, 3, 4, 18))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def export(color: str = None) -> QIcon:
        """Export/upload icon."""
        def paint(p: QPainter):
            # Arrow up
            p.drawLine(QPointF(12, 3), QPointF(12, 15))
            p.drawLine(QPointF(12, 3), QPointF(7, 8))
            p.drawLine(QPointF(12, 3), QPointF(17, 8))
            # Base
            path = QPainterPath()
            path.moveTo(4, 14)
            path.lineTo(4, 20)
            path.lineTo(20, 20)
            path.lineTo(20, 14)
            p.drawPath(path)
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def report(color: str = None) -> QIcon:
        """Report/document with lines icon."""
        def paint(p: QPainter):
            # Document outline
            path = QPainterPath()
            path.moveTo(6, 2)
            path.lineTo(6, 22)
            path.lineTo(18, 22)
            path.lineTo(18, 8)
            path.lineTo(12, 2)
            path.closeSubpath()
            p.drawPath(path)
            # Folded corner
            p.drawLine(QPointF(12, 2), QPointF(12, 8))
            p.drawLine(QPointF(12, 8), QPointF(18, 8))
            # Text lines
            p.drawLine(QPointF(9, 13), QPointF(15, 13))
            p.drawLine(QPointF(9, 16), QPointF(15, 16))
            p.drawLine(QPointF(9, 19), QPointF(13, 19))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def investigate(color: str = None) -> QIcon:
        """Investigate/magnifying glass with user icon."""
        def paint(p: QPainter):
            # Magnifying glass
            p.drawEllipse(QRectF(2, 2, 13, 13))
            p.drawLine(QPointF(13, 13), QPointF(21, 21))
            # Eye inside
            p.drawEllipse(QRectF(5, 6, 7, 4))
            p.drawEllipse(QRectF(7, 7, 2, 2))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def os_info(color: str = None) -> QIcon:
        """OS/Monitor icon."""
        def paint(p: QPainter):
            # Monitor
            p.drawRoundedRect(QRectF(2, 3, 20, 14), 2, 2)
            # Stand
            p.drawLine(QPointF(8, 17), QPointF(8, 20))
            p.drawLine(QPointF(16, 17), QPointF(16, 20))
            p.drawLine(QPointF(6, 20), QPointF(18, 20))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def refresh(color: str = None) -> QIcon:
        """Refresh/reload icon."""
        def paint(p: QPainter):
            # Circular arrow
            path = QPainterPath()
            path.arcMoveTo(QRectF(3, 3, 18, 18), 60)
            path.arcTo(QRectF(3, 3, 18, 18), 60, 240)
            p.drawPath(path)
            # Arrow head
            p.drawLine(QPointF(19, 7), QPointF(19, 12))
            p.drawLine(QPointF(19, 7), QPointF(14, 7))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def play(color: str = None) -> QIcon:
        """Play icon."""
        def paint(p: QPainter):
            path = QPainterPath()
            path.moveTo(6, 4)
            path.lineTo(20, 12)
            path.lineTo(6, 20)
            path.closeSubpath()
            p.drawPath(path)
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def stop(color: str = None) -> QIcon:
        """Stop icon."""
        def paint(p: QPainter):
            p.drawRect(QRectF(5, 5, 14, 14))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def warning(color: str = None) -> QIcon:
        """Warning/triangle icon."""
        if color is None:
            color = "#e0af68"  # Yellow from Tokyo Night
        def paint(p: QPainter):
            path = QPainterPath()
            path.moveTo(12, 3)
            path.lineTo(22, 21)
            path.lineTo(2, 21)
            path.closeSubpath()
            p.drawPath(path)
            # Exclamation
            p.drawLine(QPointF(12, 9), QPointF(12, 15))
            p.drawPoint(QPointF(12, 18))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def success(color: str = None) -> QIcon:
        """Success/check icon."""
        if color is None:
            color = "#9ece6a"  # Green from Tokyo Night
        def paint(p: QPainter):
            # Circle
            p.drawEllipse(QRectF(2, 2, 20, 20))
            # Check
            p.drawLine(QPointF(7, 12), QPointF(10, 16))
            p.drawLine(QPointF(10, 16), QPointF(17, 8))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def error(color: str = None) -> QIcon:
        """Error/X icon."""
        if color is None:
            color = "#f7768e"  # Red from Tokyo Night
        def paint(p: QPainter):
            # Circle
            p.drawEllipse(QRectF(2, 2, 20, 20))
            # X
            p.drawLine(QPointF(8, 8), QPointF(16, 16))
            p.drawLine(QPointF(16, 8), QPointF(8, 16))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def info(color: str = None) -> QIcon:
        """Info icon."""
        if color is None:
            color = "#7dcfff"  # Cyan from Tokyo Night
        def paint(p: QPainter):
            # Circle
            p.drawEllipse(QRectF(2, 2, 20, 20))
            # i
            p.drawLine(QPointF(12, 11), QPointF(12, 17))
            p.drawPoint(QPointF(12, 8))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def add(color: str = None) -> QIcon:
        """Add/plus icon."""
        def paint(p: QPainter):
            p.drawLine(QPointF(12, 5), QPointF(12, 19))
            p.drawLine(QPointF(5, 12), QPointF(19, 12))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def copy(color: str = None) -> QIcon:
        """Copy/clipboard icon."""
        def paint(p: QPainter):
            # Back rectangle
            p.drawRoundedRect(QRectF(8, 8, 12, 14), 1, 1)
            # Front rectangle
            p.drawRoundedRect(QRectF(4, 2, 12, 14), 1, 1)
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def external_link(color: str = None) -> QIcon:
        """External link icon."""
        def paint(p: QPainter):
            # Box
            path = QPainterPath()
            path.moveTo(10, 4)
            path.lineTo(4, 4)
            path.lineTo(4, 20)
            path.lineTo(20, 20)
            path.lineTo(20, 14)
            p.drawPath(path)
            # Arrow
            p.drawLine(QPointF(14, 4), QPointF(20, 4))
            p.drawLine(QPointF(20, 4), QPointF(20, 10))
            p.drawLine(QPointF(10, 14), QPointF(20, 4))
        return ModernIcons._create_icon_from_painter(paint, color)

    @staticmethod
    def dump(color: str = None) -> QIcon:
        """Dump/download icon."""
        def paint(p: QPainter):
            # Arrow down
            p.drawLine(QPointF(12, 3), QPointF(12, 15))
            p.drawLine(QPointF(12, 15), QPointF(7, 10))
            p.drawLine(QPointF(12, 15), QPointF(17, 10))
            # Base
            path = QPainterPath()
            path.moveTo(4, 14)
            path.lineTo(4, 20)
            path.lineTo(20, 20)
            path.lineTo(20, 14)
            p.drawPath(path)
        return ModernIcons._create_icon_from_painter(paint, color)


# Convenience function for getting icon with text (for toolbars/menus)
def get_icon_text(icon_func, text: str, color: str = None) -> tuple:
    """Get an icon and text pair for use in menus.

    Returns:
        Tuple of (QIcon, str) for use with addAction(icon, text, ...)
    """
    return (icon_func(color), text)
