from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                           QComboBox, QLineEdit, QPushButton,
                           QFormLayout, QGroupBox, QScrollArea,
                           QWidget, QHBoxLayout)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QIcon
from PyQt6.QtCore import Qt
import json
import os

class WelcomeScreen(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Initialize translations first
        self.translations = {
            'en': {
                'window_title': 'Welcome to Madick AI Chatbot',
                'welcome_header': 'Welcome to Madick AI',
                'description': 'Your intelligent desktop companion powered by state-of-the-art language models.',
                'basic_settings': 'Basic Settings',
                'default_model': 'Default Model:',
                'model_desc': 'Choose your default AI model. You can change this later.',
                'theme': 'Theme:',
                'theme_desc': 'Select your preferred theme. Dark theme is easier on the eyes.',
                'your_name': 'Your Name:',
                'name_placeholder': 'Enter your name (optional)',
                'name_desc': 'Your name will be used to personalize the chat experience.',
                'language': 'Language:',
                'language_desc': 'Choose your preferred interface language',
                'get_started': 'Get Started!',
                'key_features': 'Key Features',
                'feature_1': '🔄 Multiple AI Models Support',
                'feature_2': '💾 Chat History & Session Management',
                'feature_3': '🔍 Conversation Search',
                'feature_4': '🎤 Voice Input Support',
                'feature_5': '📝 Custom Templates',
                'feature_6': '🌓 Theme Customization',
                'feature_7': '📎 File Attachments',
                'feature_8': '⌨️ Keyboard Shortcuts',
                'quick_shortcuts': 'Quick Shortcuts',
                'shortcut_1': 'Ctrl+Enter: Send message',
                'shortcut_2': 'Ctrl+L: Clear chat',
                'shortcut_3': 'Ctrl+F: Search',
                'shortcut_4': 'Ctrl+T: Toggle theme'
            },
            'fr': {
                'window_title': 'Bienvenue sur Madick AI Chatbot',
                'welcome_header': 'Bienvenue sur Madick AI',
                'description': 'Votre compagnon de bureau intelligent alimenté par des modèles de langage de pointe.',
                'basic_settings': 'Paramètres de base',
                'default_model': 'Modèle par défaut:',
                'model_desc': 'Choisissez votre modèle AI par défaut. Vous pouvez le modifier ultérieurement.',
                'theme': 'Thème:',
                'theme_desc': 'Sélectionnez votre thème préféré. Le thème sombre est plus reposant pour les yeux.',
                'your_name': 'Votre nom:',
                'name_placeholder': 'Entrez votre nom (facultatif)',
                'name_desc': 'Votre nom sera utilisé pour personnaliser l\'expérience de chat.',
                'language': 'Langue:',
                'language_desc': 'Choisissez votre langue d\'interface préférée',
                'get_started': 'Commencer!',
                'key_features': 'Fonctionnalités clés',
                'feature_1': '🔄 Prise en charge de plusieurs modèles IA',
                'feature_2': '💾 Historique de chat et gestion des sessions',
                'feature_3': '🔍 Recherche de conversation',
                'feature_4': '🎤 Support de saisie vocale',
                'feature_5': '📝 Modèles personnalisés',
                'feature_6': '🌓 Personnalisation du thème',
                'feature_7': '📎 Pièces jointes',
                'feature_8': '⌨️ Raccourcis clavier',
                'quick_shortcuts': 'Raccourcis rapides',
                'shortcut_1': 'Ctrl+Entrée: Envoyer un message',
                'shortcut_2': 'Ctrl+L: Effacer le chat',
                'shortcut_3': 'Ctrl+F: Rechercher',
                'shortcut_4': 'Ctrl+T: Changer de thème'
            }
        }
        
        # Initialize settings
        self.settings = self.load_default_settings()
        self.current_language = self.settings.get('language', 'en')
        
        self.setWindowTitle(self.tr('window_title'))
        self.setMinimumSize(600, 700)

        # Setup emoji as window icon
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        font = QFont('Segoe UI Emoji', 40)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "🤖")
        painter.end()
        self.setWindowIcon(QIcon(pixmap))
        
        # Create scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        main_layout = QVBoxLayout(scroll_content)
        
        # Welcome header with icon
        header_layout = QHBoxLayout()
        icon_label = QLabel("🤖")
        icon_label.setFont(QFont("Arial", 48))
        self.header_text = QLabel(self.tr('welcome_header'))
        self.header_text.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        header_layout.addStretch()
        header_layout.addWidget(icon_label)
        header_layout.addWidget(self.header_text)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Add description
        self.desc = QLabel(self.tr('description'))
        self.desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc.setWordWrap(True)
        main_layout.addWidget(self.desc)
        
        # Basic Settings Group
        self.settings_group = QGroupBox(self.tr('basic_settings'))
        form_layout = QFormLayout()
        
        # Model selection with description
        model_widget = QWidget()
        model_layout = QVBoxLayout(model_widget)
        self.model_combo = QComboBox()
        self.model_combo.addItems(["llama3.2:1b", "deepseek-r1", "mistral:7b", "llama2:13b"])
        self.model_combo.setCurrentText(self.settings.get('default_model', 'llama3.2:1b'))
        self.model_desc = QLabel(self.tr('model_desc'))
        self.model_desc.setStyleSheet("color: gray; font-size: 10px;")
        model_layout.addWidget(self.model_combo)
        model_layout.addWidget(self.model_desc)
        form_layout.addRow(self.tr('default_model'), model_widget)
        
        # Theme selection with preview
        theme_widget = QWidget()
        theme_layout = QVBoxLayout(theme_widget)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(self.settings.get('theme', 'dark'))
        self.theme_desc = QLabel(self.tr('theme_desc'))
        self.theme_desc.setStyleSheet("color: gray; font-size: 10px;")
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addWidget(self.theme_desc)
        form_layout.addRow(self.tr('theme'), theme_widget)
        
        # Language selection
        lang_widget = QWidget()
        lang_layout = QVBoxLayout(lang_widget)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Français"])
        self.lang_combo.setCurrentText("English" if self.current_language == 'en' else "Français")
        self.lang_combo.currentTextChanged.connect(self.change_language)
        self.lang_desc = QLabel(self.tr('language_desc'))
        self.lang_desc.setStyleSheet("color: gray; font-size: 10px;")
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addWidget(self.lang_desc)
        form_layout.addRow(self.tr('language'), lang_widget)
        
        # User name
        name_widget = QWidget()
        name_layout = QVBoxLayout(name_widget)
        self.name_input = QLineEdit()
        self.name_input.setText(self.settings.get('user_name', ''))
        self.name_input.setPlaceholderText(self.tr('name_placeholder'))
        self.name_desc = QLabel(self.tr('name_desc'))
        self.name_desc.setStyleSheet("color: gray; font-size: 10px;")
        name_layout.addWidget(self.name_input)
        name_layout.addWidget(self.name_desc)
        form_layout.addRow(self.tr('your_name'), name_widget)
        
        self.settings_group.setLayout(form_layout)
        main_layout.addWidget(self.settings_group)
        
        # Get Started button
        self.start_button = QPushButton(self.tr('get_started'))
        self.start_button.setMinimumHeight(50)
        self.start_button.setStyleSheet("""
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
        self.start_button.clicked.connect(self.save_and_accept)
        main_layout.addWidget(self.start_button)
        
        scroll.setWidget(scroll_content)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)
        
        # Features Overview
        self.features_group = QGroupBox(self.tr('key_features'))
        features_layout = QHBoxLayout()
        
        # Left column
        left_column = QVBoxLayout()
        self.left_feature_labels = []
        left_features = ['feature_1', 'feature_2', 'feature_3', 'feature_4']
        for feature in left_features:
            feature_label = QLabel(self.tr(feature))
            feature_label.setStyleSheet("padding: 5px;")
            left_column.addWidget(feature_label)
            self.left_feature_labels.append((feature, feature_label))
        
        # Right column
        right_column = QVBoxLayout()
        self.right_feature_labels = []
        right_features = ['feature_5', 'feature_6', 'feature_7', 'feature_8']
        for feature in right_features:
            feature_label = QLabel(self.tr(feature))
            feature_label.setStyleSheet("padding: 5px;")
            right_column.addWidget(feature_label)
            self.right_feature_labels.append((feature, feature_label))
        
        # Add columns to main features layout
        left_widget = QWidget()
        left_widget.setLayout(left_column)
        right_widget = QWidget()
        right_widget.setLayout(right_column)
        
        features_layout.addWidget(left_widget)
        features_layout.addWidget(right_widget)
        
        self.features_group.setLayout(features_layout)
        main_layout.addWidget(self.features_group)
        
        # Keyboard shortcuts preview
        self.shortcuts_group = QGroupBox(self.tr('quick_shortcuts'))
        shortcuts_layout = QHBoxLayout()
        
        # Left column
        left_column = QVBoxLayout()
        self.left_shortcut_labels = []
        left_shortcuts = ['shortcut_1', 'shortcut_2']
        for shortcut in left_shortcuts:
            shortcut_label = QLabel(self.tr(shortcut))
            left_column.addWidget(shortcut_label)
            self.left_shortcut_labels.append((shortcut, shortcut_label))
        
        # Right column
        right_column = QVBoxLayout()
        self.right_shortcut_labels = []
        right_shortcuts = ['shortcut_3', 'shortcut_4']
        for shortcut in right_shortcuts:
            shortcut_label = QLabel(self.tr(shortcut))
            right_column.addWidget(shortcut_label)
            self.right_shortcut_labels.append((shortcut, shortcut_label))
        
        # Add columns to main shortcuts layout
        left_widget = QWidget()
        left_widget.setLayout(left_column)
        right_widget = QWidget()
        right_widget.setLayout(right_column)
        
        shortcuts_layout.addWidget(left_widget)
        shortcuts_layout.addWidget(right_widget)
        
        self.shortcuts_group.setLayout(shortcuts_layout)
        main_layout.addWidget(self.shortcuts_group)
        
    def tr(self, key):
        """Translate a string using the current language"""
        return self.translations.get(self.current_language, {}).get(key, key)
        
    def change_language(self, language_name):
        """Change the UI language based on selection"""
        # Map the display name to language code
        lang_map = {"English": "en", "Français": "fr"}
        self.current_language = lang_map.get(language_name, "en")
        
        # Update all UI texts
        self.setWindowTitle(self.tr('window_title'))
        self.header_text.setText(self.tr('welcome_header'))
        self.desc.setText(self.tr('description'))
        self.settings_group.setTitle(self.tr('basic_settings'))
        self.model_desc.setText(self.tr('model_desc'))
        self.theme_desc.setText(self.tr('theme_desc'))
        self.lang_desc.setText(self.tr('language_desc'))
        self.name_input.setPlaceholderText(self.tr('name_placeholder'))
        self.name_desc.setText(self.tr('name_desc'))
        self.start_button.setText(self.tr('get_started'))
        self.features_group.setTitle(self.tr('key_features'))
        self.shortcuts_group.setTitle(self.tr('quick_shortcuts'))
        
        # Update feature labels
        for key, label in self.left_feature_labels + self.right_feature_labels:
            label.setText(self.tr(key))
        
        # Update shortcut labels
        for key, label in self.left_shortcut_labels + self.right_shortcut_labels:
            label.setText(self.tr(key))
        
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
            'user_name': '',
            'language': 'en'
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
        self.settings['language'] = self.current_language
        
        # Save to file
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f, indent=4)
            
        self.accept()
    
    def get_settings(self):
        """Return the current settings"""
        return self.settings
