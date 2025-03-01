from PyQt6.QtWidgets import (QVBoxLayout, QLabel, 
                           QWizard, QWizardPage, QComboBox,
                           QCheckBox, QLineEdit)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class WelcomeScreen(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to Madick AI Chatbot")
        self.setMinimumSize(700, 500)
        
        # Create pages
        self.addPage(WelcomePage())
        self.addPage(ModelSelectionPage())
        self.addPage(SettingsPage())
        self.addPage(FinishPage())
        
        # Set wizard style
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        
        # Set button text
        self.setButtonText(QWizard.WizardButton.FinishButton, "Get Started!")
        
        # Store user settings
        self.user_settings = {}
        
    def get_settings(self):
        """Get settings from wizard"""
        # Get model selection
        model_page = self.page(1)
        self.user_settings['default_model'] = model_page.model_combo.currentText()
        
        # Get other settings
        settings_page = self.page(2)
        self.user_settings['theme'] = settings_page.theme_combo.currentText()
        self.user_settings['streaming'] = settings_page.streaming_check.isChecked()
        self.user_settings['name'] = settings_page.name_input.text()
        
        return self.user_settings

class WelcomePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to Madick AI Chatbot")
        self.setSubTitle("This wizard will help you set up your chatbot experience")
        
        layout = QVBoxLayout(self)
        
        # Welcome image or logo (placeholder)
        label = QLabel("🤖")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("Arial", 72))
        layout.addWidget(label)
        
        # Welcome text
        welcome_text = QLabel(
            "<p style='font-size: 14px; text-align: center;'>"
            "Thank you for choosing Madick AI! This short wizard will guide you through "
            "basic setup steps so you can start chatting right away.</p>"
        )
        welcome_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_text)
        layout.addStretch()

class ModelSelectionPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Model Selection")
        self.setSubTitle("Choose your preferred AI model")
        layout = QVBoxLayout(self)
        self.model_combo = QComboBox()
        self.model_combo.addItems(["llama3.2:1b", "deepseek-r1", "mistral:7b", "llama2:13b"])
        layout.addWidget(QLabel("Select an AI model:"))
        layout.addWidget(self.model_combo)
        layout.addStretch()

class SettingsPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Basic Settings")
        self.setSubTitle("Adjust theme, streaming, and your name")
        layout = QVBoxLayout(self)
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        streaming_label = QLabel("Enable streaming responses:")
        self.streaming_check = QCheckBox()
        name_label = QLabel("Your name (optional):")
        self.name_input = QLineEdit()
        layout.addWidget(theme_label)
        layout.addWidget(self.theme_combo)
        layout.addWidget(streaming_label)
        layout.addWidget(self.streaming_check)
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        layout.addStretch()

class FinishPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("All Set!")
        self.setSubTitle("Press 'Get Started!' to begin using Madick AI Chatbot")
        layout = QVBoxLayout(self)
        final_label = QLabel(
            "<h3>You're all set!</h3>"
            "<p>Click the button below to start chatting with Madick AI Chatbot.</p>"
        )
        final_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(final_label)
        layout.addStretch()