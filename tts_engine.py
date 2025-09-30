import pyttsx3
from PyQt6.QtCore import QThread, pyqtSignal

class TTSEngine(QThread):
    """A QThread that runs the pyttsx3 text-to-speech engine."""
    
    # Signal emitted when speaking is finished
    finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text_to_speak = ""
        self.engine = None

    def run(self):
        """Initializes the engine and speaks the text."""
        try:
            self.engine = pyttsx3.init()
            self.engine.say(self.text_to_speak)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error in TTS engine: {e}")
        finally:
            # Emit the finished signal after speaking is done
            self.finished.emit()

    def speak(self, text):
        """Sets the text and starts the thread."""
        if not self.isRunning():
            self.text_to_speak = text
            self.start()