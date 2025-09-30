# from PyQt6.QtWidgets import QWidget, QMenu, QVBoxLayout, QStackedWidget, QPushButton, QHBoxLayout
# from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QRectF, QSettings, QThread, pyqtSignal
# # --- FIX #1: Import QColor and QBrush for the tint ---
# from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QAction, QColor, QBrush
# from PIL import Image, ImageFilter
# from PIL.ImageQt import ImageQt
# import mss
# # --- FIX #3: Import the markdown library ---
# import markdown

# from ui_modes import create_minimal_mode, create_card_mode
# from settings_dialog import SettingsDialog
# from audio_processor import AudioProcessor
# from ai_core import get_ai_response
# from app_state import AppState

# # (BlurWorker and AIWorker classes are unchanged)
# class BlurWorker(QThread):
#     background_ready = pyqtSignal(QPixmap)
#     def __init__(self, parent=None): super().__init__(parent); self.sct = mss.mss(); self.geometry = None; self._is_running = True
#     def run(self):
#         while self._is_running:
#             if self.geometry:
#                 try:
#                     geo = self.geometry; monitor = self.sct.monitors[1]
#                     capture_area = {"top": geo.y(), "left": geo.x(), "width": geo.width(), "height": geo.height()}
#                     sct_img = self.sct.grab(capture_area)
#                     screenshot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
#                     blurred_screenshot = screenshot.filter(ImageFilter.GaussianBlur(radius=15))
#                     qt_image = ImageQt(blurred_screenshot); pixmap = QPixmap.fromImage(qt_image)
#                     self.background_ready.emit(pixmap)
#                 except Exception as e: print(f"Error in blur worker: {e}")
#             self.msleep(50)
#     def update_geometry(self, geometry): self.geometry = geometry
#     def stop(self): self._is_running = False

# class AIWorker(QThread):
#     response_ready = pyqtSignal(str)
#     def __init__(self, api_key, prompt, parent=None): super().__init__(parent); self.api_key = api_key; self.prompt = prompt
#     def run(self): response = get_ai_response(self.api_key, self.prompt); self.response_ready.emit(response)


# class GhostWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.old_pos = None
#         self.ai_worker = None
#         self.audio_thread = None # Will be created on demand
#         self.current_state = None
        
#         self.init_ui()
        
#         self.blur_worker = BlurWorker(self)
#         self.blur_worker.background_ready.connect(self.set_background_pixmap)
#         self.blur_worker.start()
#         self.blur_worker.update_geometry(self.geometry())

#         self.animation = QPropertyAnimation(self, b"windowOpacity")
#         self.animation.setDuration(300)
#         self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
#         # --- FIX #2: Don't start listening automatically. Set to IDLE state. ---
#         self.set_state(AppState.IDLE)

#     def init_ui(self):
#         self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
#         self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
#         self.setWindowOpacity(0.0)
#         self.setGeometry(100, 100, 550, 200)
#         self.setMinimumWidth(400); self.setMaximumHeight(800)
        
#         self.stacked_widget = QStackedWidget(self)
#         self.minimal_mode_widget, self.minimal_label = create_minimal_mode()
#         self.card_mode_widget, self.card_title_label, self.card_body_label = create_card_mode()
#         self.stacked_widget.addWidget(self.minimal_mode_widget)
#         self.stacked_widget.addWidget(self.card_mode_widget)

#         # --- FIX #2: Create Start/Stop buttons ---
#         self.start_button = QPushButton("Start Listening")
#         self.start_button.clicked.connect(self.start_listening)
        
#         self.stop_button = QPushButton("Stop Listening")
#         self.stop_button.clicked.connect(self.stop_listening)

#         button_layout = QHBoxLayout()
#         button_layout.addStretch()
#         button_layout.addWidget(self.start_button)
#         button_layout.addWidget(self.stop_button)
#         button_layout.addStretch()

#         main_layout = QVBoxLayout(self)
#         main_layout.setContentsMargins(0, 0, 0, 10) # Margin at the bottom for buttons
#         main_layout.addWidget(self.stacked_widget)
#         main_layout.addLayout(button_layout)
#         self.setLayout(main_layout)
        
#         self.set_ui_mode('minimal')

#     # --- FIX #2: New methods to control the audio thread ---
#     def start_listening(self):
#         if self.audio_thread and self.audio_thread.isRunning():
#             return # Already running
#         self.audio_thread = AudioProcessor()
#         self.audio_thread.state_changed.connect(self.set_state)
#         self.audio_thread.final_transcription.connect(self.on_final_transcription)
#         self.audio_thread.start()

#     def stop_listening(self):
#         if self.audio_thread and self.audio_thread.isRunning():
#             self.audio_thread.stop()
#             # The thread will stop, and the UI will naturally go idle.
#         self.set_state(AppState.IDLE)

#     def set_background_pixmap(self, pixmap):
#         self.background_pixmap = pixmap
#         self.update()

#     def set_state(self, new_state, data=None):
#         if self.current_state == new_state and new_state != AppState.DISPLAYING_RESPONSE:
#             return
#         self.current_state = new_state
#         print(f"State changed to: {new_state}")
        
#         # --- FIX #2: Manage button states based on application state ---
#         if new_state == AppState.IDLE:
#             self.minimal_label.setText("Ready. Press 'Start Listening'.")
#             self.start_button.setEnabled(True)
#             self.stop_button.setEnabled(False)
#             self.adjustSize()
#         elif new_state == AppState.LISTENING:
#             self.minimal_label.setText("Listening...")
#             self.start_button.setEnabled(False)
#             self.stop_button.setEnabled(True)
#             self.adjustSize()
#         elif new_state == AppState.PROCESSING_AUDIO:
#             self.minimal_label.setText("Processing...")
#             self.start_button.setEnabled(False)
#             self.stop_button.setEnabled(True)
#             self.adjustSize()
#         elif new_state == AppState.THINKING:
#             prompt = data if data else "..."
#             self.minimal_label.setText("Thinking...")
#             self.card_title_label.setText(f'You: "{prompt}"')
#             self.card_body_label.setText("🧠 Thinking...")
#             self.start_button.setEnabled(False)
#             self.stop_button.setEnabled(True)
#             self.adjustSize()
#         elif new_state == AppState.DISPLAYING_RESPONSE:
#             # --- FIX #3: Convert markdown to HTML before displaying ---
#             html_response = markdown.markdown(data if data else "Error: No response.")
#             self.minimal_label.setText(html_response)
#             self.card_body_label.setText(html_response)
#             self.start_button.setEnabled(True) # Ready for next command
#             self.stop_button.setEnabled(False)
#             self.adjustSize()
            
#     def on_final_transcription(self, text):
#         self.set_state(AppState.THINKING, data=text)
#         settings = QSettings("NaradaTech", "GhostAssistant")
#         api_key = settings.value("GEMINI_API_KEY", "")
#         if not api_key:
#             self.on_ai_response_received("API Key not found. Please set it in the settings.")
#             return
#         self.ai_worker = AIWorker(api_key=api_key, prompt=text)
#         self.ai_worker.response_ready.connect(self.on_ai_response_received)
#         self.ai_worker.finished.connect(self.ai_worker.deleteLater)
#         self.ai_worker.start()

#     def on_ai_response_received(self, response_text):
#         self.set_state(AppState.DISPLAYING_RESPONSE, data=response_text)
        
#     def fade_out(self):
#         print("Stopping threads...")
#         self.stop_listening() # Use our new stop method
#         self.blur_worker.stop()
#         try: self.animation.finished.disconnect()
#         except TypeError: pass
#         self.animation.finished.connect(self.close)
#         self.animation.setStartValue(1.0); self.animation.setEndValue(0.0); self.animation.start()

#     def paintEvent(self, event):
#         painter = QPainter(self)
#         painter.setRenderHint(QPainter.RenderHint.Antialiasing)
#         path = QPainterPath(); path.addRoundedRect(QRectF(self.rect()), 15, 15); painter.setClipPath(path)
        
#         if hasattr(self, 'background_pixmap'):
#             painter.drawPixmap(self.rect(), self.background_pixmap)

#         # --- FIX #1: Add the dark tint for text visibility ---
#         painter.setBrush(QBrush(QColor(0, 0, 0, 100))) # Black with ~40% opacity
#         painter.setPen(Qt.PenStyle.NoPen)
#         painter.drawPath(path) # Draw the tint in the same rounded shape

#     # (All other event methods like moveEvent, resizeEvent, contextMenuEvent, etc. are unchanged)
#     def moveEvent(self, event): self.blur_worker.update_geometry(self.geometry()); super().moveEvent(event)
#     def resizeEvent(self, event): self.blur_worker.update_geometry(self.geometry()); super().resizeEvent(event)
#     def show_settings_dialog(self): dialog = SettingsDialog(self); dialog.exec()
#     def set_ui_mode(self, mode):
#         if mode == 'minimal': self.stacked_widget.setCurrentWidget(self.minimal_mode_widget)
#         elif mode == 'card': self.stacked_widget.setCurrentWidget(self.card_mode_widget)
#     def fade_in(self): self.animation.setStartValue(0.0); self.animation.setEndValue(1.0); self.animation.start()
#     def contextMenuEvent(self, event):
#         menu = QMenu(self); settings_action = QAction("Settings...", self); settings_action.triggered.connect(self.show_settings_dialog)
#         menu.addAction(settings_action); menu.addSeparator()
#         mode_menu = QMenu("Switch Mode", self); minimal_action = QAction("Minimal Mode", self); minimal_action.triggered.connect(lambda: self.set_ui_mode('minimal'))
#         card_action = QAction("Card Mode", self); card_action.triggered.connect(lambda: self.set_ui_mode('card'))
#         mode_menu.addAction(minimal_action); mode_menu.addAction(card_action)
#         menu.addMenu(mode_menu); menu.addSeparator()
#         quit_action = QAction("Quit", self); quit_action.triggered.connect(self.fade_out); menu.addAction(quit_action)
#         menu.exec(event.globalPos())
#     def mousePressEvent(self, event):
#         if event.button() == Qt.MouseButton.LeftButton: self.old_pos = event.globalPosition().toPoint()
#     def mouseMoveEvent(self, event):
#         if self.old_pos:
#             delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
#             self.move(self.x() + delta.x(), self.y() + delta.y()); self.old_pos = event.globalPosition().toPoint()
#     def mouseReleaseEvent(self, event):
#         if event.button() == Qt.MouseButton.LeftButton: self.old_pos = None




































# from PyQt6.QtWidgets import QWidget, QMenu, QVBoxLayout, QStackedWidget, QPushButton, QHBoxLayout
# from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QRectF, QSettings, QThread, pyqtSignal
# from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QAction, QColor, QBrush
# from PIL import Image, ImageFilter
# from PIL.ImageQt import ImageQt
# import mss
# import markdown

# from ui_modes import create_minimal_mode, create_card_mode
# from settings_dialog import SettingsDialog
# from audio_processor import AudioProcessor
# from ai_core import get_ai_response
# from app_state import AppState

# # (BlurWorker and AIWorker classes are unchanged)
# class BlurWorker(QThread):
#     background_ready = pyqtSignal(QPixmap)
#     def __init__(self, parent=None): super().__init__(parent); self.sct = mss.mss(); self.geometry = None; self._is_running = True
#     def run(self):
#         while self._is_running:
#             if self.geometry:
#                 try:
#                     geo = self.geometry; monitor = self.sct.monitors[1]
#                     capture_area = {"top": geo.y(), "left": geo.x(), "width": geo.width(), "height": geo.height()}
#                     sct_img = self.sct.grab(capture_area); screenshot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
#                     blurred_screenshot = screenshot.filter(ImageFilter.GaussianBlur(radius=15))
#                     qt_image = ImageQt(blurred_screenshot); pixmap = QPixmap.fromImage(qt_image); self.background_ready.emit(pixmap)
#                 except Exception as e: print(f"Error in blur worker: {e}")
#             self.msleep(50)
#     def update_geometry(self, geometry): self.geometry = geometry
#     def stop(self): self._is_running = False

# class AIWorker(QThread):
#     response_ready = pyqtSignal(str)
#     def __init__(self, api_key, prompt, parent=None): super().__init__(parent); self.api_key = api_key; self.prompt = prompt
#     def run(self): response = get_ai_response(self.api_key, self.prompt); self.response_ready.emit(response)

# class GhostWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         # (Properties are unchanged)
#         self.old_pos = None; self.ai_worker = None; self.audio_thread = None; self.current_state = None
#         self.init_ui()
#         self.blur_worker = BlurWorker(self)
#         self.blur_worker.background_ready.connect(self.set_background_pixmap)
#         self.blur_worker.start()
#         self.blur_worker.update_geometry(self.geometry())
#         self.animation = QPropertyAnimation(self, b"windowOpacity")
#         self.animation.setDuration(300); self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
#         self.set_state(AppState.IDLE)

#     def init_ui(self):
#         self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
#         self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
#         self.setWindowOpacity(0.0)
#         self.setGeometry(100, 100, 550, 200)
#         self.setMinimumWidth(400)
        
#         # --- FIX: Set a maximum height for the window ---
#         self.setMaximumHeight(600) # The window will not grow taller than this

#         self.stacked_widget = QStackedWidget(self)
#         self.minimal_mode_widget, self.minimal_label = create_minimal_mode()
#         self.card_mode_widget, self.card_title_label, self.card_body_label = create_card_mode()
#         self.stacked_widget.addWidget(self.minimal_mode_widget)
#         self.stacked_widget.addWidget(self.card_mode_widget)
#         self.start_button = QPushButton("Start Listening"); self.start_button.clicked.connect(self.start_listening)
#         self.stop_button = QPushButton("Stop Listening"); self.stop_button.clicked.connect(self.stop_listening)
#         button_layout = QHBoxLayout(); button_layout.addStretch(); button_layout.addWidget(self.start_button)
#         button_layout.addWidget(self.stop_button); button_layout.addStretch()
#         main_layout = QVBoxLayout(self); main_layout.setContentsMargins(0, 0, 0, 10)
#         main_layout.addWidget(self.stacked_widget); main_layout.addLayout(button_layout)
#         self.setLayout(main_layout); self.set_ui_mode('minimal')

#     def start_listening(self): # (Unchanged)
#         if self.audio_thread and self.audio_thread.isRunning(): return
#         self.audio_thread = AudioProcessor(); self.audio_thread.state_changed.connect(self.set_state)
#         self.audio_thread.final_transcription.connect(self.on_final_transcription); self.audio_thread.start()

#     def stop_listening(self): # (Unchanged)
#         if self.audio_thread and self.audio_thread.isRunning(): self.audio_thread.stop()
#         self.set_state(AppState.IDLE)

#     def set_background_pixmap(self, pixmap): self.background_pixmap = pixmap; self.update()

#     def set_state(self, new_state, data=None): # (Unchanged)
#         if self.current_state == new_state and new_state != AppState.DISPLAYING_RESPONSE: return
#         self.current_state = new_state; print(f"State changed to: {new_state}")
#         if new_state == AppState.IDLE:
#             self.minimal_label.setText("Ready. Press 'Start Listening'."); self.start_button.setEnabled(True)
#             self.stop_button.setEnabled(False); self.adjustSize()
#         elif new_state == AppState.LISTENING:
#             self.minimal_label.setText("Listening..."); self.start_button.setEnabled(False)
#             self.stop_button.setEnabled(True); self.adjustSize()
#         elif new_state == AppState.PROCESSING_AUDIO:
#             self.minimal_label.setText("Processing..."); self.start_button.setEnabled(False)
#             self.stop_button.setEnabled(True); self.adjustSize()
#         elif new_state == AppState.THINKING:
#             prompt = data if data else "..."; self.minimal_label.setText("Thinking...")
#             self.card_title_label.setText(f'You: "{prompt}"'); self.card_body_label.setText("🧠 Thinking...")
#             self.start_button.setEnabled(False); self.stop_button.setEnabled(True); self.adjustSize()
#         elif new_state == AppState.DISPLAYING_RESPONSE:
#             html_response = markdown.markdown(data if data else "Error: No response.")
#             self.minimal_label.setText(html_response); self.card_body_label.setText(html_response)
#             self.start_button.setEnabled(True); self.stop_button.setEnabled(False); self.adjustSize()

#     # --- MODIFIED: on_final_transcription ---
#     def on_final_transcription(self, text):
#         self.set_state(AppState.THINKING, data=text)
#         settings = QSettings("NaradaTech", "GhostAssistant")
#         api_key = settings.value("GEMINI_API_KEY", "")
#         if not api_key:
#             self.on_ai_response_received("API Key not found. Please set it in the settings.")
#             return

#         # --- FIX: Engineer the prompt to ask for a concise answer ---
#         instruction = "IMPORTANT: Answer the following question concisely. Your response must be a maximum of 10 lines."
#         final_prompt = f"{instruction}\n\nUser's question: '{text}'"
        
#         self.ai_worker = AIWorker(api_key=api_key, prompt=final_prompt) # Use the new prompt
#         self.ai_worker.response_ready.connect(self.on_ai_response_received)
#         self.ai_worker.finished.connect(self.ai_worker.deleteLater)
#         self.ai_worker.start()

#     def on_ai_response_received(self, response_text): # (Unchanged)
#         self.set_state(AppState.DISPLAYING_RESPONSE, data=response_text)
        
#     def fade_out(self): # (Unchanged)
#         print("Stopping threads..."); self.stop_listening(); self.blur_worker.stop()
#         try: self.animation.finished.disconnect()
#         except TypeError: pass
#         self.animation.finished.connect(self.close)
#         self.animation.setStartValue(1.0); self.animation.setEndValue(0.0); self.animation.start()

#     def paintEvent(self, event): # (Unchanged)
#         painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
#         path = QPainterPath(); path.addRoundedRect(QRectF(self.rect()), 15, 15); painter.setClipPath(path)
#         if hasattr(self, 'background_pixmap'): painter.drawPixmap(self.rect(), self.background_pixmap)
#         painter.setBrush(QBrush(QColor(0, 0, 0, 100))); painter.setPen(Qt.PenStyle.NoPen)
#         painter.drawPath(path)

#     # (All other event methods are unchanged)
#     def moveEvent(self, event): self.blur_worker.update_geometry(self.geometry()); super().moveEvent(event)
#     def resizeEvent(self, event): self.blur_worker.update_geometry(self.geometry()); super().resizeEvent(event)
#     def show_settings_dialog(self): dialog = SettingsDialog(self); dialog.exec()
#     def set_ui_mode(self, mode):
#         if mode == 'minimal': self.stacked_widget.setCurrentWidget(self.minimal_mode_widget)
#         elif mode == 'card': self.stacked_widget.setCurrentWidget(self.card_mode_widget)
#     def fade_in(self): self.animation.setStartValue(0.0); self.animation.setEndValue(1.0); self.animation.start()
#     def contextMenuEvent(self, event):
#         menu = QMenu(self); settings_action = QAction("Settings...", self); settings_action.triggered.connect(self.show_settings_dialog)
#         menu.addAction(settings_action); menu.addSeparator()
#         mode_menu = QMenu("Switch Mode", self); minimal_action = QAction("Minimal Mode", self); minimal_action.triggered.connect(lambda: self.set_ui_mode('minimal'))
#         card_action = QAction("Card Mode", self); card_action.triggered.connect(lambda: self.set_ui_mode('card'))
#         mode_menu.addAction(minimal_action); mode_menu.addAction(card_action)
#         menu.addMenu(mode_menu); menu.addSeparator()
#         quit_action = QAction("Quit", self); quit_action.triggered.connect(self.fade_out); menu.addAction(quit_action)
#         menu.exec(event.globalPos())
#     def mousePressEvent(self, event):
#         if event.button() == Qt.MouseButton.LeftButton: self.old_pos = event.globalPosition().toPoint()
#     def mouseMoveEvent(self, event):
#         if self.old_pos:
#             delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
#             self.move(self.x() + delta.x(), self.y() + delta.y()); self.old_pos = event.globalPosition().toPoint()
#     def mouseReleaseEvent(self, event):
#         if event.button() == Qt.MouseButton.LeftButton: self.old_pos = None


























from PyQt6.QtWidgets import QWidget, QMenu, QVBoxLayout, QStackedWidget, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QRectF, QSettings, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QAction, QColor, QBrush
from PIL import Image, ImageFilter
from PIL.ImageQt import ImageQt
import mss
import markdown

from ui_modes import create_minimal_mode, create_card_mode, create_history_view
from settings_dialog import SettingsDialog
from audio_processor import AudioProcessor
from ai_core import get_ai_response
from app_state import AppState

# (BlurWorker and AIWorker classes are unchanged)
class BlurWorker(QThread):
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

class AIWorker(QThread):
    response_ready = pyqtSignal(str)
    def __init__(self, api_key, prompt, parent=None): super().__init__(parent); self.api_key = api_key; self.prompt = prompt
    def run(self): response = get_ai_response(self.api_key, self.prompt); self.response_ready.emit(response)

class GhostWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.old_pos = None; self.ai_worker = None; self.audio_thread = None; self.current_state = None
        self.conversation_history = []
        self.init_ui()
        self.blur_worker = BlurWorker(self)
        self.blur_worker.background_ready.connect(self.set_background_pixmap)
        self.blur_worker.start()
        self.blur_worker.update_geometry(self.geometry())
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300); self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.set_state(AppState.IDLE)

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.0)
        self.setGeometry(100, 100, 550, 200)
        self.setMinimumWidth(400); self.setMaximumHeight(600)
        self.stacked_widget = QStackedWidget(self)
        self.minimal_mode_widget, self.minimal_label = create_minimal_mode()
        self.card_mode_widget, self.card_title_label, self.card_body_label, self.dismiss_button = create_card_mode()
        self.history_view_widget, self.history_list_widget, self.history_back_button = create_history_view()
        self.dismiss_button.clicked.connect(self.dismiss_response)
        self.history_list_widget.itemClicked.connect(self.on_history_item_clicked)
        self.history_back_button.clicked.connect(lambda: self.set_ui_mode('card'))
        self.stacked_widget.addWidget(self.minimal_mode_widget)
        self.stacked_widget.addWidget(self.card_mode_widget)
        self.stacked_widget.addWidget(self.history_view_widget)
        self.start_button = QPushButton("Start Listening"); self.start_button.clicked.connect(self.start_listening)
        self.stop_button = QPushButton("Stop Listening"); self.stop_button.clicked.connect(self.stop_listening)
        self.history_button = QPushButton("History"); self.history_button.clicked.connect(self.show_history)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.history_button)
        button_layout.addStretch()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 10)
        main_layout.addWidget(self.stacked_widget)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        self.set_ui_mode('card')

    def start_listening(self):
        if self.audio_thread and self.audio_thread.isRunning(): return
        self.audio_thread = AudioProcessor(); self.audio_thread.state_changed.connect(self.set_state)
        self.audio_thread.final_transcription.connect(self.on_final_transcription); self.audio_thread.start()
        self.set_state(AppState.LISTENING)

    def stop_listening(self):
        if self.audio_thread and self.audio_thread.isRunning(): self.audio_thread.stop()
        self.set_state(AppState.IDLE)

    def set_background_pixmap(self, pixmap): self.background_pixmap = pixmap; self.update()

    def set_state(self, new_state, data=None):
        if self.current_state == new_state and new_state not in [AppState.DISPLAYING_RESPONSE, AppState.THINKING]: return
        self.current_state = new_state; print(f"State changed to: {new_state}")
        self.dismiss_button.hide()
        if new_state == AppState.IDLE:
            self.card_title_label.setText("Idle"); self.card_body_label.setText("Press 'Start Listening' to begin.")
            self.start_button.setEnabled(True); self.stop_button.setEnabled(False); self.history_button.setEnabled(True)
        elif new_state == AppState.LISTENING:
            self.card_title_label.setText("Listening..."); self.card_body_label.setText("")
            self.start_button.setEnabled(False); self.stop_button.setEnabled(True); self.history_button.setEnabled(True)
        elif new_state == AppState.PROCESSING_AUDIO:
            self.card_title_label.setText("Processing..."); self.card_body_label.setText("")
        elif new_state == AppState.THINKING:
            prompt = data if data else "..."; self.card_title_label.setText(f'You: "{prompt}"'); self.card_body_label.setText("🧠 Thinking...")
        elif new_state == AppState.DISPLAYING_RESPONSE:
            prompt, response_text = data; html_response = markdown.markdown(response_text)
            self.card_title_label.setText(f'You: "{prompt}"'); self.card_body_label.setText(html_response)
            self.dismiss_button.show()
            self.start_button.setEnabled(False); self.stop_button.setEnabled(True); self.history_button.setEnabled(True)
        self.adjustSize()

    def on_final_transcription(self, text):
        self.set_ui_mode('card')
        self.set_state(AppState.THINKING, data=text)
        settings = QSettings("NaradaTech", "GhostAssistant")
        api_key = settings.value("GEMINI_API_KEY", "")
        if not api_key: self.on_ai_response_received("API Key not found.", text); return
        instruction = "IMPORTANT: Answer the following question concisely. Your response must be a maximum of 10 lines."
        final_prompt = f"{instruction}\n\nUser's question: '{text}'"
        self.ai_worker = AIWorker(api_key=api_key, prompt=final_prompt)
        self.ai_worker.response_ready.connect(lambda response: self.on_ai_response_received(response, text))
        self.ai_worker.finished.connect(self.ai_worker.deleteLater)
        self.ai_worker.start()

    def on_ai_response_received(self, response_text, original_prompt):
        self.conversation_history.append((original_prompt, response_text))
        if len(self.conversation_history) > 20: self.conversation_history.pop(0)
        self.set_state(AppState.DISPLAYING_RESPONSE, data=(original_prompt, response_text))
    
    def dismiss_response(self):
        self.set_state(AppState.LISTENING)

    def show_history(self):
        self.history_list_widget.clear()
        for prompt, _ in reversed(self.conversation_history): self.history_list_widget.addItem(prompt)
        self.stacked_widget.setCurrentWidget(self.history_view_widget)
        self.adjustSize()

    def on_history_item_clicked(self, item):
        clicked_prompt = item.text()
        for prompt, response in self.conversation_history:
            if prompt == clicked_prompt:
                self.set_state(AppState.DISPLAYING_RESPONSE, data=(prompt, response))
                self.set_ui_mode('card')
                break

    # --- FIX: Restored the missing fade_in method ---
    def fade_in(self):
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()

    def fade_out(self):
        print("Stopping threads..."); self.stop_listening(); self.blur_worker.stop()
        try: self.animation.finished.disconnect()
        except TypeError: pass
        self.animation.finished.connect(self.close)
        self.animation.setStartValue(1.0); self.animation.setEndValue(0.0); self.animation.start()

    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath(); path.addRoundedRect(QRectF(self.rect()), 15, 15); painter.setClipPath(path)
        if hasattr(self, 'background_pixmap'): painter.drawPixmap(self.rect(), self.background_pixmap)
        painter.setBrush(QBrush(QColor(0, 0, 0, 100))); painter.setPen(Qt.PenStyle.NoPen); painter.drawPath(path)

    def set_ui_mode(self, mode):
        if mode == 'card': self.stacked_widget.setCurrentWidget(self.card_mode_widget)
        elif mode == 'minimal': self.stacked_widget.setCurrentWidget(self.minimal_mode_widget)

    def moveEvent(self, event): self.blur_worker.update_geometry(self.geometry()); super().moveEvent(event)
    def resizeEvent(self, event): self.blur_worker.update_geometry(self.geometry()); super().resizeEvent(event)
    def show_settings_dialog(self): dialog = SettingsDialog(self); dialog.exec()
    def contextMenuEvent(self, event):
        menu = QMenu(self); settings_action = QAction("Settings...", self); settings_action.triggered.connect(self.show_settings_dialog)
        menu.addAction(settings_action); menu.addSeparator()
        mode_menu = QMenu("Switch Mode", self); minimal_action = QAction("Minimal Mode", self); minimal_action.triggered.connect(lambda: self.set_ui_mode('minimal'))
        card_action = QAction("Card Mode", self); card_action.triggered.connect(lambda: self.set_ui_mode('card'))
        mode_menu.addAction(minimal_action); mode_menu.addAction(card_action)
        menu.addMenu(mode_menu); menu.addSeparator()
        quit_action = QAction("Quit", self); quit_action.triggered.connect(self.fade_out); menu.addAction(quit_action)
        menu.exec(event.globalPos())
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
            
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y()); self.old_pos = event.globalPosition().toPoint()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None