from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QPushButton, QScrollArea,
                           QComboBox, QLabel, QMessageBox, QStatusBar, QFileDialog,
                           QProgressBar, QSystemTrayIcon, QMenu, QLineEdit, QInputDialog,
                           QSplitter, QTabWidget, QFrame, QToolButton, QListWidget, QDialog,
                           QListWidgetItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject, QSize
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
    """A custom widget for displaying chat messages with enhanced features and styling."""
    
    def __init__(self, is_user=True, parent=None, chat_window=None):
        super().__init__(parent)
        self.is_user = is_user
        self.chat_window = chat_window
        self._content = ""
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize and setup the UI components with optimized styling."""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        
        # Apply cached styles based on message type
        self.setStyleSheet(self._get_bubble_style())
        
        # Initialize layouts with optimized margins
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(7, 4, 7, 4)
        self.layout.setSpacing(4)
        
        # Setup header with optimized layout
        self._setup_header()
        
        # Setup content area
        self._setup_content()
        
        # Setup action buttons
        self._setup_actions()
        
        # Setup context menu
        self._setup_context_menu()
        
    def _get_bubble_style(self):
        """Return cached styles for the bubble."""
        return """
            QFrame {
                background-color: %(bg_color)s;
                border-radius: 10px;
                margin-left: %(margin_left)s;
                margin-right: %(margin_right)s;
                padding: 10px;
            }
        """ % {
            'bg_color': '#2a5298' if self.is_user else '#3f3f3f',
            'margin_left': '80px' if self.is_user else '10px',
            'margin_right': '10px' if self.is_user else '80px'
        }
        
    def _setup_header(self):
        """Setup the header section with sender info and timestamp."""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        # Optimize sender name retrieval
        sender_name = (self.chat_window.settings.get('user_name', 'You') 
                      if self.chat_window and hasattr(self.chat_window, 'settings')
                      else 'You') if self.is_user else 'AI'
        
        self.sender_label = QLabel(sender_name)
        self.sender_label.setStyleSheet(
            f"color: {'#ffffff' if self.is_user else '#4fc3f7'}; font-weight: bold;"
        )
        
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: #bbbbbb; font-size: 12px;")
        
        header_layout.addWidget(self.sender_label)
        header_layout.addStretch()
        header_layout.addWidget(self.time_label)
        
        self.layout.addLayout(header_layout)
        
    def _setup_content(self):
        """Setup the content area with optimized text display."""
        self.content = QTextEdit()
        self.content.setReadOnly(True)
        self.content.setFrameStyle(QFrame.Shape.NoFrame)
        self.content.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: #ffffff;
                border: none;
                selection-background-color: #666666;
                selection-color: #ffffff;
            }
        """)
        self.content.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.content.document().setDocumentMargin(0)
        
        # Connect to documentSizeChanged for dynamic height adjustment
        self.content.document().documentLayout().documentSizeChanged.connect(
            self._adjust_content_height
        )
        
        self.layout.addWidget(self.content)
        
    def _adjust_content_height(self):
        """Dynamically adjust content height based on text content."""
        doc_height = self.content.document().size().height()
        margins = self.content.contentsMargins()
        total_margins = margins.top() + margins.bottom() + 10
        
        # Set minimum and maximum heights with scrollbar activation threshold
        min_height = 30
        max_height = 300
        
        if doc_height <= max_height:
            self.content.setFixedHeight(int(max(min_height, doc_height + total_margins)))
            self.content.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        else:
            self.content.setFixedHeight(max_height)
            self.content.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
    def _setup_actions(self):
        """Setup action buttons with improved functionality."""
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(4)
        
        buttons = []
        
        if self.is_user:
            edit_btn = self._create_action_button("edit", "Edit message", self._handle_edit)
            buttons.append(edit_btn)
            
        copy_btn = self._create_action_button("copy", "Copy to clipboard", self._handle_copy)
        buttons.append(copy_btn)
        
        if not self.is_user:
            speak_btn = self._create_action_button("speak", "Read aloud", self._handle_speak)
            save_btn = self._create_action_button("bookmark", "Save response", self._handle_save)
            buttons.extend([speak_btn, save_btn])
        
        for btn in buttons:
            actions_layout.addWidget(btn)
            
        actions_layout.addStretch()
        self.layout.addLayout(actions_layout)
        
    def _create_action_button(self, icon_name, tooltip, callback):
        """Create an action button with specified parameters."""
        btn = QToolButton()
        btn.setIcon(IconManager.get_icon(icon_name))
        btn.setToolTip(tooltip)
        btn.setIconSize(QSize(16, 16))
        btn.setFixedSize(24, 24)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(callback)
        return btn
        
    def _setup_context_menu(self):
        """Setup context menu for additional options."""
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
    def set_content(self, text, timestamp=None):
        """Set the message content with optimized HTML handling."""
        self._content = text
        self.content.setHtml(text)
        
        if timestamp:
            self.time_label.setText(timestamp)
        else:
            self.time_label.setText(datetime.now().strftime("%H:%M:%S"))
            
        # Force layout update to ensure proper sizing
        QApplication.processEvents()
        self._adjust_content_height()
        
    def append_content(self, text):
        """Append content to the message with optimized HTML handling."""
        self._content += text
        current_html = self.content.toHtml()
        
        if "</body></html>" in current_html:
            self.content.setHtml(
                current_html.replace("</body></html>", f"{text}</body></html>")
            )
        else:
            self.content.setHtml(current_html + text)
            
        # Force layout update to ensure proper sizing
        QApplication.processEvents()
        self._adjust_content_height()
            
    def _handle_copy(self):
        """Copy message content to clipboard."""
        QApplication.clipboard().setText(self.content.toPlainText())
        
        # Show feedback to user with different message for AI responses
        QApplication.clipboard().setText(self.content.toPlainText())
        if self.chat_window:
            self.chat_window.update_status("Message copied to clipboard")
        
    def _handle_edit(self):
        """Handle message editing."""
        if self.chat_window and self.is_user:
            text = self.content.toPlainText()
            self.chat_window.input_box.setPlainText(text)
            self.chat_window.input_box.setFocus()
            self.chat_window.update_status("Message ready for editing")
            
    def _handle_speak(self):
        """Handle text-to-speech functionality."""
        if self.chat_window and not self.is_user:
            self.chat_window.update_status("Text-to-speech feature initiated")
            # Placeholder for TTS implementation
            QMessageBox.information(
                self.chat_window, 
                "Text-to-Speech", 
                "This feature will be implemented in a future update."
            )
            
    def _handle_save(self):
        """Handle saving the response."""
        if self.chat_window and not self.is_user:
            text = self.content.toPlainText()
            
            # First ensure the conversation is saved to database
            if hasattr(self.chat_window, 'current_user_message') and hasattr(self.chat_window, 'db'):
                # Get the previous user message that prompted this response
                user_message = getattr(self.chat_window, 'current_user_message', "")
                
                # Save to database if not empty
                if user_message and text:
                    try:
                        # Save to database with current session
                        self.chat_window.db.save_conversation(
                            self.chat_window.current_model,
                            user_message,
                            text,
                            self.chat_window.current_session
                        )
                        self.chat_window.update_status("Response saved to history")
                        
                        # Refresh the history list if we're in the history tab
                        if self.chat_window.tabs.currentWidget() == self.chat_window.history_tab:
                            self.chat_window.load_chat_history()
                    except Exception as e:
                        self.chat_window.update_status(f"Error saving to database: {str(e)}")
            
            # Then handle file saving
            filename, _ = QFileDialog.getSaveFileName(
                self.chat_window,
                "Save Response",
                "",
                "Text Files (*.txt);;HTML Files (*.html);;All Files (*.*)"
            )
            
            if filename:
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        # Save as HTML if that format was selected
                        if filename.endswith('.html'):
                            f.write(self.content.toHtml())
                        else:
                            f.write(text)
                    self.chat_window.update_status(f"Response saved to {filename}")
                except Exception as e:
                    self.chat_window.update_status(f"Error saving file: {str(e)}")
            
    def _show_context_menu(self, position):
        """Show context menu with additional options."""
        menu = QMenu(self)
        menu.addAction("Copy", self._handle_copy)
        
        if self.is_user:
            menu.addAction("Edit", self._handle_edit)
        else:
            menu.addAction("Save As...", self._handle_save)
            menu.addAction("Read Aloud", self._handle_speak)
            
        menu.exec(self.mapToGlobal(position))

class VoiceInputDialog(QDialog):
    recording_finished = pyqtSignal(str)
    status_update = pyqtSignal(str)  # New signal for status updates

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_signals()
        self.recognizer = sr.Recognizer()
        self.text = ""
        self.is_recording = False

    def setup_ui(self):
        """Initialize and setup UI components"""
        self.setWindowTitle("Voice Input")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
            QProgressBar {
                border: 2px solid #555555;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Status label with icon
        status_layout = QHBoxLayout()
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(24, 24)
        self.status_label = QLabel("Press Start to begin recording...")
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_label, stretch=1)
        self.layout.addLayout(status_layout)
        
        # Enhanced progress visualization
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)
        
        # Audio level indicator
        self.level_bar = QProgressBar()
        self.level_bar.setRange(0, 100)
        self.level_bar.setTextVisible(False)
        self.level_bar.setVisible(False)
        self.layout.addWidget(self.level_bar)
        
        # Buttons with icons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Recording")
        self.start_button.setIcon(IconManager.get_icon("microphone"))
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setIcon(IconManager.get_icon("cancel"))
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)

    def setup_signals(self):
        """Setup signal connections"""
        self.start_button.clicked.connect(self.toggle_recording)
        self.cancel_button.clicked.connect(self.reject)
        self.recording_finished.connect(self.on_recording_finished)
        self.status_update.connect(self.update_status)

    def toggle_recording(self):
        """Toggle recording state"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start voice recording with enhanced error handling"""
        try:
            # Verify microphone availability
            if not sr.Microphone.list_microphone_names():
                raise OSError("No microphone detected")
            
            self.is_recording = True
            self.progress_bar.setVisible(True)
            self.level_bar.setVisible(True)
            self.start_button.setText("Stop Recording")
            self.update_status("Initializing microphone...", "recording")
            
            # Create and setup worker thread
            self.worker_thread = QThread()
            self.worker = VoiceWorker(self.recognizer)
            self.worker.moveToThread(self.worker_thread)
            
            # Connect all signals
            self.worker_thread.started.connect(self.worker.record)
            self.worker.finished.connect(self.worker_thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker_thread.finished.connect(self.worker_thread.deleteLater)
            self.worker.error.connect(self.handle_error)
            self.worker.result.connect(self.handle_result)
            self.worker.status.connect(lambda s: self.update_status(s, "info"))
            self.worker.audio_level.connect(self.update_audio_level)
            
            self.worker_thread.start()
            
        except Exception as e:
            self.handle_error(str(e))

    def stop_recording(self):
        """Stop current recording"""
        if hasattr(self, 'worker'):
            self.worker.stop()
            self.is_recording = False
            self.start_button.setText("Start Recording")
            self.update_status("Recording stopped", "info")

    def update_status(self, message, status_type="info"):
        """Update status with visual indicators"""
        self.status_label.setText(message)
        icon_name = {
            "info": "info",
            "error": "error",
            "recording": "microphone",
            "success": "success"
        }.get(status_type, "info")
        self.status_icon.setPixmap(IconManager.get_icon(icon_name).pixmap(24, 24))

    def update_audio_level(self, level):
        """Update audio level visualization"""
        self.level_bar.setValue(int(level * 100))

    def handle_error(self, error_msg):
        """Handle errors with visual feedback"""
        self.is_recording = False
        self.progress_bar.setVisible(False)
        self.level_bar.setVisible(False)
        self.start_button.setEnabled(True)
        self.start_button.setText("Start Recording")
        self.update_status(f"Error: {error_msg}", "error")
        QMessageBox.warning(self, "Error", error_msg)

    def handle_result(self, text):
        """Handle successful transcription"""
        self.text = text
        self.update_status("Recording successful!", "success")
        self.accept()

    def on_recording_finished(self):
        """Clean up after recording"""
        self.is_recording = False
        self.progress_bar.setVisible(False)
        self.level_bar.setVisible(False)
        self.start_button.setEnabled(True)
        self.start_button.setText("Start Recording")

    def get_text(self):
        """Return transcribed text"""
        return self.text

    def closeEvent(self, event):
        """Handle dialog close"""
        if self.is_recording:
            self.stop_recording()
        event.accept()

class VoiceWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(str)
    status = pyqtSignal(str)  # New signal for status updates
    audio_level = pyqtSignal(float)  # New signal for audio levels

    def __init__(self, recognizer, language='en-US', timeout=5, phrase_time_limit=10):
        super().__init__()
        self.recognizer = recognizer
        self.language = language
        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit
        self._is_recording = False

    def record(self):
        """Record and transcribe audio with enhanced error handling and feedback"""
        try:
            with sr.Microphone() as source:
                self.status.emit("Adjusting for ambient noise...")
                # More aggressive noise adjustment
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.energy_threshold = 300
                self.recognizer.adjust_for_ambient_noise(source, duration=1)

                self.status.emit("Listening...")
                self._is_recording = True

                # Enhanced audio capture with energy level feedback
                audio = self.recognizer.listen(
                    source,
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_time_limit,
                    callback=lambda _, level: self.audio_level.emit(level)
                )

                self.status.emit("Processing speech...")
                
                try:
                    # Try multiple recognition services
                    text = self._try_recognition(audio)
                    if text:
                        self.result.emit(text)
                    else:
                        self.error.emit("Speech recognition failed with all available services")
                        
                except sr.UnknownValueError:
                    self.error.emit("Could not understand audio. Please speak more clearly")
                except sr.RequestError as e:
                    self.error.emit(f"Service error: {str(e)}")

        except Exception as e:
            self.error.emit(f"Recording error: {str(e)}")
        finally:
            self._is_recording = False
            self.finished.emit()

    def _try_recognition(self, audio):
        """Try multiple speech recognition services"""
        services = [
            (self.recognizer.recognize_google, {'language': self.language}),
            (self.recognizer.recognize_sphinx, {'language': self.language}),
        ]

        for recognizer_func, kwargs in services:
            try:
                return recognizer_func(audio, **kwargs)
            except:
                continue
        return None

    def stop(self):
        """Stop current recording"""
        self._is_recording = False

    @property
    def is_recording(self):
        """Check if recording is in progress"""
        return self._is_recording

class ChatBotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Madick Chatbot")
        self.setMinimumSize(800, 600)
        
        # Initialize database
        self.db = ChatDatabase()
        
        # Load settings
        self.load_settings()
        
        # Available models
        self.models = ["llama3.2:1b", "deepseek-r1", "mistral:7b"]
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
        main_layout.setSpacing(0)
        
        # Create a splitter for sidebar and main content
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)  # Thinner splitter handle
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #3f3f3f;
            }
        """)
        
        # Create sidebar with gradient background
        self.sidebar = QWidget()
        self.sidebar.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #2b2b2b, stop:1 #1e1e1e);
                border-right: 1px solid #3f3f3f;
            }
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(8, 12, 8, 8)
        sidebar_layout.setSpacing(8)
        
        # Enhanced logo section
        logo_label = QLabel("Madick AI")
        logo_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
            padding: 10px;
            border-bottom: 1px solid #3f3f3f;
            margin-bottom: 15px;
        """)
        sidebar_layout.addWidget(logo_label)
        
        # Create tabs widget
        self.tabs = QTabWidget()
        self.tabs.tabBar().setVisible(False)
        self.tabs.setDocumentMode(True)
        
        # Enhanced navigation buttons with hover effects
        nav_buttons_style = """
            QPushButton {
                text-align: left;
                padding: 12px 15px;
                border: none;
                border-radius: 8px;
                margin: 2px 0px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3f3f3f;
            }
            QPushButton[active="true"] {
                background-color: #4CAF50;
                color: white;
            }
        """
        
        self.chat_nav_btn = QPushButton(" Chat")
        self.chat_nav_btn.setIcon(IconManager.get_icon("chat"))
        self.chat_nav_btn.setProperty("active", True)
        
        self.templates_nav_btn = QPushButton(" Templates")
        self.templates_nav_btn.setIcon(IconManager.get_icon("template"))
        
        self.history_nav_btn = QPushButton(" History")
        self.history_nav_btn.setIcon(IconManager.get_icon("history"))
        
        self.files_nav_btn = QPushButton(" Files")
        self.files_nav_btn.setIcon(IconManager.get_icon("file"))
        
        for btn in [self.chat_nav_btn, self.templates_nav_btn, 
                   self.history_nav_btn, self.files_nav_btn]:
            btn.setStyleSheet(nav_buttons_style)
            sidebar_layout.addWidget(btn)
            
        # Connect buttons to tab switching with smooth transitions
        self.chat_nav_btn.clicked.connect(lambda: self.switch_tab(0))
        self.templates_nav_btn.clicked.connect(lambda: self.switch_tab(1))
        self.history_nav_btn.clicked.connect(lambda: self.switch_tab(2))
        self.files_nav_btn.clicked.connect(lambda: self.switch_tab(3))
        
        sidebar_layout.addStretch()
        
        # Enhanced settings button
        self.settings_btn = QPushButton(" Settings")
        self.settings_btn.setIcon(IconManager.get_icon("settings"))
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: #bbbbbb;
                border: 1px solid #3f3f3f;
                border-radius: 8px;
                padding: 12px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #3f3f3f;
                color: white;
            }
        """)
        self.settings_btn.clicked.connect(self.open_settings)
        sidebar_layout.addWidget(self.settings_btn)
        
        # Create content area
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background-color: #1e1e1e;")
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Create tabs content
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
        self.chat_layout.setContentsMargins(5, 5, 5, 5)
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
        
        # Enhanced search in history
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
        
        # Enhanced history list with better visualization
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
            background-color: #2b2b2b;
            border: 1px solid #3f3f3f;
            border-radius: 5px;
            padding: 5px;
            }
            QListWidget::item {
            color: white;
            padding: 12px;
            border-bottom: 1px solid #3f3f3f;
            margin: 2px;
            }
            QListWidget::item:hover {
            background-color: #3f3f3f;
            }
            QListWidget::item:selected {
            background-color: #4CAF50;
            }
        """)
        
        # Load and display chat history with more details
        conversations = self.db.get_recent_conversations(self.current_session)
        for conv in conversations:
            id, timestamp, model, user_msg, ai_resp = conv
            item = QListWidgetItem()
            # Show more detailed preview
            preview = f"[{timestamp}] {model}\nUser: {user_msg[:50]}..."
            if ai_resp:
                preview += f"\nAI: {ai_resp[:50]}..."
            item.setText(preview)
            item.setData(Qt.ItemDataRole.UserRole, id)
            self.history_list.addItem(item)
            
        self.history_list.itemDoubleClicked.connect(self.load_history_item)
        history_layout.addWidget(self.history_list)
        
        # Controls for history management
        controls_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setIcon(IconManager.get_icon("refresh"))
        refresh_btn.clicked.connect(self.load_chat_history)
        
        clear_history_btn = QPushButton("Clear History")
        clear_history_btn.setIcon(IconManager.get_icon("trash"))
        clear_history_btn.clicked.connect(self.clear_history)
        
        export_history_btn = QPushButton("Export")
        export_history_btn.setIcon(IconManager.get_icon("export"))
        export_history_btn.clicked.connect(self.export_chat)
        
        controls_layout.addWidget(refresh_btn)
        controls_layout.addWidget(clear_history_btn)
        controls_layout.addWidget(export_history_btn)
        
        history_layout.addLayout(controls_layout)
        
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
        
        # Hide tabs bar buttons of navigation
        self.tabs.tabBar().hide()
        content_layout.addWidget(self.tabs)
        
        # Add progress bar to layout
        content_layout.addWidget(self.progress_bar)
        
        # Set improved initial splitter sizes
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.content_area)
        self.splitter.setSizes([250, 750])  # Slightly wider sidebar
        
        main_layout.addWidget(self.splitter)
        
    def switch_tab(self, index):
        # Update active state of navigation buttons
        for i, btn in enumerate([self.chat_nav_btn, self.templates_nav_btn, 
                               self.history_nav_btn, self.files_nav_btn]):
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        # Switch to selected tab
        self.tabs.setCurrentIndex(index)
    
    def get_sidebar_button_style(self, selected=False):
        base_style = """
            QPushButton {
                background-color: %(bg_color)s;
                color: %(text_color)s;
                border: none;
                border-radius: 5px;
                padding: 10px;
                text-align: left;
                %(extra_style)s
            }
        """
        
        if selected:
            return base_style % {
                'bg_color': '#3f3f3f',
                'text_color': 'white',
                'extra_style': 'font-weight: bold;'
            }
        else:
            return base_style % {
                'bg_color': 'transparent',
                'text_color': '#bbbbbb',
                'extra_style': '''
                }
                QPushButton:hover {
                    background-color: #3f3f3f;
                    color: white;
                }'''
            }

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
        if ok and name.strip():  # Check if name is not empty after trimming
            name = name.strip()
            if name not in self.sessions:  # Check for duplicates
                self.sessions.append(name)
                self.session_combo.addItem(name)
                self.session_combo.setCurrentText(name)
                self.current_session = name
            else:
                QMessageBox.warning(self, "Warning", "Session name already exists!")

    def change_session(self, session_name):
        if not session_name:
            return
        try:
            self.current_session = session_name
            self.load_chat_history()
            self.update_history_list()
            self.update_status(f"Switched to session: {session_name}")
        except Exception as e:
            self.update_status(f"Error changing session: {str(e)}")
            self.current_session = "Default"

    def search_chat(self):
        search_text = self.search_input.text().lower()
        
        # Reset all message highlights
        for bubble in self.message_bubbles:
            content = bubble.content.toPlainText()
            base_style = bubble.styleSheet().replace("border: 2px solid #FFEB3B;", "")
            
            if search_text and search_text in content.lower():
                bubble.setStyleSheet(base_style + " border: 2px solid #FFEB3B;")
            else:
                bubble.setStyleSheet(base_style)

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
        user_bubble = MessageBubble(is_user=True, chat_window=self)
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
        ai_bubble = MessageBubble(is_user=False, chat_window=self)
        ai_bubble.set_content(self.format_response(response), timestamp)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, ai_bubble)
        self.message_bubbles.append(ai_bubble)         

        self.db.save_conversation(self.current_model, self.current_user_message, response, self.current_session)
        
        # Update history list if we're in the history tab
        if self.tabs.currentWidget() == self.history_tab:
            self.update_history_list()
            
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
            if ai_resp is not None:
                ai_bubble.set_content(self.format_response(ai_resp), timestamp)
            else:
                ai_bubble.set_content("No response received.", timestamp)
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, ai_bubble)
            
            self.message_bubbles.extend([user_bubble, ai_bubble])
            
        # Update the history list if we're in the history tab
        if self.tabs.currentWidget() == self.history_tab:
            self.update_history_list()

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
        try:
            dialog = VoiceInputDialog(self)
            if dialog.exec():
                transcribed_text = dialog.get_text()
                if transcribed_text and transcribed_text.strip():
                    current_text = self.input_box.toPlainText().strip()
                    if current_text:
                        self.input_box.setPlainText(f"{current_text}\n{transcribed_text}")
                    else:
                        self.input_box.setPlainText(transcribed_text)
                    self.input_box.setFocus()
        except Exception as e:
            self.update_status(f"Voice input error: {str(e)}")
    
    def attach_file(self):
        """Allow the user to attach a file to the conversation"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Attach File", "", "All Files (*.*)")
            
            if file_path and os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                max_size = 10 * 1024 * 1024  # 10MB limit
                
                if file_size > max_size:
                    QMessageBox.warning(self, "File Too Large", 
                                      "File size exceeds 10MB limit.")
                    return
                    
                file_name = os.path.basename(file_path)
                current_text = self.input_box.toPlainText()
                file_text = f"\n[Attached file: {file_name}]\n"
                
                self.input_box.setPlainText(current_text + file_text if current_text else file_text)
                
                # Add file to the files list if not already present
                existing_items = [self.files_list.item(i).text() for i in range(self.files_list.count())]
                if file_name not in existing_items:
                    self.files_list.addItem(file_name)
                
                # Initialize attached_files if needed
                if not hasattr(self, 'attached_files'):
                    self.attached_files = {}
                self.attached_files[file_name] = file_path
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to attach file: {str(e)}")
    
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
    def update_history_list(self):
        """Update the history list with conversations from the current session"""
        try:
            self.history_list.clear()
            conversations = self.db.get_recent_conversations(self.current_session)
            
            for conv in conversations:
                id, timestamp, model, user_msg, ai_resp, session = conv
                item = QListWidgetItem()
                # Show more detailed preview
                preview = f"[{timestamp}] {model}\nUser: {user_msg[:50]}..."
                if ai_resp:
                    preview += f"\nAI: {ai_resp[:50]}..."
                item.setText(preview)
                item.setData(Qt.ItemDataRole.UserRole, id)
                self.history_list.addItem(item)
        except Exception as e:
            self.update_status(f"Error updating history list: {str(e)}")

    def load_history_item(self, item):
        """Load a selected history item from history into the chat"""
        try:
            conversation_id = item.data(Qt.ItemDataRole.UserRole)
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT user_message FROM conversations WHERE id = ?', (conversation_id,))
            result = cursor.fetchone()
            
            if result:
                user_message = result[0]
                self.input_box.setPlainText(user_message)
        except Exception as e:
            self.update_status(f"Error loading history item: {str(e)}")
            
    def clear_history(self):
        """Clear all conversations from history"""
        reply = QMessageBox.question(self, 'Clear History', 
                                   'Are you sure you want to clear all chat history?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.clear_history()
                self.history_list.clear()
                self.update_status("Chat history cleared successfully")
            except Exception as e:
                self.update_status(f"Error clearing history: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = ChatBotWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
