from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QLineEdit, QComboBox, QCheckBox, 
                           QPushButton, QSpinBox, QTextEdit, QGroupBox,
                           QFormLayout, QLabel)
import json
import os

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Initialize translations
        self.translations = {
            'en': {
                'settings': 'Settings',
                'general': 'General',
                'models': 'Models',
                'advanced': 'Advanced',
                'save': 'Save',
                'cancel': 'Cancel',
                'general_settings': 'General Settings',
                'theme': 'Theme:',
                'language': 'Language:',
                'font_size': 'Font Size:',
                'max_history': 'Max History Items:',
                'enable_tts': 'Enable Text-to-Speech:',
                'model_settings': 'Model Settings',
                'default_model': 'Default Model:',
                'enable_streaming': 'Enable Streaming:',
                'system_prompt': 'System Prompt:',
                'advanced_settings': 'Advanced Settings',
                'api_url': 'API URL:',
                'temperature': 'Temperature:'
            },
            'fr': {
                'settings': 'Paramètres',
                'general': 'Général',
                'models': 'Modèles',
                'advanced': 'Avancé',
                'save': 'Enregistrer',
                'cancel': 'Annuler',
                'general_settings': 'Paramètres Généraux',
                'theme': 'Thème:',
                'language': 'Langue:',
                'font_size': 'Taille de Police:',
                'max_history': 'Nombre Maximum d\'Éléments d\'Historique:',
                'enable_tts': 'Activer la Synthèse Vocale:',
                'model_settings': 'Paramètres du Modèle',
                'default_model': 'Modèle par Défaut:',
                'enable_streaming': 'Activer le Streaming:',
                'system_prompt': 'Invite Système:',
                'advanced_settings': 'Paramètres Avancés',
                'api_url': 'URL de l\'API:',
                'temperature': 'Température:'
            }
        }
        
        # Load current settings
        self.settings = self.load_settings()
        
        # Set current language
        self.current_language = self.settings.get('language', 'en')
        
        self.setWindowTitle(self.tr('settings'))
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.init_ui()
        
    def tr(self, key):
        """Translate a string using the current language"""
        return self.translations.get(self.current_language, {}).get(key, key)
        
    def load_settings(self):
        # Default settings
        default_settings = {
            'theme': 'dark',
            'default_model': 'llama3.2:1b',
            'streaming': True,
            'text_to_speech': False,
            'system_prompt': '',
            'max_history': 50,
            'font_size': 14,
            'language': 'en'  # Default language code
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
        self.tabs = QTabWidget()
        
        # General settings tab
        general_tab = self.create_general_tab()
        self.tabs.addTab(general_tab, self.tr('general'))
        
        # Models tab
        models_tab = self.create_models_tab()
        self.tabs.addTab(models_tab, self.tr('models'))
        
        # Advanced tab
        advanced_tab = self.create_advanced_tab()
        self.tabs.addTab(advanced_tab, self.tr('advanced'))
        
        # Add tab widget to layout
        layout.addWidget(self.tabs)
        
        # Add save/cancel buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton(self.tr('save'))
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button = QPushButton(self.tr('cancel'))
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def create_general_tab(self):
        self.general_group = QGroupBox(self.tr('general_settings'))
        layout = QFormLayout(self.general_group)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(self.settings.get('theme', 'dark'))
        self.theme_label = QLabel(self.tr('theme'))
        layout.addRow(self.theme_label, self.theme_combo)
        
        # Language selection
        self.language_combo = QComboBox()
        languages = [("English", "en"), ("Français", "fr")]
        for display, code in languages:
            self.language_combo.addItem(display, code)
        
        # Set current language
        index = self.language_combo.findData(self.settings.get('language', 'en'))
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        
        self.language_label = QLabel(self.tr('language'))
        layout.addRow(self.language_label, self.language_combo)
        
        # Font size
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(self.settings.get('font_size', 14))
        self.font_size_label = QLabel(self.tr('font_size'))
        layout.addRow(self.font_size_label, self.font_size)
        
        # Max history
        self.max_history = QSpinBox()
        self.max_history.setRange(10, 1000)
        self.max_history.setValue(self.settings.get('max_history', 50))
        self.max_history_label = QLabel(self.tr('max_history'))
        layout.addRow(self.max_history_label, self.max_history)
        
        # Text to speech
        self.text_to_speech = QCheckBox()
        self.text_to_speech.setChecked(self.settings.get('text_to_speech', False))
        self.tts_label = QLabel(self.tr('enable_tts'))
        layout.addRow(self.tts_label, self.text_to_speech)
        
        return self.general_group
        
    def create_models_tab(self):
        self.models_group = QGroupBox(self.tr('model_settings'))
        layout = QFormLayout(self.models_group)
        
        # Default model
        self.default_model = QComboBox()
        self.default_model.addItems(["llama3.2:1b", "deepseek-r1", "mistral:7b", "llama2:13b"])
        self.default_model.setCurrentText(self.settings.get('default_model', 'llama3.2:1b'))
        self.model_label = QLabel(self.tr('default_model'))
        layout.addRow(self.model_label, self.default_model)
        
        # Streaming
        self.streaming = QCheckBox()
        self.streaming.setChecked(self.settings.get('streaming', True))
        self.streaming_label = QLabel(self.tr('enable_streaming'))
        layout.addRow(self.streaming_label, self.streaming)
        
        # System prompt
        self.system_prompt = QTextEdit()
        self.system_prompt.setPlainText(self.settings.get('system_prompt', ''))
        self.system_prompt.setMaximumHeight(100)
        self.prompt_label = QLabel(self.tr('system_prompt'))
        layout.addRow(self.prompt_label, self.system_prompt)
        
        return self.models_group
        
    def create_advanced_tab(self):
        self.advanced_group = QGroupBox(self.tr('advanced_settings'))
        layout = QFormLayout(self.advanced_group)
        
        # API URL
        self.api_url = QLineEdit()
        self.api_url.setText(self.settings.get('api_url', 'http://localhost:11434'))
        self.api_url_label = QLabel(self.tr('api_url'))
        layout.addRow(self.api_url_label, self.api_url)
        
        # Temperature
        self.temperature = QSpinBox()
        self.temperature.setRange(0, 100)
        self.temperature.setValue(int(self.settings.get('temperature', 70)))
        self.temp_label = QLabel(self.tr('temperature'))
        layout.addRow(self.temp_label, self.temperature)
        
        return self.advanced_group
    
    def on_language_changed(self, index):
        """Update UI language when selection changes"""
        lang_code = self.language_combo.itemData(index)
        if lang_code != self.current_language:
            self.current_language = lang_code
            self.update_ui_language()
    
    def update_ui_language(self):
        """Update all UI elements to the current language"""
        # Update window title
        self.setWindowTitle(self.tr('settings'))
        
        # Update tab names
        self.tabs.setTabText(0, self.tr('general'))
        self.tabs.setTabText(1, self.tr('models'))
        self.tabs.setTabText(2, self.tr('advanced'))
        
        # Update group titles
        self.general_group.setTitle(self.tr('general_settings'))
        self.models_group.setTitle(self.tr('model_settings'))
        self.advanced_group.setTitle(self.tr('advanced_settings'))
        
        # Update labels
        self.theme_label.setText(self.tr('theme'))
        self.language_label.setText(self.tr('language'))
        self.font_size_label.setText(self.tr('font_size'))
        self.max_history_label.setText(self.tr('max_history'))
        self.tts_label.setText(self.tr('enable_tts'))
        self.model_label.setText(self.tr('default_model'))
        self.streaming_label.setText(self.tr('enable_streaming'))
        self.prompt_label.setText(self.tr('system_prompt'))
        self.api_url_label.setText(self.tr('api_url'))
        self.temp_label.setText(self.tr('temperature'))
        
        # Update buttons
        self.save_button.setText(self.tr('save'))
        self.cancel_button.setText(self.tr('cancel'))
        
    def save_settings(self):
        # Update settings from UI
        self.settings['theme'] = self.theme_combo.currentText()
        self.settings['language'] = self.language_combo.currentData()  # Use code, not display name
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
