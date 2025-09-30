from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, QRectF, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QBrush
import markdown
import mss
from PIL import Image, ImageFilter
from PIL.ImageQt import ImageQt

from ui_modes import create_main_content_layout

# --- FIX: The BlurWorker class is now defined directly inside this file ---
# This removes the need to import from the non-existent ghost_window.py
class BlurWorker(QThread):
    background_ready = pyqtSignal(QPixmap)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sct = mss.mss()
        self.geometry = None
        self._is_running = True

    def run(self):
        while self._is_running:
            if self.geometry:
                try:
                    geo = self.geometry; monitor = self.sct.monitors[1]
                    capture_area = {"top": geo.y(), "left": geo.x(), "width": geo.width(), "height": geo.height()}
                    sct_img = self.sct.grab(capture_area)
                    screenshot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    blurred_screenshot = screenshot.filter(ImageFilter.GaussianBlur(radius=15))
                    qt_image = ImageQt(blurred_screenshot)
                    pixmap = QPixmap.fromImage(qt_image)
                    self.background_ready.emit(pixmap)
                except Exception as e:
                    print(f"Error in blur worker: {e}")
            self.msleep(50) # Prevents 100% CPU usage

    def update_geometry(self, geometry):
        self.geometry = geometry

    def stop(self):
        self._is_running = False

class ContentWindow(QWidget):
    dismissed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.old_pos = None
        self.conversation_history = []
        
        self.init_ui()
        
        self.blur_worker = BlurWorker(self)
        self.blur_worker.background_ready.connect(self.set_background_pixmap)
        
    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(150, 150, 600, 400)
        self.setMinimumWidth(500); self.setMaximumHeight(800)

        main_widget, self.history_list_widget, self.title_label, self.body_label, self.dismiss_button = create_main_content_layout()
        
        # This is a critical step: set the layout OF THIS WINDOW to be the layout from the widget we created.
        self.setLayout(main_widget.layout())
        
        self.dismiss_button.clicked.connect(self.on_dismiss)
        self.history_list_widget.itemClicked.connect(self.on_history_item_clicked)

    def display_content(self, history, active_prompt):
        self.conversation_history = history
        self.history_list_widget.clear()
        
        # Block signals while we populate the list to avoid triggering itemClicked
        self.history_list_widget.blockSignals(True)
        for p, _ in reversed(self.conversation_history):
            self.history_list_widget.addItem(p)
        self.history_list_widget.blockSignals(False)

        for prompt, response in self.conversation_history:
            if prompt == active_prompt:
                html_response = markdown.markdown(response)
                self.title_label.setText(f'You: "{prompt}"')
                self.body_label.setText(html_response)
                break
        
        self.adjustSize()
        self.show()

    def on_history_item_clicked(self, item):
        clicked_prompt = item.text()
        # Find just the response, don't re-populate the whole list
        for prompt, response in self.conversation_history:
            if prompt == clicked_prompt:
                html_response = markdown.markdown(response)
                self.title_label.setText(f'You: "{prompt}"')
                self.body_label.setText(html_response)
                self.adjustSize()
                break

    def on_dismiss(self):
        self.hide()
        self.dismissed.emit()

    def set_background_pixmap(self, pixmap):
        self.background_pixmap = pixmap
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath(); path.addRoundedRect(QRectF(self.rect()), 15, 15); painter.setClipPath(path)
        if hasattr(self, 'background_pixmap'): painter.drawPixmap(self.rect(), self.background_pixmap)
        painter.setBrush(QBrush(QColor(0, 0, 0, 100))); painter.setPen(Qt.PenStyle.NoPen); painter.drawPath(path)

    def showEvent(self, event):
        print("Content window shown, starting blur worker.")
        if not self.blur_worker.isRunning():
            self.blur_worker.start()
        self.blur_worker.update_geometry(self.geometry())
        super().showEvent(event)

    def hideEvent(self, event):
        print("Content window hidden, stopping blur worker.")
        if self.blur_worker.isRunning():
            self.blur_worker.stop()
            self.blur_worker.wait()
        super().hideEvent(event)

    def moveEvent(self, event):
        if self.blur_worker.isRunning(): self.blur_worker.update_geometry(self.geometry())
        super().moveEvent(event)
    def resizeEvent(self, event):
        if self.blur_worker.isRunning(): self.blur_worker.update_geometry(self.geometry())
        super().resizeEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton: self.old_pos = event.globalPosition().toPoint()
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y()); self.old_pos = event.globalPosition().toPoint()
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton: self.old_pos = None

    def closeEvent(self, event):
        self.hide(); event.ignore()