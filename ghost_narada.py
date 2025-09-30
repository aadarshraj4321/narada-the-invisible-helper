import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QMenu, QVBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QAction
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
        
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.0) 
        self.setGeometry(100, 100, 450, 250)
        self.setWindowTitle("Ghost Assistant")

        # --- NEW: UI Mode Management ---
        # QStackedWidget will hold our different UI layouts
        self.stacked_widget = QStackedWidget(self)
        
        # Create the actual widgets for each mode
        self.minimal_mode_widget = self.create_minimal_mode()
        self.card_mode_widget = self.create_card_mode()

        # Add them to the stacked widget
        self.stacked_widget.addWidget(self.minimal_mode_widget)
        self.stacked_widget.addWidget(self.card_mode_widget)

        # Set the main layout for the GhostWindow
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)
        
        # Set initial mode
        self.set_ui_mode('minimal')

    # --- NEW: Method to create the minimal mode UI ---
    def create_minimal_mode(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.minimal_label = QLabel("This is Minimal Mode.\nJust the answer appears here.", widget)
        self.minimal_label.setWordWrap(True) # Allows text to wrap to new lines
        self.minimal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.minimal_label.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-weight: bold;
            background-color: transparent;
            padding: 15px;
        """)
        layout.addWidget(self.minimal_label)
        return widget

    # --- NEW: Method to create the card mode UI ---
    def create_card_mode(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10) # Add some spacing
        layout.setSpacing(5)

        # Label for the user's prompt/title
        self.card_title_label = QLabel("Your Prompt Will Go Here", widget)
        self.card_title_label.setWordWrap(True)
        self.card_title_label.setStyleSheet("""
            color: #d1d1d1; /* Lighter grey for the title */
            font-size: 16px;
            font-weight: bold;
            background-color: transparent;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2); /* Subtle separator line */
            padding: 5px;
        """)
        
        # Label for the AI's response/body
        self.card_body_label = QLabel("The AI's detailed response will appear in this section, providing more context than the minimal view.", widget)
        self.card_body_label.setWordWrap(True)
        self.card_body_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.card_body_label.setStyleSheet("""
            color: white;
            font-size: 15px;
            background-color: transparent;
            padding: 10px;
        """)
        
        layout.addWidget(self.card_title_label)
        layout.addWidget(self.card_body_label)
        layout.addStretch() # Pushes content to the top
        return widget

    # --- NEW: Method to switch between modes ---
    def set_ui_mode(self, mode):
        if mode == 'minimal':
            self.stacked_widget.setCurrentWidget(self.minimal_mode_widget)
        elif mode == 'card':
            self.stacked_widget.setCurrentWidget(self.card_mode_widget)

    def fade_in(self):
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()

    def fade_out(self):
        try: self.animation.finished.disconnect() 
        except TypeError: pass
        self.animation.finished.connect(self.close)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.start()
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.fade_out()

    # --- MODIFIED: Right-click menu now includes mode switching ---
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        # Mode switching submenu
        mode_menu = QMenu("Switch Mode", self)
        minimal_action = QAction("Minimal Mode", self)
        minimal_action.triggered.connect(lambda: self.set_ui_mode('minimal'))
        card_action = QAction("Card Mode", self)
        card_action.triggered.connect(lambda: self.set_ui_mode('card'))
        mode_menu.addAction(minimal_action)
        mode_menu.addAction(card_action)
        
        menu.addMenu(mode_menu)
        menu.addSeparator() # Adds a dividing line
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.fade_out)
        menu.addAction(quit_action)
        
        menu.exec(event.globalPos())

    def update_background_blur(self):
        # (This method is unchanged)
        geo = self.geometry()
        monitor = self.sct.monitors[1]
        capture_area = {"top": geo.y(), "left": geo.x(), "width": geo.width(), "height": geo.height()}
        sct_img = self.sct.grab(capture_area)
        screenshot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        blurred_screenshot = screenshot.filter(ImageFilter.GaussianBlur(radius=15))
        qt_image = ImageQt(blurred_screenshot)
        self.background_pixmap = QPixmap.fromImage(qt_image)
        self.update()

    def paintEvent(self, event):
        # (This method is unchanged)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 15, 15)
        painter.setClipPath(path)
        if hasattr(self, 'background_pixmap'):
            painter.drawPixmap(self.rect(), self.background_pixmap)

    def moveEvent(self, event):
        # (This method is unchanged)
        self.update_background_blur()
        super().moveEvent(event)

    def mousePressEvent(self, event):
        # (This method is unchanged)
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        # (This method is unchanged)
        if self.old_pos:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        # (This method is unchanged)
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ghost_window = GhostWindow()
    ghost_window.show()
    ghost_window.fade_in()
    sys.exit(app.exec())