from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, QRectF, pyqtSignal, QThread, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QBrush
import markdown
import mss
from PIL import Image, ImageFilter
from PIL.ImageQt import ImageQt

from ui_modes import create_main_content_layout

class BlurWorker(QThread): # (This class is unchanged)
    background_ready = pyqtSignal(QPixmap)
    def __init__(self, parent=None): super().__init__(parent); self.sct = mss.mss(); self.geometry = None; self._is_running = True
    def run(self):
        while self._is_running:
            if self.geometry:
                try:
                    geo = self.geometry; monitor = self.sct.monitors[1]
                    capture_area = {"top": geo.y(), "left": geo.x(), "width": geo.width(), "height": geo.height()}
                    sct_img = self.sct.grab(capture_area); screenshot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    blurred_screenshot = screenshot.filter(ImageFilter.GaussianBlur(radius=15))
                    qt_image = ImageQt(blurred_screenshot); pixmap = QPixmap.fromImage(qt_image); self.background_ready.emit(pixmap)
                except Exception as e: print(f"Error in blur worker: {e}")
            self.msleep(50)
    def update_geometry(self, geometry): self.geometry = geometry
    def stop(self): self._is_running = False

class ContentWindow(QWidget):
    dismissed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.old_pos = None
        self.conversation_history = []
        self.init_ui()
        self.blur_worker = BlurWorker(self)
        self.blur_worker.background_ready.connect(self.set_background_pixmap)
        
        # --- NEW: Animation Setup ---
        self.init_animations()
        
    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(150, 150, 600, 400)
        self.setMinimumWidth(500); self.setMaximumHeight(800)
        
        # Start hidden and fully transparent
        self.setWindowOpacity(0.0)
        self.hide()

        main_widget, self.history_list_widget, self.title_label, self.body_label, self.dismiss_button = create_main_content_layout()
        self.setLayout(main_widget.layout())
        self.dismiss_button.clicked.connect(self.fade_out) # Connect to fade_out now
        self.history_list_widget.itemClicked.connect(self.on_history_item_clicked)
    
    # --- NEW: Method to create the animations ---
    def init_animations(self):
        # We use an animation group to animate geometry and opacity at the same time
        self.animation_group = QParallelAnimationGroup(self)
        
        self.pos_animation = QPropertyAnimation(self, b"geometry")
        self.pos_animation.setDuration(300)
        self.pos_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(300)
        
        self.animation_group.addAnimation(self.pos_animation)
        self.animation_group.addAnimation(self.opacity_animation)
        
        # When fade out is finished, actually hide the widget
        self.animation_group.finished.connect(self.on_animation_finished)

    def display_content(self, history, active_prompt):
        self.conversation_history = history
        self.history_list_widget.blockSignals(True)
        self.history_list_widget.clear()
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
        self.fade_in() # Use the new animation method

    def on_history_item_clicked(self, item):
        clicked_prompt = item.text()
        for prompt, response in self.conversation_history:
            if prompt == clicked_prompt:
                html_response = markdown.markdown(response)
                self.title_label.setText(f'You: "{prompt}"')
                self.body_label.setText(html_response)
                self.adjustSize()
                break

    def on_dismiss(self):
        self.fade_out() # Call the animation
        self.dismissed.emit()

    # --- NEW: Animation control methods ---
    def fade_in(self):
        self.show() # Make the widget visible before animating
        start_rect = self.geometry()
        end_rect = self.geometry()
        start_rect.moveTop(start_rect.top() - 30) # Start 30px higher
        
        self.pos_animation.setStartValue(start_rect)
        self.pos_animation.setEndValue(end_rect)
        
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        
        self.is_fading_out = False
        self.animation_group.start()

    def fade_out(self):
        start_rect = self.geometry()
        end_rect = self.geometry()
        end_rect.moveTop(end_rect.top() - 30) # End 30px higher
        
        self.pos_animation.setStartValue(start_rect)
        self.pos_animation.setEndValue(end_rect)
        
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)

        self.is_fading_out = True
        self.animation_group.start()
        
    def on_animation_finished(self):
        if self.is_fading_out:
            self.hide() # Actually hide the window now
            self.dismissed.emit() # Emit signal after hiding

    def set_background_pixmap(self, pixmap): self.background_pixmap = pixmap; self.update()
    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath(); path.addRoundedRect(QRectF(self.rect()), 15, 15); painter.setClipPath(path)
        if hasattr(self, 'background_pixmap'): painter.drawPixmap(self.rect(), self.background_pixmap)
        painter.setBrush(QBrush(QColor(0, 0, 0, 100))); painter.setPen(Qt.PenStyle.NoPen); painter.drawPath(path)
    def showEvent(self, event):
        print("Content window shown, starting blur worker.")
        if not self.blur_worker.isRunning(): self.blur_worker.start()
        self.blur_worker.update_geometry(self.geometry()); super().showEvent(event)
    def hideEvent(self, event):
        print("Content window hidden, stopping blur worker.")
        if self.blur_worker.isRunning(): self.blur_worker.stop(); self.blur_worker.wait()
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
    def closeEvent(self, event): self.hide(); event.ignore()