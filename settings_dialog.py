from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QLabel, QLineEdit, QComboBox, QCheckBox, 
                           QPushButton, QSpinBox, QTextEdit, QGroupBox,
                           QFormLayout)
from PyQt6.QtCore import Qt
import json
import os

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Load current settings
        self.settings = self.load_settings()
        
        self.init_ui()
        
    def load_settings(self):
        # Default settings
        default_settings = {
            'theme': 'dark',
            'default_model': 'llama3.2:1b',
            'streaming': True,
            'text_to_speech': False,
            'system_prompt': '',
            'max_history': 50,
            'font_size': 14
        }
        
        # Try to load from file
        if os.path.exists('settings.json'):
            try:
                with open('settings.json', 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return default_settings
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tabs = QTabWidget()
        
        # General settings tab
        general_tab = self.create_general_tab()
        tabs.addTab(general_tab, "General")
        
        # Models tab
        models_tab = self.create_models_tab()
        tabs.addTab(models_tab, "Models")
        
        # Advanced tab
        advanced_tab = self.create_advanced_tab()
        tabs.addTab(advanced_tab, "Advanced")
        
        # Add tab widget to layout
        layout.addWidget(tabs)
        
        # Add save/cancel buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
    def create_general_tab(self):
        tab = QGroupBox("General Settings")
        layout = QFormLayout(tab)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(self.settings.get('theme', 'dark'))
        layout.addRow("Theme:", self.theme_combo)
        
        # Font size
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(self.settings.get('font_size', 14))
        layout.addRow("Font Size:", self.font_size)
        
        # Max history
        self.max_history = QSpinBox()
        self.max_history.setRange(10, 1000)
        self.max_history.setValue(self.settings.get('max_history', 50))
        layout.addRow("Max History Items:", self.max_history)
        
        # Text to speech
        self.text_to_speech = QCheckBox()
        self.text_to_speech.setChecked(self.settings.get('text_to_speech', False))
        layout.addRow("Enable Text-to-Speech:", self.text_to_speech)
        
        return tab
        
    def create_models_tab(self):
        tab = QGroupBox("Model Settings")
        layout = QFormLayout(tab)
        
        # Default model
        self.default_model = QComboBox()
        self.default_model.addItems(["llama3.2:1b", "deepseek-r1", "mistral:7b", "llama2:13b"])
        self.default_model.setCurrentText(self.settings.get('default_model', 'llama3.2:1b'))
        layout.addRow("Default Model:", self.default_model)
        
        # Streaming
        self.streaming = QCheckBox()
        self.streaming.setChecked(self.settings.get('streaming', True))
        layout.addRow("Enable Streaming:", self.streaming)
        
        # System prompt
        self.system_prompt = QTextEdit()
        self.system_prompt.setPlainText(self.settings.get('system_prompt', ''))
        self.system_prompt.setMaximumHeight(100)
        layout.addRow("System Prompt:", self.system_prompt)
        
        return tab
        
    def create_advanced_tab(self):
        tab = QGroupBox("Advanced Settings")
        layout = QFormLayout(tab)
        
        # API URL
        self.api_url = QLineEdit()
        self.api_url.setText(self.settings.get('api_url', 'http://localhost:11434'))
        layout.addRow("API URL:", self.api_url)
        
        # Temperature
        self.temperature = QSpinBox()
        self.temperature.setRange(0, 100)
        self.temperature.setValue(int(self.settings.get('temperature', 70)))
        layout.addRow("Temperature:", self.temperature)
        
        return tab
        
    def save_settings(self):
        # Update settings from UI
        self.settings['theme'] = self.theme_combo.currentText()
        self.settings['font_size'] = self.font_size.value()
        self.settings['max_history'] = self.max_history.value()
        self.settings['text_to_speech'] = self.text_to_speech.isChecked()
        self.settings['default_model'] = self.default_model.currentText()
        self.settings['streaming'] = self.streaming.isChecked()
        self.settings['system_prompt'] = self.system_prompt.toPlainText()
        self.settings['api_url'] = self.api_url.text()
        self.settings['temperature'] = self.temperature.value()
        
        # Save to file
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f, indent=4)
            
        self.accept()
