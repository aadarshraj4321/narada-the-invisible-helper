from enum import Enum, auto

class AppState(Enum):
    IDLE = auto() # <-- NEW STATE for when not listening
    LISTENING = auto()
    PROCESSING_AUDIO = auto()
    THINKING = auto()
    DISPLAYING_RESPONSE = auto()