from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QPushButton, QScrollArea,
                           QComboBox, QLabel, QMessageBox, QStatusBar, QFileDialog,
                           QProgressBar, QSystemTrayIcon, QMenu, QLineEdit, QInputDialog,
                           QSplitter, QTabWidget, QFrame, QToolButton, QListWidget, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QKeySequence, QShortcut
import sys
import json
import markdown
import speech_recognition as sr
from datetime import datetime
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from langchain_ollama import OllamaLLM
from model.database import ChatDatabase
from app.settings_dialog import SettingsDialog
from app.icon_manager import IconManager
import os

class AIResponseThread(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, llm, prompt):
        super().__init__() 
        self.llm = llm
        self.prompt = prompt

    def run(self):
        try:
            response = self.llm.invoke(self.prompt)
            self.response_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))

class MessageBubble(QFrame):
    def __init__(self, is_user=True, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.setup_ui()
        
    def setup_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        
        # Set appropriate styles based on sender
        if self.is_user:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2a5298;
                    border-radius: 10px;
                    margin-left: 80px;
                    margin-right: 10px;
                    padding: 10px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #3f3f3f;
                    border-radius: 10px;
                    margin-left: 10px;
                    margin-right: 80px;
                    padding: 10px;
                }
            """)
            
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(7, 4, 7, 4)
        
        # Header with timestamp and sender
        header_layout = QHBoxLayout()
        self.sender_label = QLabel(ChatBotWindow().settings.get('user_name', 'You') if self.is_user else "AI")
        self.sender_label.setStyleSheet(f"color: {'#ffffff' if self.is_user else '#4fc3f7'}; font-weight: bold;")
        
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: #bbbbbb; font-size: 12px;")
        
        header_layout.addWidget(self.sender_label)
        header_layout.addStretch()
        header_layout.addWidget(self.time_label)
        
        # Message content
        self.content = QTextEdit()
        self.content.setReadOnly(True)
        self.content.setFrameStyle(QFrame.Shape.NoFrame)
        self.content.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: #ffffff;
                border: none;
            }
        """)
        
        # Create action buttons for messages
        actions_layout = QHBoxLayout()
        
        if self.is_user:
            edit_btn = QToolButton()
            edit_btn.setIcon(IconManager.get_icon("edit"))
            edit_btn.setToolTip("Edit message")
            actions_layout.addWidget(edit_btn)
            
        copy_btn = QToolButton()
        copy_btn.setIcon(IconManager.get_icon("copy"))
        copy_btn.setToolTip("Copy to clipboard")
        
        if not self.is_user:
            speak_btn = QToolButton()
            speak_btn.setIcon(IconManager.get_icon("speak"))
            speak_btn.setToolTip("Read aloud")
            actions_layout.addWidget(speak_btn)
            
            save_btn = QToolButton()
            save_btn.setIcon(IconManager.get_icon("bookmark"))
            save_btn.setToolTip("Save response")
            actions_layout.addWidget(save_btn)
        
        actions_layout.addWidget(copy_btn)
        actions_layout.addStretch()
        
        # Add layouts to main layout
        self.layout.addLayout(header_layout)
        self.layout.addWidget(self.content)
        self.layout.addLayout(actions_layout)
        
    def set_content(self, text, timestamp=None):
        self.content.setHtml(text)
        if timestamp:
            self.time_label.setText(timestamp)
        else:
            self.time_label.setText(datetime.now().strftime("%H:%M:%S"))
            
    def append_content(self, text):
        current_html = self.content.toHtml()
        # Remove HTML close tags, add new content and re-add close tags
        if "</body></html>" in current_html:
            current_html = current_html.replace("</body></html>", f"{text}</body></html>")
            self.content.setHtml(current_html)
        else:
            self.content.setHtml(current_html + text)

class VoiceInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Voice Input")
        self.setMinimumWidth(400)
        
        self.layout = QVBoxLayout(self)
        
        self.status_label = QLabel("Press Start to begin recording...")
        self.layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)
        
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Recording")
        self.start_button.clicked.connect(self.start_recording)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.cancel_button)
        
        self.layout.addLayout(button_layout)
        
        self.recognizer = sr.Recognizer()
        self.text = ""
        
    def start_recording(self):
        self.progress_bar.setVisible(True)
        self.status_label.setText("Listening... Speak now")
        self.start_button.setEnabled(False)
        
        # Start recording in a separate thread
        self.recording_thread = QThread()
        self.recording_thread.run = self.record_audio
        self.recording_thread.start()
        
    def record_audio(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5)
                
                self.status_label.setText("Processing speech...")
                
                try:
                    self.text = self.recognizer.recognize_google(audio)
                    self.accept()
                except sr.UnknownValueError:
                    self.status_label.setText("Could not understand audio. Try again.")
                except sr.RequestError:
                    self.status_label.setText("Could not request results. Check your internet connection.")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
        
        self.progress_bar.setVisible(False)
        self.start_button.setEnabled(True)

    def get_text(self):
        return self.text

class ChatBotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Madick AI Chatbot")
        self.setMinimumSize(1200, 800)
        
        # Initialize database
        self.db = ChatDatabase()
        
        # Load settings
        self.load_settings()
        
        # Available models
        self.models = ["llama3.2:1b", "deepseek-r1", "mistral:7b", "llama2:13b"]
        self.current_model = self.settings.get('default_model', "llama3.2:1b")
        self.llm = OllamaLLM(model=self.current_model)
        
        # Setup icons
        self.icon_manager = IconManager()
        self.setWindowIcon(IconManager.get_icon("app"))
        
        # Add status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("color: white; background-color: #1e1e1e;")
        
        # Create toolbar and toolbar layout
        self.toolbar = QWidget()
        self.toolbar_layout = QHBoxLayout(self.toolbar)
        self.toolbar_layout.setContentsMargins(10, 5, 10, 5)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 5px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        
        # System tray setup
        self.setup_system_tray()
        
        # Setup shortcuts
        self.setup_shortcuts()
        
        self.current_theme = self.settings.get('theme', "dark")
        self.current_session = "Default"
        self.sessions = ["Default"]
        
        # Message bubbles container
        self.message_bubbles = []
        
        # Setup UI
        self.setup_splitter_ui()
        
        # Load chat history
        self.load_chat_history()
        
        self.update_status("Ready")
        
    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                self.settings = json.load(f)
        except:
            # Default settings
            self.settings = {
                'theme': 'dark',
                'default_model': 'llama3.2:1b',
                'streaming': True,
                'text_to_speech': False,
                'system_prompt': '',
                'max_history': 50,
                'font_size': 14
            }
            
    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)

    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        try:
            self.tray_icon.setIcon(IconManager.get_icon("app"))
        except:
            pass
        
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(QApplication.quit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def setup_shortcuts(self):
        # Send message shortcut (Ctrl+Enter)
        send_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        send_shortcut.activated.connect(self.send_message)
        
        # Clear chat shortcut (Ctrl+L)
        clear_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        clear_shortcut.activated.connect(self.clear_chat)
        
        # Export chat shortcut (Ctrl+E)
        export_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        export_shortcut.activated.connect(self.export_chat)
        
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(lambda: self.search_input.setFocus())
        
        theme_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        theme_shortcut.activated.connect(self.toggle_theme)
        
        new_session_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_session_shortcut.activated.connect(self.create_new_session)
        
        # Add voice input shortcut (Ctrl+Shift+V)
        voice_shortcut = QShortcut(QKeySequence("Ctrl+Shift+V"), self)
        voice_shortcut.activated.connect(self.start_voice_input)
        
        # Add settings shortcut (Ctrl+,)
        settings_shortcut = QShortcut(QKeySequence("Ctrl+,"), self)
        settings_shortcut.activated.connect(self.open_settings)

    def setup_splitter_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a splitter for sidebar and main content
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create sidebar
        self.sidebar = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(5, 8, 5, 5)
        
        # Logo at the top of sidebar
        logo_label = QLabel("Madick AI")
        logo_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 15px;")
        sidebar_layout.addWidget(logo_label)
        
        # Navigation buttons
        self.chat_nav_btn = QPushButton(" Chat")
        self.chat_nav_btn.setIcon(IconManager.get_icon("chat"))
        self.chat_nav_btn.setStyleSheet(self.get_sidebar_button_style(True))
        self.chat_nav_btn.clicked.connect(lambda: self.tabs.setCurrentWidget(self.chat_tab))
        
        self.templates_nav_btn = QPushButton(" Templates")
        self.templates_nav_btn.setIcon(IconManager.get_icon("template"))
        self.templates_nav_btn.setStyleSheet(self.get_sidebar_button_style())
        self.templates_nav_btn.clicked.connect(lambda: self.tabs.setCurrentWidget(self.templates_tab))
        
        self.history_nav_btn = QPushButton(" History")
        self.history_nav_btn.setIcon(IconManager.get_icon("history"))
        self.history_nav_btn.setStyleSheet(self.get_sidebar_button_style())
        self.history_nav_btn.clicked.connect(lambda: self.tabs.setCurrentWidget(self.history_tab))
        
        self.files_nav_btn = QPushButton(" Files")
        self.files_nav_btn.setIcon(IconManager.get_icon("file"))
        self.files_nav_btn.setStyleSheet(self.get_sidebar_button_style())
        self.files_nav_btn.clicked.connect(lambda: self.tabs.setCurrentWidget(self.files_tab))
        
        
        sidebar_layout.addWidget(self.chat_nav_btn)
        sidebar_layout.addWidget(self.templates_nav_btn)
        sidebar_layout.addWidget(self.history_nav_btn)
        sidebar_layout.addWidget(self.files_nav_btn)
        
        sidebar_layout.addStretch()
        
        # Settings button at bottom of sidebar
        self.settings_btn = QPushButton(" Settings")
        self.settings_btn.setIcon(IconManager.get_icon("settings"))
        self.settings_btn.clicked.connect(self.open_settings)
        sidebar_layout.addWidget(self.settings_btn)
        
        # Main content area
        self.content_area = QWidget()
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add toolbar to content layout
        content_layout.addWidget(self.toolbar)
        
        # Create tab widget for different sections
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3f3f3f;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #2b2b2b;
                color: #bbbbbb;
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #3f3f3f;
                color: white;
            }
        """)
        
        # Create chat tab
        self.chat_tab = QWidget()
        chat_tab_layout = QVBoxLayout(self.chat_tab)
        
        # Model selection area
        model_layout = QHBoxLayout()
        model_label = QLabel("Model:")
        model_label.setStyleSheet("color: white;")
        self.model_combo = QComboBox()
        self.model_combo.addItems(self.models)
        self.model_combo.setCurrentText(self.current_model)
        self.model_combo.currentTextChanged.connect(self.change_model)
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        model_layout.addStretch()
        
        # Session selection
        session_label = QLabel("Session:")
        session_label.setStyleSheet("color: white;")
        self.session_combo = QComboBox()
        self.session_combo.addItems(self.sessions)
        self.session_combo.setStyleSheet(self.get_combo_style())
        self.session_combo.currentTextChanged.connect(self.change_session)
        
        new_session_btn = QToolButton()
        new_session_btn.setIcon(IconManager.get_icon("plus"))
        new_session_btn.setToolTip("New Session")
        new_session_btn.clicked.connect(self.create_new_session)
        
        model_layout.addWidget(session_label)
        model_layout.addWidget(self.session_combo)
        model_layout.addWidget(new_session_btn)
        
        # Add buttons to model layout
        clear_btn = QPushButton("Clear")
        clear_btn.setIcon(IconManager.get_icon("trash"))
        clear_btn.setStyleSheet(self.get_button_style("#d32f2f"))
        clear_btn.clicked.connect(self.clear_chat)
        model_layout.addWidget(clear_btn)
        
        export_btn = QPushButton("Export")
        export_btn.setIcon(IconManager.get_icon("export"))
        export_btn.setStyleSheet(self.get_button_style("#2196F3"))
        export_btn.clicked.connect(self.export_chat)
        model_layout.addWidget(export_btn)
        
        chat_tab_layout.addLayout(model_layout)
        
        # Chat messages scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #2b2b2b;
            }
            QScrollBar:vertical {
                border: none;
                background: #2b2b2b;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #666666;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.setSpacing(15)
        self.chat_layout.addStretch()
        
        self.scroll_area.setWidget(self.chat_container)
        chat_tab_layout.addWidget(self.scroll_area)
        
        # Input area with controls
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 10, 0, 0)
        
        # Add prompt templates and formatting buttons
        formatting_layout = QHBoxLayout()
        
        file_btn = QToolButton()
        file_btn.setIcon(IconManager.get_icon("attachment"))
        file_btn.setToolTip("Attach File")
        file_btn.clicked.connect(self.attach_file)
        
        voice_btn = QToolButton()
        voice_btn.setIcon(IconManager.get_icon("microphone"))
        voice_btn.setToolTip("Voice Input (Ctrl+Shift+V)")
        voice_btn.clicked.connect(self.start_voice_input)
        
        template_label = QLabel("Template:")
        template_label.setStyleSheet("color: white;")
        
        self.template_combo = QComboBox()
        self.template_combo.addItems(["None", "Code Explanation", "Summarize", "Translate", "Custom..."])
        self.template_combo.setStyleSheet(self.get_combo_style())
        self.template_combo.currentTextChanged.connect(self.apply_template)
        
        formatting_layout.addWidget(file_btn)
        formatting_layout.addWidget(voice_btn)
        formatting_layout.addWidget(template_label)
        formatting_layout.addWidget(self.template_combo)
        formatting_layout.addStretch()
        
        #streaming_check = QCheckBox("Streaming Responses")
        #streaming_check.setChecked(self.streaming_enabled)
        #streaming_check.toggled.connect(self.toggle_streaming)
        #formatting_layout.addWidget(streaming_check)
        
        input_layout.addLayout(formatting_layout)
        
        # Text input and send button
        message_layout = QHBoxLayout()
        
        self.input_box = QTextEdit()
        self.input_box.setFixedHeight(100)
        self.input_box.setStyleSheet("""
            QTextEdit {
                background-color: #3f3f3f;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }
        """)
        
        self.send_button = QPushButton("Send")
        self.send_button.setIcon(IconManager.get_icon("send"))
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        
        message_layout.addWidget(self.input_box)
        message_layout.addWidget(self.send_button)
        
        input_layout.addLayout(message_layout)
        chat_tab_layout.addWidget(input_container)
        
        # Create templates tab
        self.templates_tab = QWidget()
        templates_layout = QVBoxLayout(self.templates_tab)
        
        # Templates list
        templates_layout.addWidget(QLabel("Available Templates"))
        self.templates_list = QListWidget()
        self.load_templates()
        templates_layout.addWidget(self.templates_list)
        
        # Create history tab
        self.history_tab = QWidget()
        history_layout = QVBoxLayout(self.history_tab)
        
        # Search in history
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in chat history...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.search_input.textChanged.connect(self.search_chat)
        
        search_layout.addWidget(self.search_input)
        history_layout.addLayout(search_layout)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.load_history_item)
        history_layout.addWidget(self.history_list)
        
        # Create files tab
        self.files_tab = QWidget()
        files_layout = QVBoxLayout(self.files_tab)
        
        files_layout.addWidget(QLabel("Uploaded Files"))
        self.files_list = QListWidget()
        files_layout.addWidget(self.files_list)
        
        upload_btn = QPushButton("Upload File")
        upload_btn.clicked.connect(self.attach_file)
        files_layout.addWidget(upload_btn)
        
        # Add tabs to tab widget
        self.tabs.addTab(self.chat_tab, "Chat")
        self.tabs.addTab(self.templates_tab, "Templates")
        self.tabs.addTab(self.history_tab, "History")
        self.tabs.addTab(self.files_tab, "Files")
        
        content_layout.addWidget(self.tabs)
        
        # Add progress bar to layout
        content_layout.addWidget(self.progress_bar)
        
        # Add both sidebar and content area to splitter
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.content_area)
        
        # Set initial splitter sizes - 20% sidebar, 80% content
        self.splitter.setSizes([200, 800])
        
        main_layout.addWidget(self.splitter)
        
        # Set theme
        if self.current_theme == "dark":
            self.set_dark_theme()
        else:
            self.set_light_theme()
            
    def get_sidebar_button_style(self, selected=False):
        if selected:
            return """
                QPushButton {
                    background-color: #3f3f3f;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                    text-align: left;
                    font-weight: bold;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: transparent;
                    color: #bbbbbb;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #3f3f3f;
                    color: white;
                }
            """

    def get_combo_style(self):
        return """
            QComboBox {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #3f3f3f;
                color: white;
                selection-background-color: #4CAF50;
            }
        """

    def get_button_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
        """

    def load_templates(self):
        templates = [
            "Code Explanation - Explain this code in detail",
            "Summarize - Provide a concise summary",
            "Translate - Translate to [language]",
            "Pros and Cons - List pros and cons",
            "Writing Assistant - Help me write",
            "Data Analysis - Analyze this dataset"
        ]
        
        self.templates_list.clear()
        for template in templates:
            self.templates_list.addItem(template)

    def apply_template(self, template_name):
        if template_name == "None":
            return
            
        if template_name == "Code Explanation":
            self.input_box.setText("Explain this code in detail:\n```\n\n```")
            
        elif template_name == "Summarize":
            self.input_box.setText("Please summarize the following text:\n\n")

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.set_light_theme()
        else:
            self.set_dark_theme()

    def set_dark_theme(self):
        self.current_theme = "dark"
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QWidget { background-color: #1e1e1e; }
        """)

    def set_light_theme(self):
        self.current_theme = "light"
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f5; }
            QWidget { background-color: #f5f5f5; color: #2c3e50; }
            QLabel { color: #2c3e50; }
            QPushButton { 
                background-color: #e0e0e0; 
                color: #2c3e50;
                border: 1px solid #bdbdbd;
            }
            QPushButton:hover {
                background-color: #d5d5d5;
            }
            QTextEdit {
                background-color: white;
                color: #2c3e50;
                border: 1px solid #bdbdbd;
            }
            QComboBox {
                background-color: white;
                color: #2c3e50;
                border: 1px solid #bdbdbd;
            }
            QListWidget {
                background-color: white;
                color: #2c3e50;
                border: 1px solid #bdbdbd;
            }
            QStatusBar {
                background-color: #e0e0e0;
                color: #2c3e50;
            }
        """)

    def create_new_session(self):
        name, ok = QInputDialog.getText(self, "New Session", "Enter session name:")
        if ok and name:
            self.sessions.append(name)
            self.session_combo.addItem(name)
            self.session_combo.setCurrentText(name)
            self.current_session = name

    def change_session(self, session_name):
        self.current_session = session_name
        self.load_chat_history()

    def search_chat(self):
        search_text = self.search_input.text().lower()
        
        # Reset all message highlights
        for bubble in self.message_bubbles:
            content = bubble.content.toPlainText()
            if search_text and search_text in content.lower():
                bubble.setStyleSheet(bubble.styleSheet() + "border: 2px solid #FFEB3B;")
            else:
                bubble.setStyleSheet(bubble.styleSheet().replace("border: 2px solid #FFEB3B;", ""))

    def show_shortcuts(self):
        shortcuts = """
        <h3>Keyboard Shortcuts</h3>
        <table>
        <tr><td><b>Ctrl+Enter</b></td><td>Send message</td></tr>
        <tr><td><b>Ctrl+L</b></td><td>Clear chat</td></tr>
        <tr><td><b>Ctrl+E</b></td><td>Export chat</td></tr>
        <tr><td><b>Ctrl+F</b></td><td>Focus search</td></tr>
        <tr><td><b>Ctrl+T</b></td><td>Toggle theme</td></tr>
        <tr><td><b>Ctrl+N</b></td><td>New session</td></tr>
        </table>
        """
        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts)

    def send_message(self):
        user_message = self.input_box.toPlainText().strip()
        if not user_message:
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Create and add user message bubble
        user_bubble = MessageBubble(is_user=True)
        user_bubble.set_content(user_message, timestamp)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, user_bubble)
        self.message_bubbles.append(user_bubble)
        
        self.progress_bar.setVisible(True)
        self.send_button.setEnabled(False)
        self.update_status("Waiting for AI response...")
        
        # Store user message for later use
        self.current_user_message = user_message
        
        # Create and start response thread
        self.response_thread = AIResponseThread(self.llm, user_message)
        self.response_thread.response_ready.connect(self.handle_ai_response)
        self.response_thread.error_occurred.connect(self.handle_ai_error)
        self.response_thread.finished.connect(self.on_response_complete)
        self.response_thread.start()
        
        self.input_box.clear()
        
        # Scroll to bottom
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def handle_ai_response(self, response):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Create new AI response bubble
        ai_bubble = MessageBubble(is_user=False)
        ai_bubble.set_content(self.format_response(response), timestamp)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, ai_bubble)
        self.message_bubbles.append(ai_bubble)         

        self.db.save_conversation(self.current_model, self.current_user_message, response, self.current_session)
        
        # Scroll to bottom
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

        def handle_token(self, token):
            """Handle streaming tokens"""
            if not hasattr(self, 'current_ai_bubble'):
                # Create new AI response bubble for streaming
                self.current_ai_bubble = MessageBubble(is_user=False)
                self.current_ai_bubble.set_content("", datetime.now().strftime("%H:%M:%S"))
                self.chat_layout.insertWidget(self.chat_layout.count() - 1, self.current_ai_bubble)
                self.message_bubbles.append(self.current_ai_bubble)
                
            # Append token to current bubble
            self.current_ai_bubble.append_content(token)
            
            # Scroll to bottom
            self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().maximum()
            )

    def handle_token(self, token):
        """Handle streaming tokens"""
        if not hasattr(self, 'current_ai_bubble'):
            # Create new AI response bubble for streaming
            self.current_ai_bubble = MessageBubble(is_user=False)
            self.current_ai_bubble.set_content("", datetime.now().strftime("%H:%M:%S"))
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, self.current_ai_bubble)
            self.message_bubbles.append(self.current_ai_bubble)
            
        # Append token to current bubble
        self.current_ai_bubble.append_content(token)
        
        # Scroll to bottom
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def handle_ai_error(self, error_message):
        # Create error message bubble
        error_bubble = MessageBubble(is_user=False)
        error_bubble.setStyleSheet("""
            QFrame {
                background-color: #d32f2f;
                border-radius: 10px;
                margin-left: 10px;
                margin-right: 80px;
                padding: 10px;
            }
        """)
        error_bubble.set_content(f"Error: {error_message}")
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, error_bubble)
        self.message_bubbles.append(error_bubble)

    def on_response_complete(self):
        self.progress_bar.setVisible(False)
        self.send_button.setEnabled(True)
        self.update_status("Ready")
        if hasattr(self, 'current_ai_bubble'):
            delattr(self, 'current_ai_bubble')

    def format_response(self, text):
        # Convert markdown to HTML
        html = markdown.markdown(text)
        
        # Find and highlight code blocks
        code_blocks = text.split("```")
        for i in range(1, len(code_blocks), 2):
            try:
                lang = code_blocks[i].split("\n")[0]
                code = "\n".join(code_blocks[i].split("\n")[1:])
                lexer = get_lexer_by_name(lang, stripall=True)
                formatted_code = highlight(code, lexer, HtmlFormatter(style='monokai'))
                html = html.replace(code_blocks[i], formatted_code)
            except:
                continue
                
        return html

    def export_chat(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Chat History", "", "JSON Files (*.json);;Text Files (*.txt)")
        if filename:
            conversations = self.db.get_recent_conversations()
            if filename.endswith('.json'):
                with open(filename, 'w') as f:
                    json.dump([{
                        'timestamp': conv[1],
                        'model': conv[2],
                        'user_message': conv[3],
                        'ai_response': conv[4]
                    } for conv in conversations], f, indent=2)
            else:
                with open(filename, 'w') as f:
                    for conv in conversations:
                        f.write(f"Time: {conv[1]}\nModel: {conv[2]}\n")
                        f.write(f"User: {conv[3]}\nAI: {conv[4]}\n\n")

    def update_status(self, message):
        self.status_bar.showMessage(message)

    def change_model(self, model_name):
        self.current_model = model_name
        self.llm = OllamaLLM(model=model_name)
        
        # Add system message bubble
        system_bubble = MessageBubble(is_user=False)
        system_bubble.setStyleSheet("""
            QFrame {
                background-color: #ff9800;
                border-radius: 10px;
                margin-left: 10px;
                margin-right: 80px;
                padding: 10px;
            }
        """)
        system_bubble.set_content(f"Switched to {model_name} model")
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, system_bubble)
        self.message_bubbles.append(system_bubble)

    def clear_chat(self):
        reply = QMessageBox.question(self, 'Clear Chat', 
                                   'Are you sure you want to clear the chat history?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Clear all message bubbles
            while self.chat_layout.count() > 1:  # Keep the stretch at the end
                item = self.chat_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.message_bubbles.clear()
            self.db.clear_history()

    def load_chat_history(self):
        """Load chat history from database"""
        # Clear existing messages
        while self.chat_layout.count() > 1:  # Keep the stretch at the end
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        conversations = self.db.get_recent_conversations(self.current_session)
        for conv in conversations[::-1]:  # Display in chronological order
            _, timestamp, model, user_msg, ai_resp, session = conv
            
            # Create user message bubble
            user_bubble = MessageBubble(is_user=True)
            user_bubble.set_content(user_msg, timestamp)
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, user_bubble)
            
            # Create AI response bubble
            ai_bubble = MessageBubble(is_user=False)
            ai_bubble.set_content(self.format_response(ai_resp), timestamp)
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, ai_bubble)
            
            self.message_bubbles.extend([user_bubble, ai_bubble])

    def closeEvent(self, event):
        self.hide()
        self.tray_icon.showMessage(
            "ChatBot Minimized",
            "Application is still running in the system tray.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
        event.ignore()

    def start_voice_input(self):
        """Open voice input dialog and add transcribed text to input box"""
        dialog = VoiceInputDialog(self)
        if dialog.exec():
            transcribed_text = dialog.get_text()
            if transcribed_text:
                current_text = self.input_box.toPlainText()
                if (current_text):
                    self.input_box.setPlainText(f"{current_text}\n{transcribed_text}")
                else:
                    self.input_box.setPlainText(transcribed_text)
                self.input_box.setFocus()
    
    def attach_file(self):
        """Allow the user to attach a file to the conversation"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Attach File", "", "All Files (*.*)")
        
        if file_path:
            file_name = os.path.basename(file_path)
            # Add file reference to the input box
            current_text = self.input_box.toPlainText()
            file_text = f"\n[Attached file: {file_name}]\n"
            
            if current_text:
                self.input_box.setPlainText(current_text + file_text)
            else:
                self.input_box.setPlainText(file_text)
                
            # Add file to the files list
            self.files_list.addItem(file_name)
            
            # Store file path for later use
            if not hasattr(self, 'attached_files'):
                self.attached_files = {}
            self.attached_files[file_name] = file_path
    
    def open_settings(self):
        """Open the settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Reload settings
            self.load_settings()
            
            # Apply settings changes
            self.current_theme = self.settings.get('theme', 'dark')
            if self.current_theme == 'dark':
                self.set_dark_theme()
            else:
                self.set_light_theme()
                
            # Update the model if changed
            new_model = self.settings.get('default_model')
            if new_model != self.current_model:
                self.current_model = new_model
                self.model_combo.setCurrentText(new_model)
                self.llm = OllamaLLM(model=new_model)
                
            # Update streaming setting
            self.streaming_enabled = self.settings.get('streaming', True)
            
            # Update UI
            self.update_status("Settings updated")
    
    def load_history_item(self, item):
        """Load a selected history item into the chat"""
        text = item.text()
        self.input_box.setPlainText(text)
    
    def toggle_streaming(self, enabled):
        """Toggle streaming responses on/off"""
        self.streaming_enabled = enabled
        self.settings['streaming'] = enabled
        self.save_settings()
        
        status = "enabled" if enabled else "disabled"
        self.update_status(f"Streaming responses {status}")

def main():
    app = QApplication(sys.argv)
    window = ChatBotWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
