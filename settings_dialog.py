from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox
from PyQt6.QtCore import QSettings

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        
        # Use QSettings to store and retrieve application settings
        # These names are important for identifying your app's settings file
        self.settings = QSettings("NaradaTech", "GhostAssistant")
        
        # --- UI Elements ---
        self.api_key_input = QLineEdit(self)
        
        # Create OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept) # The accept() slot will save and close
        button_box.rejected.connect(self.reject) # The reject() slot will just close
        
        # --- Layout ---
        # A form layout is perfect for label-input pairs
        form_layout = QFormLayout()
        form_layout.addRow("Gemini API Key:", self.api_key_input)
        
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        
        self.setLayout(main_layout)
        
        # Load the saved settings into the input fields
        self.load_settings()

    def load_settings(self):
        """Loads settings and populates the input fields."""
        api_key = self.settings.value("GEMINI_API_KEY", "") # Default to empty string
        self.api_key_input.setText(api_key)

    def accept(self):
        """Saves the current values from the input fields."""
        self.settings.setValue("GEMINI_API_KEY", self.api_key_input.text())
        super().accept() # Closes the dialog with an "Accepted" status