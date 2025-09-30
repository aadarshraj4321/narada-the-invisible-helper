from PyQt6.QtWidgets import QWidget, QMenu, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QSettings, QThread, pyqtSignal
from PyQt6.QtGui import QAction

from content_window import ContentWindow
from settings_dialog import SettingsDialog
from audio_processor import AudioProcessor
from ai_core import get_ai_response
from app_state import AppState

class AIWorker(QThread): # (This class is unchanged)
    response_ready = pyqtSignal(str)
    def __init__(self, api_key, prompt, parent=None): super().__init__(parent); self.api_key = api_key; self.prompt = prompt
    def run(self): response = get_ai_response(self.api_key, self.prompt); self.response_ready.emit(response)

class ControlWindow(QWidget):
    def __init__(self):
        super().__init__()
        # This is the variable that will store the mouse position for dragging
        self.old_pos = None
        
        self.ai_worker = None; self.current_state = None
        self.conversation_history = []
        self.content_window = ContentWindow()
        self.content_window.dismissed.connect(self.on_content_dismissed)
        
        # Create and start the audio thread ONCE. This is the stable approach.
        self.audio_thread = AudioProcessor()
        self.audio_thread.state_changed.connect(self.set_state)
        self.audio_thread.final_transcription.connect(self.on_final_transcription)
        self.audio_thread.start()
        
        self.init_ui()
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300); self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.set_state(AppState.IDLE)

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.0)
        self.setGeometry(50, 50, 450, 100)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.75); border-radius: 10px;")
        
        # --- THIS IS THE DRAG BAR WIDGET ---
        # It's just a visual indicator. The logic is handled by the main window now.
        self.drag_bar = QWidget(self)
        self.drag_bar.setFixedHeight(20)
        self.drag_bar.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.1); 
            border-top-left-radius: 10px; 
            border-top-right-radius: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        """)
        
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background: transparent;")
        
        self.start_button = QPushButton("Start"); self.start_button.clicked.connect(self.start_listening)
        self.stop_button = QPushButton("Stop"); self.stop_button.clicked.connect(self.stop_listening)
        self.history_button = QPushButton("Show"); self.history_button.clicked.connect(self.show_content_window)
        self.quit_button = QPushButton("Quit"); self.quit_button.clicked.connect(self.close)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button); button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.history_button); button_layout.addWidget(self.quit_button)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 5)
        main_layout.setSpacing(5)
        
        main_layout.addWidget(self.drag_bar) # The visual bar at the top
        main_layout.addWidget(self.status_label)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        
    def start_listening(self):
        self.audio_thread.toggle_listening(is_paused=False)
        self.set_state(AppState.LISTENING)

    def stop_listening(self):
        self.audio_thread.toggle_listening(is_paused=True)
        self.set_state(AppState.IDLE)

    def set_state(self, new_state): # (Unchanged)
        if self.current_state == new_state: return
        self.current_state = new_state; print(f"State changed to: {new_state}")
        if new_state == AppState.IDLE:
            self.status_label.setText("Idle"); self.start_button.setEnabled(True); self.stop_button.setEnabled(False)
        elif new_state == AppState.LISTENING:
            self.status_label.setText("Listening..."); self.start_button.setEnabled(False); self.stop_button.setEnabled(True)
        elif new_state == AppState.PROCESSING_AUDIO: self.status_label.setText("Processing...")
        elif new_state == AppState.THINKING: self.status_label.setText("Thinking...")

    def on_final_transcription(self, text): # (Unchanged)
        self.set_state(AppState.THINKING)
        settings = QSettings("NaradaTech", "GhostAssistant")
        api_key = settings.value("GEMINI_API_KEY", "")
        if not api_key: self.on_ai_response_received("API Key not found.", text); return
        instruction = "IMPORTANT: Answer concisely, max 10 lines."
        final_prompt = f"{instruction}\n\nUser's question: '{text}'"
        self.ai_worker = AIWorker(api_key=api_key, prompt=final_prompt)
        self.ai_worker.response_ready.connect(lambda response: self.on_ai_response_received(response, text))
        self.ai_worker.finished.connect(self.ai_worker.deleteLater)
        self.ai_worker.start()

    def on_ai_response_received(self, response_text, original_prompt): # (Unchanged)
        self.conversation_history.append((original_prompt, response_text))
        if len(self.conversation_history) > 20: self.conversation_history.pop(0)
        self.content_window.display_content(self.conversation_history, original_prompt)
        if not self.audio_thread._is_paused: self.set_state(AppState.LISTENING)

    def on_content_dismissed(self): # (Unchanged)
        if not self.audio_thread._is_paused: self.set_state(AppState.LISTENING)
        else: self.set_state(AppState.IDLE)
            
    def show_content_window(self): # (Unchanged)
        if not self.conversation_history: self.content_window.display_content([], "No history yet.")
        else: last_prompt, _ = self.conversation_history[-1]; self.content_window.display_content(self.conversation_history, last_prompt)

    def fade_in(self): self.animation.setStartValue(0.0); self.animation.setEndValue(1.0); self.animation.start()

    def closeEvent(self, event): # (Unchanged)
        print("Stopping threads and closing application...")
        self.audio_thread.stop(); self.audio_thread.wait()
        self.content_window.close(); super().closeEvent(event)

    def contextMenuEvent(self, event): # (Unchanged)
        menu = QMenu(self)
        settings_action = QAction("Settings...", self); settings_action.triggered.connect(lambda: SettingsDialog(self).exec())
        menu.addAction(settings_action); menu.addSeparator()
        quit_action = QAction("Quit Application", self); quit_action.triggered.connect(self.close)
        menu.addAction(quit_action); menu.exec(event.globalPos())
    
    # --- THE DEFINITIVE DRAGGING SOLUTION ---
    def mousePressEvent(self, event):
        # Check if the click was inside the drag_bar widget
        if event.button() == Qt.MouseButton.LeftButton and self.drag_bar.geometry().contains(event.pos()):
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        # Only move the window if the drag was initiated from the drag_bar
        if self.old_pos:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        # Stop dragging
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None