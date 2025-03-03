from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QLineEdit, QComboBox, QCheckBox, 
                           QPushButton, QSpinBox, QTextEdit, QGroupBox,
                           QFormLayout, QLabel, QListWidget, QMessageBox, QListWidgetItem)
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
        self.current_language = self.translations[self.current_language].get('language', 'en')
        
        self.setWindowTitle(self.tr('settings'))
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.init_ui()
        
    def tr(self, key):
        """Translate a string using the current language"""
        return self.translations.get(self.current_language, {}).get(key, key)
           
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
        
        # Connect to parent's model management functions if available
        if hasattr(self.parent(), 'add_custom_model'):
            self.add_model_button.clicked.connect(self.parent().add_custom_model)
        
        if hasattr(self.parent(), 'show_model_info'):
            self.model_info_button.clicked.connect(lambda: self.parent().show_model_info(
            self.default_model.currentText()))
            
        if hasattr(self.parent(), 'set_default_model'):
            self.set_default_button.clicked.connect(lambda: self.parent().set_default_model(
            self.default_model.currentText(), self))
        
        # Connect remove button to our method
        if hasattr(self.parent(), 'remove_custom_model'):
            self.remove_model_button.clicked.connect(self.remove_custom_model)
        
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
        
        # Model management buttons
        button_layout = QHBoxLayout()
        self.add_model_button = QPushButton("Add Model")
        self.remove_model_button = QPushButton("Remove Model")
        self.model_info_button = QPushButton("Model Info")
        self.set_default_button = QPushButton("Set as Default")
        
        button_layout.addWidget(self.add_model_button)
        button_layout.addWidget(self.remove_model_button)
        button_layout.addWidget(self.model_info_button)
        button_layout.addWidget(self.set_default_button)
        
        layout.addRow("Model Actions:", button_layout)
        
        # Custom models list
        self.custom_models_list = QListWidget()
        layout.addRow("Custom Models:", self.custom_models_list)
        self.populate_custom_models_list()  # Populate the list on creation
        
        # Connect selection change event
        self.custom_models_list.itemSelectionChanged.connect(self.on_custom_model_selection_changed)
        
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
    
    def populate_custom_models_list(self):
        """Populate the custom models list from settings"""
        self.custom_models_list.clear()
        custom_models = self.settings.get('custom_models', {})
        for model_name in custom_models:
            item = QListWidgetItem(model_name)
            self.custom_models_list.addItem(item)
            
    def list_all_models(self):
        """Return a list of all available models (built-in and custom)"""
        built_in_models = ["llama3.2:1b", "deepseek-r1", "mistral:7b", "llama2:13b"]
        custom_models = list(self.settings.get('custom_models', {}).keys())
        return built_in_models + custom_models
    
    def on_custom_model_selection_changed(self):
        """Enable or disable the remove button based on selection"""
        self.remove_model_button.setEnabled(bool(self.custom_models_list.selectedItems()))
    
    def select_model(self):
        """Returns the currently selected model from the custom models list.
        
        Returns:
            tuple: (model_name, is_selected) where model_name is the selected model name 
                  or None if no selection, and is_selected is a boolean.
        """
        selected = self.custom_models_list.selectedItems()
        if not selected:
            return None, False
        
        return selected[0].text(), True
    
    def remove_custom_model(self):
        """Show a dialog to select and remove a custom model"""
        # Get all custom models
        custom_models = self.settings.get('custom_models', {})
        if not custom_models:
            QMessageBox.information(self, 'No Custom Models', 'There are no custom models to remove.')
            return
            
        # Create a model selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Model to Remove")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        
        # Add explanatory label
        label = QLabel("Select a model to remove:")
        layout.addWidget(label)
        
        # Add model selection list
        model_list = QListWidget()
        for model_name in custom_models:
            item = QListWidgetItem(model_name)
            model_list.addItem(item)
        layout.addWidget(model_list)
        
        # Add buttons
        button_layout = QHBoxLayout()
        remove_button = QPushButton("Remove")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(remove_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        # Connect buttons
        remove_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        remove_button.setEnabled(False)
        
        # Enable remove button only when a model is selected
        model_list.itemSelectionChanged.connect(
            lambda: remove_button.setEnabled(bool(model_list.selectedItems()))
        )
        
        # Show dialog and process result
        if dialog.exec() == QDialog.DialogCode.Accepted and model_list.selectedItems():
            model_name = model_list.selectedItems()[0].text()
            self._remove_selected_model(model_name)
    
    def _remove_selected_model(self, model_name):
        """Remove the specified custom model from settings with proper error handling"""
        # Check if it's a built-in model that shouldn't be removed
        built_in_models = ["llama3.2:1b"]
        if model_name in built_in_models:
            QMessageBox.warning(
                self, 
                'Protected Model', 
                f"'{model_name}' is a built-in model and cannot be removed."
            )
            return
        
        # Confirm deletion with more detailed message
        reply = QMessageBox.question(
            self, 
            'Remove Model', 
            f"Are you sure you want to remove the model '{model_name}'?\n\n"
            f"This will remove the model configuration from settings.\n"
            f"The model files themselves will not be deleted.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No  # Default to No for safety
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Remove from settings
                custom_models = self.settings.get('custom_models', {})
                if model_name in custom_models:
                    del custom_models[model_name]
                    self.settings['custom_models'] = custom_models
                    
                    # Save settings immediately
                    with open('settings.json', 'w') as f:
                        json.dump(self.settings, f, indent=4)
                    
                    # If this was the default model, change to a safe default
                    if self.settings.get('default_model') == model_name:
                        self.settings['default_model'] = "llama3.2:1b"
                        self.default_model.setCurrentText("llama3.2:1b")
                    
                    # Repopulate list
                    self.populate_custom_models_list()
                    
                    # Update default model dropdown
                    current_model = self.default_model.currentText()
                    self.default_model.clear()
                    self.default_model.addItems(built_in_models + list(custom_models.keys()))
                    
                    # Try to restore the previous selection, or use default
                    if self.default_model.findText(current_model) >= 0:
                        self.default_model.setCurrentText(current_model)
                    else:
                        self.default_model.setCurrentText("llama3.2:1b")
                    
                    # Pass the change to parent if it exists
                    if hasattr(self.parent(), 'remove_custom_model'):
                        self.parent().remove_custom_model(model_name, self)
                    
                    # Show success message
                    QMessageBox.information(
                        self, 
                        'Model Removed', 
                        f"Model '{model_name}' was successfully removed."
                    )
                else:
                    QMessageBox.warning(
                        self, 
                        'Model Not Found', 
                        f"Model '{model_name}' was not found in custom models."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    'Error', 
                    f"An error occurred while removing the model:\n{str(e)}"
                )

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
            'language': 'en',
            'api_url': 'http://localhost:11434',
            'temperature': 70
        }
        
        # Try to load from file
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            
        return default_settings
