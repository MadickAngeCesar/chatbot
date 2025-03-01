from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                           QComboBox, QLineEdit, QPushButton,
                           QFormLayout, QGroupBox, QScrollArea,
                           QWidget, QHBoxLayout)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import json
import os

class WelcomeScreen(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to Madick AI Chatbot")
        self.setMinimumSize(600, 700)
        
        # Initialize settings
        self.settings = self.load_default_settings()
        
        # Create scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        main_layout = QVBoxLayout(scroll_content)
        
        # Welcome header with icon
        header_layout = QHBoxLayout()
        icon_label = QLabel("🤖")
        icon_label.setFont(QFont("Arial", 48))
        header_text = QLabel("Welcome to Madick AI")
        header_text.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        header_layout.addStretch()
        header_layout.addWidget(icon_label)
        header_layout.addWidget(header_text)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Add description
        desc = QLabel("Your intelligent desktop companion powered by state-of-the-art language models.")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        main_layout.addWidget(desc)
        
        # Basic Settings Group
        settings_group = QGroupBox("Basic Settings")
        form_layout = QFormLayout()
        
        # Model selection with description
        model_widget = QWidget()
        model_layout = QVBoxLayout(model_widget)
        self.model_combo = QComboBox()
        self.model_combo.addItems(["llama3.2:1b", "deepseek-r1", "mistral:7b", "llama2:13b"])
        self.model_combo.setCurrentText(self.settings.get('default_model', 'llama3.2:1b'))
        model_desc = QLabel("Choose your default AI model. You can change this later.")
        model_desc.setStyleSheet("color: gray; font-size: 10px;")
        model_layout.addWidget(self.model_combo)
        model_layout.addWidget(model_desc)
        form_layout.addRow("Default Model:", model_widget)
        
        # Theme selection with preview
        theme_widget = QWidget()
        theme_layout = QVBoxLayout(theme_widget)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(self.settings.get('theme', 'dark'))
        theme_desc = QLabel("Select your preferred theme. Dark theme is easier on the eyes.")
        theme_desc.setStyleSheet("color: gray; font-size: 10px;")
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addWidget(theme_desc)
        form_layout.addRow("Theme:", theme_widget)
        
        # User name
        name_widget = QWidget()
        name_layout = QVBoxLayout(name_widget)
        self.name_input = QLineEdit()
        self.name_input.setText(self.settings.get('user_name', ''))
        self.name_input.setPlaceholderText("Enter your name (optional)")
        name_desc = QLabel("Your name will be used to personalize the chat experience.")
        name_desc.setStyleSheet("color: gray; font-size: 10px;")
        name_layout.addWidget(self.name_input)
        name_layout.addWidget(name_desc)
        form_layout.addRow("Your Name:", name_widget)
        
        settings_group.setLayout(form_layout)
        main_layout.addWidget(settings_group)
        
        # Get Started button
        start_button = QPushButton("Get Started!")
        start_button.setMinimumHeight(50)
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        start_button.clicked.connect(self.save_and_accept)
        main_layout.addWidget(start_button)
        
        scroll.setWidget(scroll_content)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)
        
        # Features Overview
        features_group = QGroupBox("Key Features")
        features_layout = QHBoxLayout()  # Changed to horizontal layout for columns
        
        # Left column
        left_column = QVBoxLayout()
        left_features = [
            "🔄 Multiple AI Models Support",
            "💾 Chat History & Session Management",
            "🔍 Conversation Search",
            "🎤 Voice Input Support",
        ]
        for feature in left_features:
            feature_label = QLabel(feature)
            feature_label.setStyleSheet("padding: 5px;")
            left_column.addWidget(feature_label)
        
        # Right column
        right_column = QVBoxLayout()
        right_features = [
            "📝 Custom Templates",
            "🌓 Theme Customization",
            "📎 File Attachments",
            "⌨️ Keyboard Shortcuts"
        ]
        for feature in right_features:
            feature_label = QLabel(feature)
            feature_label.setStyleSheet("padding: 5px;")
            right_column.addWidget(feature_label)
        
        # Add columns to main features layout
        left_widget = QWidget()
        left_widget.setLayout(left_column)
        right_widget = QWidget()
        right_widget.setLayout(right_column)
        
        features_layout.addWidget(left_widget)
        features_layout.addWidget(right_widget)
        
        features_group.setLayout(features_layout)
        main_layout.addWidget(features_group)
        
        # Keyboard shortcuts preview
        shortcuts_group = QGroupBox("Quick Shortcuts")
        shortcuts_layout = QHBoxLayout()  # Changed to horizontal layout
        
        # Left column
        left_column = QVBoxLayout()
        left_shortcuts = [
            "Ctrl+Enter: Send message",
            "Ctrl+L: Clear chat"
        ]
        for shortcut in left_shortcuts:
            shortcut_label = QLabel(shortcut)
            left_column.addWidget(shortcut_label)
        
        # Right column
        right_column = QVBoxLayout()
        right_shortcuts = [
            "Ctrl+F: Search",
            "Ctrl+T: Toggle theme"
        ]
        for shortcut in right_shortcuts:
            shortcut_label = QLabel(shortcut)
            right_column.addWidget(shortcut_label)
        
        # Add columns to main shortcuts layout
        left_widget = QWidget()
        left_widget.setLayout(left_column)
        right_widget = QWidget()
        right_widget.setLayout(right_column)
        
        shortcuts_layout.addWidget(left_widget)
        shortcuts_layout.addWidget(right_widget)
        
        shortcuts_group.setLayout(shortcuts_layout)
        main_layout.addWidget(shortcuts_group)
        
    def load_default_settings(self):
        """Load existing settings or create defaults"""
        default_settings = {
            'theme': 'dark',
            'default_model': 'llama3.2:1b',
            'streaming': True,
            'text_to_speech': False,
            'system_prompt': '',
            'max_history': 50,
            'font_size': 14,
            'user_name': ''
        }
        
        if os.path.exists('settings.json'):
            try:
                with open('settings.json', 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return default_settings
    
    def save_and_accept(self):
        """Save settings and close dialog"""
        self.settings['default_model'] = self.model_combo.currentText()
        self.settings['theme'] = self.theme_combo.currentText()
        self.settings['user_name'] = self.name_input.text()
        
        # Save to file
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f, indent=4)
            
        self.accept()
    
    def get_settings(self):
        """Return the current settings"""
        return self.settings
