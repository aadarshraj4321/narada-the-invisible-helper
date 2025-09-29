import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
# --- NEW IMPORTS ---
from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath
# --- END NEW IMPORTS ---
from PIL import Image, ImageFilter
from PIL.ImageQt import ImageQt
import mss

class GhostWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.old_pos = None
        self.sct = mss.mss()
        self.init_ui()
        self.update_background_blur()
        
        # --- NEW: Animation Setup ---
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300) # Animation duration in milliseconds
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # --- NEW: Start with zero opacity for fade-in ---
        self.setWindowOpacity(0.0) 
        
        self.setGeometry(100, 100, 450, 250)
        self.setWindowTitle("Ghost Assistant")

        self.label = QLabel("I fade in and have rounded corners!\n(Press ESC to fade out)", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setGeometry(0, 0, 450, 250)
        self.label.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-weight: bold;
            background-color: transparent;
            padding: 15px;
        """)

    # --- NEW: Animation Methods ---
    def fade_in(self):
        """Animates the window opacity from 0.0 to 1.0."""
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()

    def fade_out(self):
        """Animates the window opacity from 1.0 to 0.0."""
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.start()
        # Close the app after the animation finishes
        self.animation.finished.connect(self.close)
        
    # --- NEW: Key Press Event to trigger fade-out ---
    def keyPressEvent(self, event):
        """Close the application when the ESC key is pressed."""
        if event.key() == Qt.Key.Key_Escape:
            self.fade_out()

    def update_background_blur(self):
        geo = self.geometry()
        monitor = self.sct.monitors[1]
        capture_area = {"top": geo.y(), "left": geo.x(), "width": geo.width(), "height": geo.height()}
        sct_img = self.sct.grab(capture_area)
        screenshot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        blurred_screenshot = screenshot.filter(ImageFilter.GaussianBlur(radius=15))
        qt_image = ImageQt(blurred_screenshot)
        self.background_pixmap = QPixmap.fromImage(qt_image)
        self.update()

    # --- MODIFIED: Paint Event now creates rounded corners ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing) # For smooth edges

        # Create a rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 15, 15) # 15px radius for corners

        # Set the clipping path of the painter
        painter.setClipPath(path)

        # Draw the blurred background pixmap, which will be clipped to the rounded shape
        if hasattr(self, 'background_pixmap'):
            painter.drawPixmap(self.rect(), self.background_pixmap)

    def moveEvent(self, event):
        self.update_background_blur()
        super().moveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ghost_window = GhostWindow()
    ghost_window.show()
    # --- NEW: Trigger the fade-in animation on startup ---
    ghost_window.fade_in()
    sys.exit(app.exec())