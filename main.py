import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication

# --- NEW: Import the ControlWindow as our main entry point ---
from control_window import ControlWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    QCoreApplication.setOrganizationName("NaradaTech")
    QCoreApplication.setApplicationName("GhostAssistant")
    
    # Create an instance of our main control window
    control_window = ControlWindow()
    
    # Show the window and fade it in
    control_window.show()
    control_window.fade_in()
    
    sys.exit(app.exec())