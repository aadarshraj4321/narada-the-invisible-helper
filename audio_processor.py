import speech_recognition as sr
from PyQt6.QtCore import QThread, pyqtSignal
from app_state import AppState

class AudioProcessor(QThread):
    state_changed = pyqtSignal(AppState)
    final_transcription = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.recognizer.pause_threshold = 2.0
        
        # --- FIX #2: New state flags for pausing/resuming ---
        self._is_running = True
        self._is_paused = True # Start in a paused state

    def toggle_listening(self, is_paused):
        """Public method to safely pause or resume the listening loop."""
        self._is_paused = is_paused
        if not is_paused:
            print("Audio processor resumed.")
        else:
            print("Audio processor paused.")

    def run(self):
        print("Audio thread started. Calibrating...")
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            print(f"Could not calibrate microphone: {e}"); self._is_running = False

        while self._is_running:
            # --- FIX #2: The new pause logic ---
            if self._is_paused:
                self.msleep(100) # Sleep for a short time to avoid busy-waiting
                continue # Skip the rest of the loop

            try:
                with self.microphone as source:
                    self.state_changed.emit(AppState.LISTENING)
                    print("Listening for a command...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=15)
                    
                    self.state_changed.emit(AppState.PROCESSING_AUDIO)
                    print("Recognizing with Google Speech...")
                    text = self.recognizer.recognize_google(audio)
                    
                    print(f"Google Speech thinks you said: {text}")
                    if text:
                        self.final_transcription.emit(text)

            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                print("Google Speech could not understand audio")
                continue
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech service; {e}")
                continue
            except Exception as e:
                print(f"An error occurred in audio loop: {e}"); break
        
        print("Audio thread has fully stopped.")

    def stop(self):
        """Stops the thread completely."""
        self._is_running = False