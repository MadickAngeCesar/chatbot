from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QPushButton, QScrollArea,
                           QComboBox, QLabel, QMessageBox, QStatusBar, QFileDialog,
                           QProgressBar, QSystemTrayIcon, QMenu, QLineEdit, QInputDialog,
                           QSplitter, QTabWidget, QFrame, QToolButton, QListWidget, QDialog,
                           QListWidgetItem, QSizePolicy, QCheckBox)
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
from PyQt6.QtGui import QPixmap, QPainter, QFont, QIcon
from app.templates_manager import TemplateManager
from app.tts_worker import OfflineTTSWorker
from app.tts_worker import OnlineTTSWorker  
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl
import subprocess
import platform
import shutil

class Translator:
    """
    A translator class to enable multilingual support in the chatbot application.
    Manages translations between English and French.
    """
    
    def __init__(self):
        """Initialize the translator with English and French translations."""
        self.translations = {
            'en': {
                'window_title': 'Madick Chatbot',
                'ready': 'Ready',
                'error': 'Error',
                'warning': 'Warning',
                'info': 'Information',
                'success': 'Success',
                'chat': '💬 Chat',
                'templates': '📋 Templates',
                'history': '📚 History',
                'files': '📁 Files',
                'settings': '⚙️ Settings',
                'model': 'Model:',
                'session': 'Session:',
                'clear': '🗑️ Clear',
                'export': '📤 Export',
                'start_recording': 'Start Recording',
                'stop_recording': 'Stop Recording',
                'template': 'Template:',
                'send': '📩 Send',
                'you': 'You',
                'ai': 'AI',
                'available_templates': 'Available Templates',
                'none': 'None',
                'custom': 'Custom...',
                'new_template': 'New Template',
                'template_name': 'Template Name:',
                'template_prompt': 'Enter the template prompt (use {input} for user input):',
                'template_description': 'Enter a short description:',
                'template_category': 'Select or enter a category:',
                'search_placeholder': 'Search in chat history...',
                'refresh': '🔄 Refresh',
                'clear_history': '🗑️ Clear History',
                'user': 'User',
                'uploaded_files': 'Uploaded Files',
                'upload_file': '📎 Upload File',
                'attach_file': '📎 Attach File',
                'file_attached': 'File Attached',
                'binary_file': 'Binary File',
                'file_too_large': 'File Too Large',
                'invalid_json': 'Invalid JSON',
                'binary_file_detected': 'Binary File Detected',
                'error_reading_file': 'Error Reading File',
                'voice_input': 'Voice Input',
                'recording_start_prompt': 'Press Start to begin recording...',
                'initializing_mic': 'Initializing microphone...',
                'listening': 'Listening...',
                'processing_speech': 'Processing speech...',
                'recording_stopped': 'Recording stopped',
                'recording_success': 'Recording successful!',
                'cancel': 'Cancel',
                'message_copied': 'Message copied to clipboard',
                'message_edit_ready': 'Message ready for editing',
                'tts_future': 'This feature will be implemented in a future update.',
                'response_saved_db': 'Response saved to history',
                'response_saved_file': 'Response saved to {filename}',
                'error_saving_db': 'Error saving to database: {error}',
                'error_saving_file': 'Error saving file: {error}',
                'switched_model': 'Switched to {model} model',
                'switched_session': 'Switched to session: {session}',
                'clear_chat_confirm': 'Are you sure you want to clear the chat history?',
                'clear_history_confirm': 'Are you sure you want to clear all chat history?',
                'history_cleared': 'Chat history cleared successfully',
                'error_history': 'Error clearing history: {error}',
                'minimized': 'ChatBot Minimized',
                'still_running': 'Application is still running in the system tray.',
                'voice_error': 'Voice input error: {error}',
                'new_session': 'New Session',
                'session_name': 'Enter session name:',
                'session_exists': 'Session name already exists!',
                'delete_template': 'Delete Template',
                'delete_template_confirm': 'Are you sure you want to delete the template \'{name}\'?',
                'template_deleted': 'Template \'{name}\' deleted successfully',
                'template_created': 'Template \'{name}\' created successfully',
                'error_template': 'Error {action} template: {error}',
                'content_of_file': 'Content of {filename}:',
                'send_file_confirm': 'Do you want to send the contents of {filename} to the AI?',
                'file_content_added': 'File content added to input',
                'binary_file_info': '{filename} is a binary file. Only the file reference will be added.',
                'attached_file': '[Attached file: {filename}]',
                'file_attached_status': 'File \'{filename}\' attached',
                'no_mic': 'No microphone detected',
                'speech_not_understood': 'Could not understand audio. Please speak more clearly',
                'service_error': 'Service error: {error}',
                'recording_error': 'Recording error: {error}',
                'language_changed': 'Language changed to {language}'
            },
            'fr': {
                'window_title': 'Madick Chatbot',
                'ready': 'Prêt',
                'error': 'Erreur',
                'warning': 'Avertissement',
                'info': 'Information',
                'success': 'Succès',
                'chat': '💬 Discuter',
                'templates': '📋 Modèles',
                'history': '📚 Historique',
                'files': '📁 Fichiers',
                'settings': '⚙️ Paramètres',
                'model': 'Modèle:',
                'session': 'Session:',
                'clear': '🗑️ Effacer',
                'export': '📤 Exporter',
                'start_recording': 'Commencer l\'enregistrement',
                'stop_recording': 'Arrêter l\'enregistrement',
                'template': 'Modèle:',
                'send': '📩 Envoyer',
                'you': 'Vous',
                'ai': 'IA',
                'available_templates': 'Modèles disponibles',
                'none': 'Aucun',
                'custom': 'Personnalisé...',
                'new_template': 'Nouveau modèle',
                'template_name': 'Nom du modèle:',
                'template_prompt': 'Entrez le modèle (utilisez {input} pour l\'entrée utilisateur):',
                'template_description': 'Entrez une courte description:',
                'template_category': 'Sélectionnez ou entrez une catégorie:',
                'search_placeholder': 'Rechercher dans l\'historique...',
                'refresh': '🔄 Rafraîchir',
                'clear_history': '🗑️ Effacer l\'historique',
                'user': 'Utilisateur',
                'uploaded_files': 'Fichiers téléchargés',
                'upload_file': '📎 Télécharger un fichier',
                'attach_file': '📎 Joindre un fichier',
                'file_attached': 'Fichier joint',
                'binary_file': 'Fichier binaire',
                'file_too_large': 'Fichier trop volumineux',
                'invalid_json': 'JSON invalide',
                'binary_file_detected': 'Fichier binaire détecté',
                'error_reading_file': 'Erreur de lecture du fichier',
                'voice_input': 'Entrée vocale',
                'recording_start_prompt': 'Appuyez sur Démarrer pour commencer l\'enregistrement...',
                'initializing_mic': 'Initialisation du microphone...',
                'listening': 'Écoute en cours...',
                'processing_speech': 'Traitement de la parole...',
                'recording_stopped': 'Enregistrement arrêté',
                'recording_success': 'Enregistrement réussi!',
                'cancel': 'Annuler',
                'message_copied': 'Message copié dans le presse-papiers',
                'message_edit_ready': 'Message prêt pour l\'édition',
                'tts_future': 'Cette fonctionnalité sera implémentée dans une future mise à jour.',
                'response_saved_db': 'Réponse sauvegardée dans l\'historique',
                'response_saved_file': 'Réponse sauvegardée dans {filename}',
                'error_saving_db': 'Erreur lors de la sauvegarde dans la base de données: {error}',
                'error_saving_file': 'Erreur lors de la sauvegarde du fichier: {error}',
                'switched_model': 'Passage au modèle {model}',
                'switched_session': 'Session changée: {session}',
                'clear_chat_confirm': 'Êtes-vous sûr de vouloir effacer l\'historique de discussion?',
                'clear_history_confirm': 'Êtes-vous sûr de vouloir effacer tout l\'historique de discussion?',
                'history_cleared': 'Historique de discussion effacé avec succès',
                'error_history': 'Erreur lors de l\'effacement de l\'historique: {error}',
                'minimized': 'ChatBot Minimisé',
                'still_running': 'L\'application est toujours en cours d\'exécution dans la barre d\'état système.',
                'voice_error': 'Erreur d\'entrée vocale: {error}',
                'new_session': 'Nouvelle Session',
                'session_name': 'Entrez le nom de la session:',
                'session_exists': 'Le nom de la session existe déjà!',
                'delete_template': 'Supprimer le modèle',
                'delete_template_confirm': 'Êtes-vous sûr de vouloir supprimer le modèle \'{name}\'?',
                'template_deleted': 'Modèle \'{name}\' supprimé avec succès',
                'template_created': 'Modèle \'{name}\' créé avec succès',
                'error_template': 'Erreur lors {action} du modèle: {error}',
                'content_of_file': 'Contenu du fichier {filename}:',
                'send_file_confirm': 'Voulez-vous envoyer le contenu de {filename} à l\'IA?',
                'file_content_added': 'Contenu du fichier ajouté à l\'entrée',
                'binary_file_info': '{filename} est un fichier binaire. Seule la référence au fichier sera ajoutée.',
                'attached_file': '[Fichier joint: {filename}]',
                'file_attached_status': 'Fichier \'{filename}\' joint',
                'no_mic': 'Aucun microphone détecté',
                'speech_not_understood': 'Impossible de comprendre l\'audio. Veuillez parler plus clairement',
                'service_error': 'Erreur de service: {error}',
                'recording_error': 'Erreur d\'enregistrement: {error}',
                'language_changed': 'Langue changée en {language}'
            }
        }
        
        self.current_language = 'en'
        
        # Try to load language setting from settings file
        self._load_language_from_settings()
    
    def _load_language_from_settings(self):
        """Load language setting from the settings file if it exists."""
        
        try:
            pass
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if 'language' in settings:
                        self.set_language(settings['language'])
        except Exception as e:
            # In case of any error, fallback to English
            print(f"Error loading language settings: {e}")
            self.current_language = 'en'
    
    def reload_settings(self):
        """Reload language settings from settings file."""
        self._load_language_from_settings()
    
    def set_language(self, language_code):
        """Set the current language."""
        if language_code in self.translations:
            self.current_language = language_code
            return True
        else:
            print(f"Language '{language_code}' not supported. Using English.")
            self.current_language = 'en'
            return False
    
    def get_translation(self, key, **kwargs):
        """Get a translated string for the given key with optional formatting."""
        # Get the translation dictionary for the current language
        translations = self.translations.get(self.current_language, self.translations['en'])
        
        # Get the translated text or fallback to English or the key itself
        translated = translations.get(key)
        if translated is None:
            # Try English as fallback
            translated = self.translations['en'].get(key, key)
        
        # Apply any format parameters
        if kwargs and '{' in translated:
            try:
                translated = translated.format(**kwargs)
            except KeyError:
                # If formatting fails, return the unformatted string
                pass
                
        return translated
    
    def tr(self, key, **kwargs):
        """Shorthand method for get_translation."""
        return self.get_translation(key, **kwargs)

# Create a global translator instance
translator = Translator()

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
        self.tts_thread = None  # To keep reference to active TTS thread
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
        
        # Safely get sender name with better error handling
        if self.is_user:
            sender_name = "You"
            if self.chat_window is not None and hasattr(self.chat_window, "settings"):
                try:
                    sender_name = self.chat_window.settings.get("user_name", "You")
                except (AttributeError, TypeError):
                    pass
        else:
            sender_name = "AI"
        
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
            edit_btn = self._create_action_button("✏️", "Edit message", self._handle_edit)
            buttons.append(edit_btn)
            
        copy_btn = self._create_action_button("📋", "Copy to clipboard", self._handle_copy)
        buttons.append(copy_btn)
        
        if not self.is_user:
            speak_btn = self._create_action_button("🔊", "Read aloud", self._handle_speak)
            save_btn = self._create_action_button("🔖", "Save response", self._handle_save)
            buttons.extend([speak_btn, save_btn])
        
        for btn in buttons:
            actions_layout.addWidget(btn)
            
        actions_layout.addStretch()
        self.layout.addLayout(actions_layout)
        
    def _create_action_button(self, emoji, tooltip, callback):
        """Create an action button with emoji instead of icon."""
        btn = QToolButton()
        btn.setText(emoji)
        btn.setToolTip(tooltip)
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
        """Handle text-to-speech functionality with offline model support."""
        if not self.chat_window or self.is_user:
            return
            
        try:
            # Cancel any existing TTS operation
            if self.tts_thread is not None and self.tts_thread.isRunning():
                if hasattr(self, 'tts_worker') and hasattr(self.tts_worker, 'cancel'):
                    self.tts_worker.cancel()
                self.tts_thread.quit()
                self.tts_thread.wait(3000)  # Wait up to 3 seconds for thread to finish
                
            # Get the text content to speak
            text_to_speak = self.content.toPlainText()
            if not text_to_speak:
                return
                
            # Load speech settings
            settings = self.chat_window.settings
            use_offline_tts = settings.get('use_offline_voice', False)
            offline_tts_model = settings.get('offline_tts_model', '')
            voice_name = settings.get('tts_voice', 'en-US-Neural2-F')
            speech_rate = float(settings.get('speech_rate', 1.0))
            
            # Create status message with spinner
            status_msg = QMessageBox(self.chat_window)
            status_msg.setWindowTitle("Text-to-Speech")
            status_msg.setText("Generating speech...\nPlease wait.")
            status_msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
            
            # Show the dialog but don't block
            status_msg.show()
            QApplication.processEvents()
            
            # Create a worker thread for TTS processing
            self.tts_thread = QThread()
            
            if use_offline_tts and offline_tts_model and os.path.exists(offline_tts_model):
                # Use offline TTS model
                self.tts_worker = OfflineTTSWorker(text_to_speak, offline_tts_model, speech_rate)
            else:
                # Use online TTS service (gTTS as fallback)
                self.tts_worker = OnlineTTSWorker(text_to_speak, voice_name, speech_rate)
                
            self.tts_worker.moveToThread(self.tts_thread)
            
            # Connect signals
            self.tts_thread.started.connect(self.tts_worker.generate_speech)
            self.tts_worker.finished.connect(self.tts_thread.quit)
            self.tts_worker.finished.connect(self.tts_worker.deleteLater)
            self.tts_thread.finished.connect(self._on_tts_thread_finished)
            self.tts_worker.error.connect(lambda e: self.chat_window.update_status(f"TTS error: {e}"))
            self.tts_worker.progress.connect(lambda p: self.chat_window.update_status(f"TTS progress: {p}%"))
            
            # Handle completion
            self.tts_worker.speech_ready.connect(lambda audio_path: self._play_audio(audio_path, status_msg))
            
            # Start the thread
            self.tts_thread.start()
        except Exception as e:
            self.chat_window.update_status(f"TTS error: {str(e)}")
            QMessageBox.warning(
                self.chat_window,
                "TTS Error", 
                f"Error initializing text-to-speech: {str(e)}\n\nPlease check the settings."
            )
    
    def _play_audio(self, audio_path, status_msg=None):
        """Play the generated audio."""
        try:
            # First verify audio file exists and is readable
            if not audio_path or not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
                
            if os.path.getsize(audio_path) == 0:
                raise ValueError("Audio file is empty")
                
            if status_msg:
                status_msg.accept()
                
            # Create audio player dialog
            player_dialog = QDialog(self.chat_window)
            player_dialog.setWindowTitle("Audio Player")
            player_dialog.setMinimumWidth(400)
            
            # Layout
            layout = QVBoxLayout(player_dialog)
            
            # File info
            file_info = QLabel(f"File: {os.path.basename(audio_path)}")
            layout.addWidget(file_info)
            
            # Try to use PyQt6's QMediaPlayer if available
            try:
                # Create media player with hardware acceleration support
                audio_output = QAudioOutput()
                player = QMediaPlayer()
                player.setAudioOutput(audio_output)
                
                # Log FFmpeg initialization if needed
                self.chat_window.update_status("Initializing audio playback with FFmpeg support")
                
                # Set media source with absolute path
                abs_path = os.path.abspath(audio_path)
                self.chat_window.update_status(f"Loading audio file: {abs_path}")
                
                url = QUrl.fromLocalFile(abs_path)
                player.setSource(url)
                
                # Add player status info
                status_label = QLabel("Ready to play")
                layout.addWidget(status_label)
                
                # Connect player signals
                player.errorOccurred.connect(lambda error, errorString: 
                    status_label.setText(f"Player error: {errorString}"))
                
                player.playbackStateChanged.connect(lambda state: 
                    status_label.setText("Playing" if state == QMediaPlayer.PlaybackState.PlayingState 
                                        else "Paused" if state == QMediaPlayer.PlaybackState.PausedState 
                                        else "Stopped"))
                
                # Controls
                controls = QHBoxLayout()
                play_btn = QPushButton("▶️ Play")
                pause_btn = QPushButton("⏸️ Pause")
                stop_btn = QPushButton("⏹️ Stop")
                
                # Connect buttons
                play_btn.clicked.connect(player.play)
                pause_btn.clicked.connect(player.pause)
                stop_btn.clicked.connect(player.stop)
                
                controls.addWidget(play_btn)
                controls.addWidget(pause_btn)
                controls.addWidget(stop_btn)
                
                # Export button
                export_btn = QPushButton("💾 Save Audio")
                export_btn.clicked.connect(lambda: self._export_audio(audio_path))
                controls.addWidget(export_btn)
                
                layout.addLayout(controls)
                
                # Show media player info
                media_info = QLabel("Media Player Ready")
                layout.addWidget(media_info)
                
                # Check for media errors before playing
                if player.mediaStatus() == QMediaPlayer.MediaStatus.InvalidMedia:
                    media_info.setText(f"Error: Invalid media format - {os.path.basename(audio_path)}")
                    self.chat_window.update_status(f"Invalid media format: {os.path.basename(audio_path)}")
                else:
                    # Auto-play with error handling
                    player.play()
                    self.chat_window.update_status(f"Playing audio file: {os.path.basename(audio_path)}")
                
            except Exception as e:
                # Log the exception
                self.chat_window.update_status(f"Media player error: {str(e)}")
                
                # Fallback to system default player
                info_label = QLabel(f"Using system audio player (exception: {str(e)})")
                layout.addWidget(info_label)
                
                # Try to play with system default
                system = platform.system()
                try:
                    if system == "Windows":
                        subprocess.Popen(["start", "", audio_path], shell=True)
                    elif system == "Darwin":  # macOS
                        subprocess.Popen(["open", audio_path])
                    else:  # Linux and others
                        subprocess.Popen(["xdg-open", audio_path])
                except Exception as e:
                    error_label = QLabel(f"Error playing audio: {str(e)}")
                    layout.addWidget(error_label)
                
                # Export button
                export_btn = QPushButton("💾 Save Audio")
                export_btn.clicked.connect(lambda: self._export_audio(audio_path))
                layout.addWidget(export_btn)
            
            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(player_dialog.accept)
            layout.addWidget(close_btn)
            
            player_dialog.exec()
            
        except Exception as e:
            self.chat_window.update_status(f"Error playing audio: {str(e)}")
        
    def _export_audio(self, audio_path):
        """Export the generated audio file."""
        if not audio_path or not os.path.exists(audio_path):
            return
            
        try:
            # Get file save location from user
            save_path, _ = QFileDialog.getSaveFileName(
                self.chat_window,
                "Save Audio File",
                os.path.basename(audio_path),
                "Audio Files (*.mp3 *.wav);;All Files (*.*)"
            )
            
            if save_path:
                shutil.copy2(audio_path, save_path)
                self.chat_window.update_status(f"Audio saved to {save_path}")
        except Exception as e:
            self.chat_window.update_status(f"Error exporting audio: {str(e)}")
            
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
                
                with open(filename, 'w', encoding='utf-8') as f:
                    if filename.endswith(".html"):
                        f.write(self.content.toHtml())
                    else:
                        f.write(text)

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
        
    def _on_tts_thread_finished(self):
        """Handle cleanup when TTS thread finishes."""
        if hasattr(self, 'tts_worker'):
            del self.tts_worker
            
    def closeEvent(self, event):
        """Properly clean up threads before the widget is closed."""
        self._cleanup_threads()
        super().closeEvent(event)
        
    def _cleanup_threads(self):
        """Ensure all threads are properly terminated before object destruction."""
        if self.tts_thread is not None and self.tts_thread.isRunning():
            if hasattr(self, 'tts_worker') and hasattr(self.tts_worker, 'cancel'):
                self.tts_worker.cancel()
                self.tts_thread.quit()
                self.tts_thread.wait(1000)  # Wait up to 1 second for thread to finish

class VoiceWorker(QObject):
    """Worker class for voice recording and speech recognition"""
    result = pyqtSignal(str)
    partial_result = pyqtSignal(str)
    status = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal()
    audio_level = pyqtSignal(float)
    
    def __init__(self, recognizer, language="en-US", offline_mode=False, offline_model=None):
        super().__init__()
        self.recognizer = recognizer
        self.language = language
        self.is_running = True
        self.offline_mode = offline_mode
        self.offline_model = offline_model
    
    def record(self):
        """Record audio and perform speech recognition"""
        try:
            with sr.Microphone() as source:
                self.status.emit(translator.tr('initializing_mic'))
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.status.emit(translator.tr('listening'))
                
                # Begin listening loop
                while self.is_running:
                    try:
                        # Emit audio level for visualization
                        energy = self.recognizer.energy_threshold
                        normalized_energy = min(1.0, energy / 4000)
                        self.audio_level.emit(normalized_energy)
                        
                        # Record audio with timeout
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        
                        if not self.is_running:
                            break
                            
                        self.status.emit(translator.tr('processing_speech'))
                        
                        if self.offline_mode and self.offline_model:
                            # Placeholder for offline recognition
                            # In a real implementation, you would use whisper or another offline model
                            text = "Offline recognition not fully implemented"
                        else:
                            # Use Google's service for online recognition
                            text = self.recognizer.recognize_google(audio, language=self.language)
                            
                        self.result.emit(text)
                        self.finished.emit()
                        break
                        
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        self.error.emit(translator.tr('speech_not_understood'))
                        break
                    except sr.RequestError as e:
                        self.error.emit(translator.tr('service_error', error=str(e)))
                        break
                        
        except Exception as e:
            self.error.emit(translator.tr('recording_error', error=str(e)))
        finally:
            self.finished.emit()
            
    def stop(self):
        """Stop the recording process"""
        self.is_running = False

class ModelDownloadWorker(QObject):
    """Worker class for downloading voice models"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(str, str)  # model_type, model_path
    error = pyqtSignal(str)
    
    def __init__(self, model_type, model_name, output_dir):
        super().__init__()
        self.model_type = model_type
        self.model_name = model_name
        self.output_dir = output_dir
        self.is_running = False
        
    def download(self):
        """Download the model with progress updates"""
        try:
            self.is_running = True
            
            # Create the output file path
            model_filename = f"{self.model_name.replace(':', '_')}.bin"
            output_path = os.path.join(self.output_dir, model_filename)
            
            # Mock download process with progress updates
            # In a real implementation, you would use requests or another library
            for i in range(0, 101, 5):
                if not self.is_running:
                    return
                self.progress.emit(i)
                # Simulate download time
                QThread.msleep(200)
            
            # Create empty file to simulate download completion
            with open(output_path, 'wb') as f:
                f.write(b'MOCK_MODEL_DATA')
            
            self.finished.emit(self.model_type, output_path)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.is_running = False
    
    def stop(self):
        """Stop the download process"""
        self.is_running = False

class VoiceInputDialog(QDialog):
    recording_finished = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.recognizer = sr.Recognizer()
        self.text = ""
        self.is_recording = False
        self.settings = {}
        # Initialize default language
        self.language = "en-UK"
        self.load_settings()
        self.setup_offline_models()
        self.setup_ui()
        self.setup_signals()

    def load_settings(self):
        """Load voice settings from the settings file"""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
        except Exception as e:
            print(f"Error loading voice settings: {e}")
            self.settings = {}

    def setup_offline_models(self):
        """Setup offline models if available"""
        self.offline_mode = self.settings.get('use_offline_voice', False)
        self.offline_stt_model = self.settings.get('offline_stt_model', '')
        self.offline_tts_model = self.settings.get('offline_tts_model', '')
        
        # Check if models exist
        self.stt_model_available = os.path.exists(self.offline_stt_model) if self.offline_stt_model else False
        self.tts_model_available = os.path.exists(self.offline_tts_model) if self.offline_tts_model else False

    def setup_ui(self):
        """Initialize and setup UI components"""
        self.setWindowTitle("Voice Input")
        self.setMinimumWidth(500)
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
            QComboBox {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
                min-width: 150px;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Status label with icon
        status_layout = QHBoxLayout()
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(24, 24)
        self.status_label = QLabel(translator.tr('recording_start_prompt'))
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_label, stretch=1)
        self.layout.addLayout(status_layout)
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_label = QLabel("Language:")
        lang_label.setStyleSheet("font-weight: bold;")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "French", "Spanish", "German", "Italian", "Japanese", "Chinese"])
        
        # Set default language based on app language
        default_lang = "English" if translator.current_language == 'en' else "French"
        self.lang_combo.setCurrentText(default_lang)
        
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo, stretch=1)
        self.layout.addLayout(lang_layout)
        
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
        
        # Transcription preview
        self.result_preview = QTextEdit()
        self.result_preview.setPlaceholderText("Transcription will appear here...")
        self.result_preview.setReadOnly(True)
        self.result_preview.setMaximumHeight(100)
        self.result_preview.setStyleSheet("""
            QTextEdit {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.layout.addWidget(self.result_preview)
        
        # Offline mode toggle
        self.offline_mode_layout = QHBoxLayout()
        self.offline_checkbox = QCheckBox("Use offline models")
        self.offline_checkbox.setStyleSheet("color: white;")
        self.offline_checkbox.setChecked(self.settings.get('use_offline_voice', False))
        self.offline_checkbox.toggled.connect(self.toggle_offline_mode)
        
        self.download_btn = QPushButton("Download Models")
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.download_btn.clicked.connect(self.download_models)
        
        self.offline_mode_layout.addWidget(self.offline_checkbox)
        self.offline_mode_layout.addWidget(self.download_btn)
        self.layout.addLayout(self.offline_mode_layout)
        
        # Status indicator for offline models
        self.offline_status = QLabel()
        self.update_offline_status()
        self.layout.addWidget(self.offline_status)
        
        # Buttons with icons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Recording")
        self.start_button.setIcon(IconManager.get_icon("microphone"))
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setIcon(IconManager.get_icon("cancel"))
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)
        
        # Update UI based on current settings
        self.toggle_offline_mode(self.offline_checkbox.isChecked())

    def update_offline_status(self):
        """Update offline model status indicators"""
        if self.offline_checkbox.isChecked():
            stt_status = "✅ Installed" if self.stt_model_available else "❌ Not installed"
            tts_status = "✅ Installed" if self.tts_model_available else "❌ Not installed"
            self.offline_status.setText(f"STT Model: {stt_status} | TTS Model: {tts_status}")
            self.offline_status.setStyleSheet("color: #4CAF50;" if 
                                             (self.stt_model_available and self.tts_model_available) 
                                             else "color: #F44336;")
        else:
            self.offline_status.setText("Offline mode disabled (using online services)")
            self.offline_status.setStyleSheet("color: #BBBBBB;")

    def toggle_offline_mode(self, enabled):
        """Toggle between online and offline voice recognition"""
        self.offline_mode = enabled
        self.update_offline_status()
        
        # Update settings
        self.settings['use_offline_voice'] = enabled
        self.save_settings()

    def save_settings(self):
        """Save voice settings to the settings file"""
        try:
            # Load current settings first to avoid overwriting other settings
            current_settings = {}
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    current_settings = json.load(f)
                    
            # Update with voice settings
            current_settings.update({
                'use_offline_voice': self.offline_mode,
                'offline_stt_model': self.offline_stt_model,
                'offline_tts_model': self.offline_tts_model
            })
            
            # Save back to file
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(current_settings, f, indent=2)
        except Exception as e:
            print(f"Error saving voice settings: {e}")

    def download_models(self):
        """Open dialog to download offline voice models"""
        self.download_dialog = QDialog(self)
        self.download_dialog.setWindowTitle("Download Voice Models")
        self.download_dialog.setMinimumWidth(500)
        self.download_dialog.setStyleSheet(self.styleSheet())
        
        layout = QVBoxLayout(self.download_dialog)
        
        # STT model selection
        stt_layout = QHBoxLayout()
        stt_label = QLabel("Speech-to-Text Model:")
        self.stt_combo = QComboBox()
        self.stt_combo.addItems(["tiny-whisper", "whisper-small", "whisper-medium", "whisper-large"])
        stt_download_btn = QPushButton("Download")
        stt_download_btn.clicked.connect(lambda: self.start_model_download('stt'))
        
        stt_layout.addWidget(stt_label)
        stt_layout.addWidget(self.stt_combo, stretch=1)
        stt_layout.addWidget(stt_download_btn)
        layout.addLayout(stt_layout)
        
        # TTS model selection
        tts_layout = QHBoxLayout()
        tts_label = QLabel("Text-to-Speech Model:")
        self.tts_combo = QComboBox()
        self.tts_combo.addItems(["piper-tiny", "piper-small", "piper-medium"])
        tts_download_btn = QPushButton("Download")
        tts_download_btn.clicked.connect(lambda: self.start_model_download('tts'))
        
        tts_layout.addWidget(tts_label)
        tts_layout.addWidget(self.tts_combo, stretch=1)
        tts_layout.addWidget(tts_download_btn)
        layout.addLayout(tts_layout)
        
        # Download progress section
        self.download_status = QLabel("Select a model to download")
        layout.addWidget(self.download_status)
        
        self.download_progress = QProgressBar()
        self.download_progress.setVisible(False)
        layout.addWidget(self.download_progress)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.download_dialog.accept)
        layout.addWidget(close_btn)
        
        self.download_dialog.exec()
        
    def update_download_progress(self, progress):
        """Update the download progress bar"""
        self.download_progress.setValue(progress)
        
    def get_text(self):
        """Return the transcribed text"""
        return self.text
        
    def start_model_download(self, model_type):
        """Start downloading the selected voice model"""
        model_name = self.stt_combo.currentText() if model_type == 'stt' else self.tts_combo.currentText()
        self.download_status.setText(f"Downloading {model_name}...")
        self.download_progress.setVisible(True)
        
        # Create directory if it doesn't exist
        models_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../models')
        os.makedirs(models_dir, exist_ok=True)
        
        # Mock download functionality
        # In a real implementation, you would use requests, urllib, or another library to download the model
        self.download_thread = QThread()
        self.download_worker = ModelDownloadWorker(model_type, model_name, models_dir)
        self.download_worker.moveToThread(self.download_thread)
        
        self.download_thread.started.connect(self.download_worker.download)
        self.download_worker.progress.connect(self.update_download_progress)
        self.download_worker.finished.connect(self.download_finished)
        self.download_worker.error.connect(self.download_error)
        
        self.download_thread.start()
        
        self.download_dialog.exec()

    def start_model_download(self, model_type):
        """Start downloading the selected voice model"""
        model_name = self.stt_combo.currentText() if model_type == 'stt' else self.tts_combo.currentText()
        self.download_status.setText(f"Downloading {model_name}...")
        self.download_progress.setVisible(True)
        
        # Create directory if it doesn't exist
        models_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../models')
        os.makedirs(models_dir, exist_ok=True)
        
        # Mock download functionality
        # In a real implementation, you would use requests, urllib, or another library to download the model
        self.download_thread = QThread()
        self.download_worker = ModelDownloadWorker(model_type, model_name, models_dir)
        self.download_worker.moveToThread(self.download_thread)
        
        self.download_thread.started.connect(self.download_worker.download)
        self.download_worker.progress.connect(self.update_download_progress)
        self.download_worker.finished.connect(self.download_finished)
        self.download_worker.error.connect(self.download_error)
        
        self.download_thread.start()

    def update_download_progress(self, progress):
        """Update the download progress bar"""
        self.download_progress.setValue(progress)

    def download_finished(self, model_type, model_path):
        """Handle completed download"""
        if model_type == 'stt':
            self.offline_stt_model = model_path
            self.stt_model_available = True
        else:
            self.offline_tts_model = model_path
            self.tts_model_available = True
            
        # Update settings
        self.settings[f'offline_{model_type}_model'] = model_path
        self.save_settings()
        
        self.download_status.setText(f"Download complete: {os.path.basename(model_path)}")
        self.download_progress.setVisible(False)
        self.update_offline_status()

    def download_error(self, error_msg):
        """Handle download errors"""
        self.download_status.setText(f"Error: {error_msg}")
        self.download_progress.setVisible(False)

    def setup_signals(self):
        """Setup signal connections"""
        self.start_button.clicked.connect(self.toggle_recording)
        self.cancel_button.clicked.connect(self.reject)
        self.recording_finished.connect(self.on_recording_finished)
        self.status_update.connect(self.update_status)
        self.lang_combo.currentTextChanged.connect(self.update_language)

    def update_language(self, language):
        """Update the speech recognition language"""
        language_codes = {
            "English": "en-US",
            "French": "fr-FR",
            "Spanish": "es-ES",
            "German": "de-DE",
            "Italian": "it-IT",
            "Japanese": "ja-JP",
            "Chinese": "zh-CN"
        }
        self.language = language_codes.get(language, "en-US")
        if hasattr(self, 'worker'):
            self.worker.language = self.language

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
                raise OSError(translator.tr('no_mic'))
            
            self.is_recording = True
            self.progress_bar.setVisible(True)
            self.level_bar.setVisible(True)
            self.start_button.setText(translator.tr('stop_recording'))
            self.update_status(translator.tr('initializing_mic'), "recording")
            
            # Create and setup worker thread
            self.worker_thread = QThread()
            self.worker = VoiceWorker(
                self.recognizer, 
                language=self.language,
                offline_mode=self.offline_mode,
                offline_model=self.offline_stt_model if self.stt_model_available else None
            )
            self.worker.moveToThread(self.worker_thread)
            
            # Connect all signals
            self.worker_thread.started.connect(self.worker.record)
            self.worker.finished.connect(self.worker_thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker_thread.finished.connect(self.worker_thread.deleteLater)
            self.worker.error.connect(self.handle_error)
            self.worker.result.connect(self.handle_result)
            self.worker.partial_result.connect(self.update_preview)
            self.worker.status.connect(lambda s: self.update_status(s, "info"))
            self.worker.audio_level.connect(self.update_audio_level)
            
            self.worker_thread.start()
            
        except Exception as e:
            self.handle_error(str(e))

    def update_preview(self, text):
        """Update the live transcription preview"""
        self.result_preview.setText(text)
        # Auto-scroll to bottom
        self.result_preview.verticalScrollBar().setValue(
            self.result_preview.verticalScrollBar().maximum()
        )

    def stop_recording(self):
        """Stop current recording"""
        if hasattr(self, 'worker'):
            self.worker.stop()
            self.is_recording = False
            self.start_button.setText(translator.tr('start_recording'))
            self.update_status(translator.tr('recording_stopped'), "info")

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
        self.start_button.setText(translator.tr('start_recording'))
        self.update_status(error_msg, "error")
        
    def handle_result(self, text):
        """Handle the final speech recognition result"""
        self.text = text
        self.update_preview(text)
        self.update_status(translator.tr('recording_success'), "success")
        self.is_recording = False
        self.progress_bar.setVisible(False)
        self.level_bar.setVisible(False)
        self.start_button.setText(translator.tr('start_recording'))
        self.recording_finished.emit(text)
        self.accept()
        
    def on_recording_finished(self, text):
        """Handle when recording is finished"""
        self.text = text

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
        
        # Setup emoji as window icon
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        font = QFont('Segoe UI Emoji', 40)  # Font that supports emoji
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "🤖")  # Robot emoji for chatbot
        painter.end()
        self.setWindowIcon(QIcon(pixmap))
        
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
        
        self.chat_nav_btn = QPushButton(" 💬 Chat")
        self.chat_nav_btn.setProperty("active", True)
        
        self.templates_nav_btn = QPushButton(" 📋 Templates")
        
        self.history_nav_btn = QPushButton(" 📚 History")
        
        self.files_nav_btn = QPushButton(" 📁 Files")
        
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
        self.settings_btn = QPushButton(" ⚙️ Settings")
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
        
        # Get all available models including custom ones from settings
        all_models = self.models.copy()
        if 'custom_models' in self.settings:
            for model_name in self.settings['custom_models']:
                if model_name not in all_models:
                    all_models.append(model_name)
        
        self.model_combo.addItems(all_models)
        self.model_combo.setCurrentText(self.current_model)
        self.model_combo.setStyleSheet(self.get_combo_style())
        self.model_combo.currentTextChanged.connect(self.change_model)
        
        # Setup model management buttons
        info_btn = QToolButton()
        info_btn.setText("ℹ️")
        info_btn.setToolTip("Model Information")
        info_btn.clicked.connect(lambda: self.show_model_info(self.model_combo.currentText()))
        
        # Add custom model button
        add_model_btn = QToolButton()
        add_model_btn.setText("➕")
        add_model_btn.setToolTip("Add Custom Model")
        add_model_btn.clicked.connect(self.add_custom_model)
        
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        model_layout.addWidget(info_btn)
        model_layout.addWidget(add_model_btn)
        model_layout.addStretch()
        
        # Session selection
        session_label = QLabel("Session:")
        session_label.setStyleSheet("color: white;")
        self.session_combo = QComboBox()
        self.session_combo.addItems(self.sessions)
        self.session_combo.setStyleSheet(self.get_combo_style())
        self.session_combo.currentTextChanged.connect(self.change_session)
        
        new_session_btn = QToolButton()
        new_session_btn.setText("➕")
        new_session_btn.setToolTip("New Session")
        new_session_btn.clicked.connect(self.create_new_session)
        
        model_layout.addWidget(session_label)
        model_layout.addWidget(self.session_combo)
        model_layout.addWidget(new_session_btn)
        
        # Add buttons to model layout
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setStyleSheet(self.get_button_style("#d32f2f"))
        clear_btn.clicked.connect(self.clear_chat)
        model_layout.addWidget(clear_btn)
        
        export_btn = QPushButton("📤 Export")
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
        file_btn.setText("📎")
        file_btn.setToolTip("Attach File")
        file_btn.clicked.connect(self.attach_file)
        
        voice_btn = QToolButton()
        voice_btn.setText("🎤")
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
        
        self.send_button = QPushButton("📩 Send")
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
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_chat_history)
        
        clear_history_btn = QPushButton("🗑️ Clear History")
        clear_history_btn.clicked.connect(self.clear_history)
        
        export_history_btn = QPushButton("📤 Export")
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
        
        upload_btn = QPushButton("📎 Upload File")
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
        """Load templates from the template manager and update the UI list."""
        self.template_manager = TemplateManager()
        templates = self.template_manager.get_all_templates()
        
        self.templates_list.clear()
        
        # Add templates to UI with categories
        categories = self.template_manager.get_template_categories()
        for category in categories:
            # Get templates for this category
            category_templates = self.template_manager.get_templates_by_category(category)
            
            for name, template_data in category_templates.items():
                item = QListWidgetItem(f"{name} - {template_data['description']}")
                item.setData(Qt.ItemDataRole.UserRole, name)
                self.templates_list.addItem(item)
        
        # Update the combo box with template names
        self.template_combo.clear()
        self.template_combo.addItem("None")
        for name in templates.keys():
            self.template_combo.addItem(name)
        self.template_combo.addItem("Custom...")
        
        # Connect double-click event for templates
        self.templates_list.itemDoubleClicked.connect(self.apply_template_from_list)
        
        # Setup context menu for templates list
        self.templates_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.templates_list.customContextMenuRequested.connect(self.show_template_context_menu)

    def show_template_context_menu(self, position):
        """Show context menu for template list item."""
        item = self.templates_list.itemAt(position)
        if not item:
            return
            
        template_name = item.data(Qt.ItemDataRole.UserRole)
        
        # Create context menu
        menu = QMenu()
        apply_action = menu.addAction("Apply Template")
        menu.addSeparator()
        delete_action = menu.addAction("Delete Template")
        
        # Show menu and get selected action
        action = menu.exec(self.templates_list.mapToGlobal(position))
        
        if action == apply_action:
            self.apply_template_from_list(item)
        elif action == delete_action:
            self.delete_template(template_name)

    def delete_template(self, template_name):
        """Delete the selected template after confirmation."""
        reply = QMessageBox.question(
            self, 
            "Delete Template", 
            f"Are you sure you want to delete the template '{template_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.template_manager.delete_template(template_name)
                self.load_templates()  # Reload templates
                self.update_status(f"Template '{template_name}' deleted successfully")
                
                # If the deleted template is currently selected, reset to "None"
                if self.template_combo.currentText() == template_name:
                    self.template_combo.setCurrentText("None")
            except Exception as e:
                self.update_status(f"Error deleting template: {str(e)}")

    def apply_template_from_list(self, item):
        """Apply template when double-clicked from template list."""
        template_name = item.data(Qt.ItemDataRole.UserRole)
        self.template_combo.setCurrentText(template_name)
        self.apply_template(template_name)
        # Switch to chat tab
        self.switch_tab(0)

    def apply_template(self, template_name):
        """Apply the selected template to the input box."""
        if template_name == "None":
            return
            
        if template_name == "Custom...":
            self.create_custom_template()
            return
            
        # Get template from template manager
        template = self.template_manager.get_template(template_name)
        if template:
            # Replace {input} with cursor position marker
            template = template.replace("{input}", "")
            self.input_box.setPlainText(template)
            self.input_box.setFocus()
            
            # Move cursor to position of first parameter
            cursor = self.input_box.textCursor()
            position = self.input_box.toPlainText().find("{")
            if position >= 0:
                cursor.setPosition(position)
                self.input_box.setTextCursor(cursor)

    def create_custom_template(self):
        """Create a new custom template."""
        name, ok = QInputDialog.getText(self, "New Template", "Template Name:")
        if not ok or not name:
            return
            
        # Get prompt content
        prompt, ok = QInputDialog.getMultiLineText(
            self, 
            "Template Prompt", 
            "Enter the template prompt (use {input} for user input):"
        )
        if not ok or not prompt:
            return
            
        # Get description
        description, ok = QInputDialog.getText(
            self, 
            "Template Description", 
            "Enter a short description:"
        )
        if not ok:
            description = ""
            
        # Get category
        categories = self.template_manager.get_template_categories()
        category, ok = QInputDialog.getItem(
            self,
            "Template Category",
            "Select or enter a category:",
            categories,
            0,
            True
        )
        if not ok:
            category = "custom"
            
        # Save template
        try:
            self.template_manager.add_template(name, prompt, description, category)
            self.load_templates()  # Reload templates
            self.update_status(f"Template '{name}' created successfully")
            
            # Set as current template
            self.template_combo.setCurrentText(name)
            self.apply_template(name)
        except Exception as e:
            self.update_status(f"Error creating template: {str(e)}")

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
        """Change the active model and update the LLM instance"""
        if not model_name or model_name == self.current_model:
            return
            
        try:
            # Update current model and create new LLM instance
            self.current_model = model_name
            
            # Check if API URL is specified in settings
            api_base = self.settings.get('api_url', 'http://localhost:11434')
            temperature = float(self.settings.get('temperature', 70)) / 100.0  # Convert from 0-100 to 0-1
            
            # Create LLM with settings
            self.llm = OllamaLLM(
                model=model_name,
                base_url=api_base,
                temperature=temperature
            )
            
            # Add system message bubble
            system_bubble = MessageBubble(is_user=False, chat_window=self)
            system_bubble.setStyleSheet("""
                QFrame {
                    background-color: #ff9800;
                    border-radius: 10px;
                    margin-left: 10px;
                    margin-right: 80px;
                    padding: 10px;
                }
            """)
            
            # Use translator for the message
            msg = translator.tr('switched_model', model=model_name)
            system_bubble.set_content(msg)
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, system_bubble)
            self.message_bubbles.append(system_bubble)
            
            # Scroll to the new message
            self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().maximum()
            )
            
            # Update status bar with translated message
            self.update_status(msg)
            
        except Exception as e:
            self.update_status(f"Error changing model: {str(e)}")
            # Revert to previous model in combo box
            self.model_combo.setCurrentText(self.current_model)

    def add_custom_model(self):
        """Allow users to add custom models to the chatbot"""
        model_name, ok = QInputDialog.getText(self, "Add Custom Model", "Model name (as used by Ollama):")
        
        if not ok or not model_name:
            return
            
        if model_name in self.models:
            QMessageBox.warning(self, "Duplicate Model", f"Model '{model_name}' already exists.")
            return
            
        # Get optional model description
        model_description, ok = QInputDialog.getMultiLineText(
            self, 
            "Model Description", 
            "Enter a description for this model (optional):"
        )
        
        # Add model to the list
        self.models.append(model_name)
        
        # Update model combobox
        self.model_combo.addItem(model_name)
        
        # Save custom model in settings
        if 'custom_models' not in self.settings:
            self.settings['custom_models'] = {}
        
        self.settings['custom_models'][model_name] = {
            'description': model_description,
            'added_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.save_settings()
        self.update_status(f"Added custom model: {model_name}")

    def show_model_info(self, model_name=None):
        """Display information about the selected model"""
        if not model_name:
            model_name = self.current_model
        
        # Create dialog for model details
        dialog = QDialog(self)
        dialog.setWindowTitle("Model Information")
        dialog.setMinimumSize(500, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Model name header
        model_header = QLabel(f"<h2>{model_name}</h2>")
        model_header.setStyleSheet("color: #4CAF50;")
        layout.addWidget(model_header)
        
        # Model description
        description = "No description available."
        added_date = ""
        
        # Check if it's a custom model with saved information
        if 'custom_models' in self.settings and model_name in self.settings['custom_models']:
            model_data = self.settings['custom_models'][model_name]
            if model_data.get('description'):
                description = model_data['description']
            if model_data.get('added_date'):
                added_date = f"Added on: {model_data['added_date']}"
        
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        if added_date:
            date_label = QLabel(added_date)
            date_label.setStyleSheet("color: #888888;")
            layout.addWidget(date_label)
        
        # Get model parameters from Ollama if available
        try:
            # This is a placeholder - in reality you would query Ollama API for model details
            # For now we'll just show basic information
            info_text = QTextEdit()
            info_text.setReadOnly(True)
            
            info_html = f"""
            <h3>Model Information</h3>
            <p><b>Name:</b> {model_name}</p>
            <p><b>Provider:</b> Ollama</p>
            <p><b>Status:</b> Available</p>
            <p>Use the Ollama command line for more details:</p>
            <pre>ollama show {model_name}</pre>
            """
            
            info_text.setHtml(info_html)
            layout.addWidget(info_text)
        except Exception as e:
            error_label = QLabel(f"Error retrieving model details: {str(e)}")
            error_label.setStyleSheet("color: #d32f2f;")
            layout.addWidget(error_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Set as default button
        set_default_btn = QPushButton("Set as Default")
        set_default_btn.clicked.connect(lambda: self.set_default_model(model_name, dialog))
        
        # Remove model button (only for custom models)
        remove_btn = QPushButton("Remove Model")
        if 'custom_models' in self.settings and model_name in self.settings['custom_models']:
            remove_btn.clicked.connect(lambda: self.remove_custom_model(model_name, dialog))
        else:
            remove_btn.setEnabled(False)
            remove_btn.setToolTip("Cannot remove built-in models")
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        
        button_layout.addWidget(set_default_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        dialog.exec()

    def set_default_model(self, model_name, dialog=None):
        """Set the specified model as the default"""
        self.settings['default_model'] = model_name
        self.save_settings()
        self.update_status(f"Set {model_name} as the default model")
        if dialog:
            dialog.accept()

    def remove_custom_model(self, model_name, dialog=None):
        """Remove a custom model from the list"""
        if model_name not in self.models:
            return
            
        # Don't remove if it's the current model
        if model_name == self.current_model:
            QMessageBox.warning(self, "Cannot Remove", 
                           "Cannot remove the currently selected model. Switch to another model first.")
            return
        
        reply = QMessageBox.question(
            self, "Remove Model",
            f"Are you sure you want to remove the model '{model_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove from models list
            self.models.remove(model_name)
            
            # Remove from combobox
            index = self.model_combo.findText(model_name)
            if index >= 0:
                self.model_combo.removeItem(index)
            
            # Remove from settings
            if 'custom_models' in self.settings and model_name in self.settings['custom_models']:
                del self.settings['custom_models'][model_name]
                self.save_settings()
            
            self.update_status(f"Removed model: {model_name}")
            if dialog:
                dialog.accept()

    def setup_model_management(self):
        """Setup UI elements for model management"""
        # Add a button next to the model combo for adding custom models
        model_layout = self.chat_tab.findChild(QHBoxLayout)
        if not model_layout:
            return
            
        # Add model info button
        info_btn = QToolButton()
        info_btn.setText("ℹ️")
        info_btn.setToolTip("Model Information")
        info_btn.clicked.connect(lambda: self.show_model_info(self.model_combo.currentText()))
        
        # Add custom model button
        add_model_btn = QToolButton()
        add_model_btn.setText("➕")
        add_model_btn.setToolTip("Add Custom Model")
        add_model_btn.clicked.connect(self.add_custom_model)
        
        # Insert buttons after the model combo
        for i in range(model_layout.count()):
            item = model_layout.itemAt(i)
            if item and item.widget() == self.model_combo:
                model_layout.insertWidget(i+1, info_btn)
                model_layout.insertWidget(i+2, add_model_btn)
                break
        
        # Load custom models from settings
        if 'custom_models' in self.settings:
            for model_name in self.settings['custom_models']:
                if model_name not in self.models:
                    self.models.append(model_name)
                    self.model_combo.addItem(model_name)
                    
        # Add context menu to model combo
        self.model_combo.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.model_combo.customContextMenuRequested.connect(self._show_model_context_menu)
        
    def _show_model_context_menu(self, position):
        """Show context menu for model combobox"""
        menu = QMenu()
        model_name = self.model_combo.currentText()
        
        # Add actions
        info_action = menu.addAction("Model Information")
        info_action.triggered.connect(lambda: self.show_model_info(model_name))
        
        set_default_action = menu.addAction("Set as Default")
        set_default_action.triggered.connect(lambda: self.set_default_model(model_name))
        
        menu.addSeparator()
        
        add_action = menu.addAction("Add Custom Model")
        add_action.triggered.connect(self.add_custom_model)
        
        # Only enable remove if it's a custom model
        remove_action = menu.addAction("Remove Model")
        is_custom = 'custom_models' in self.settings and model_name in self.settings['custom_models']
        remove_action.setEnabled(is_custom)
        if is_custom:
            remove_action.triggered.connect(lambda: self.remove_custom_model(model_name))
        
        menu.exec(self.model_combo.mapToGlobal(position))

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
        """Allow the user to attach a file to the conversation and process various file types"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Attach File", "", 
                "Text Files (*.txt);;JSON Files (*.json);;Markdown (*.md);;Python (*.py);;CSV (*.csv);;HTML (*.html);;All Files (*.*)")
            
            if not file_path or not os.path.exists(file_path):
                return
            
            file_size = os.path.getsize(file_path)
            max_size = 10 * 1024 * 1024  # 10MB limit
            
            if file_size > max_size:
                QMessageBox.warning(self, "File Too Large", 
                          "File size exceeds 10MB limit.")
                return
                
            file_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_name)[1].lower()
            
            # Initialize attached_files if needed
            if not hasattr(self, 'attached_files'):
                self.attached_files = {}
                self.attached_files[file_name] = file_path
            
            # Define text-based file types
            text_extensions = ['.txt', '.json', '.md', '.py', '.js', '.html', '.css', '.csv', 
                      '.xml', '.yaml', '.yml', '.ini', '.cfg', '.conf', '.sh', '.bat']
            code_extensions = ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', 
                      '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.ts']
            
            # Process text-based files
            file_content = None
            if file_extension in text_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    # Format content based on file type
                    if file_extension == '.json':
                        try:
                            json_data = json.loads(file_content)
                            file_content = json.dumps(json_data, indent=2)
                        except json.JSONDecodeError:
                            QMessageBox.warning(self, "Invalid JSON", 
                                      "The JSON file is not properly formatted.")
                    
                    # Determine language for code files
                    language = ""
                    if file_extension in code_extensions:
                        language = file_extension[1:]  # Remove the dot
                    
                    # Ask if user wants to insert content or just reference
                    if file_content:
                        reply = QMessageBox.question(self, "File Attached", 
                                     f"Do you want to send the contents of {file_name} to the AI?",
                                     QMessageBox.StandardButton.Yes | 
                                     QMessageBox.StandardButton.No)
                        
                        if reply == QMessageBox.StandardButton.Yes:
                            current_text = self.input_box.toPlainText().strip()
                            
                            # Format code blocks properly based on file type
                            if file_extension in code_extensions or file_extension in ['.json', '.md', '.csv']:
                                prefix = f"Content of {file_name}:\n\n```{language}\n"
                                suffix = "\n```"
                            else:
                                prefix = f"Content of {file_name}:\n\n"
                                suffix = ""
                            
                            if current_text:
                                self.input_box.setPlainText(f"{current_text}\n\n{prefix}{file_content}{suffix}")
                            else:
                                self.input_box.setPlainText(f"{prefix}{file_content}{suffix}")
                            
                            self.update_status(f"File content added to input")
                            return
                except UnicodeDecodeError:
                    QMessageBox.warning(self, "Binary File Detected", 
                              f"{file_name} appears to be a binary file and cannot be displayed directly.")
                except Exception as e:
                    QMessageBox.warning(self, "Error Reading File", 
                              f"Could not read the file: {str(e)}")
            else:
                # Binary file handling
                QMessageBox.information(self, "Binary File", 
                             f"{file_name} is a binary file. Only the file reference will be added.")
            
            # Default: just attach file reference
            current_text = self.input_box.toPlainText()
            file_text = f"\n[Attached file: {file_name}]\n"
            
            self.input_box.setPlainText(current_text + file_text if current_text else file_text)
            
            # Add file to the files list if not already present
            existing_items = [self.files_list.item(i).text() for i in range(self.files_list.count())]
            if file_name not in existing_items:
                self.files_list.addItem(file_name)
            
            self.update_status(f"File '{file_name}' attached")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to attach file: {str(e)}")
    
    def open_settings(self):
        """Open the settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Save previous settings for comparison
            previous_language = self.settings.get('language', 'en')
            
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
                
            # Apply language changes if needed
            current_language = self.settings.get('language', 'en')
            if current_language != previous_language:
                # Update translator language
                translator.set_language(current_language)
                
                # Update UI texts
                self.update_ui_language()
                
                self.update_status(translator.tr("language_changed", 
                                               language="English" if current_language == "en" else "Français"))
    
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

    def update_ui_language(self):
        """Update all UI elements to use the current language"""
        # Update window title
        self.setWindowTitle(translator.tr('window_title'))
        
        # Update navigation buttons
        self.chat_nav_btn.setText(f" {translator.tr('chat')}")
        self.templates_nav_btn.setText(f" {translator.tr('templates')}")
        self.history_nav_btn.setText(f" {translator.tr('history')}")
        self.files_nav_btn.setText(f" {translator.tr('files')}")
        self.settings_btn.setText(f" {translator.tr('settings')}")
        
        # Update tab titles
        self.tabs.setTabText(0, translator.tr('chat'))
        self.tabs.setTabText(1, translator.tr('templates'))
        self.tabs.setTabText(2, translator.tr('history'))
        self.tabs.setTabText(3, translator.tr('files'))
        
        # Update chat tab elements
        model_label = self.chat_tab.findChild(QLabel, None, Qt.FindChildOption.FindDirectChildrenOnly)
        if model_label:
            model_label.setText(translator.tr('model'))
        
        # Update other elements in the chat tab
        for btn in self.chat_tab.findChildren(QPushButton):
            if "🗑️" in btn.text():
                btn.setText(translator.tr('clear'))
            elif "📤" in btn.text():
                btn.setText(translator.tr('export'))
        
        # Update input area
        for label in self.chat_tab.findChildren(QLabel):
            if "Template" in label.text():
                label.setText(translator.tr('template'))
        
        self.send_button.setText(translator.tr('send'))
        
        # Update placeholder texts
        self.search_input.setPlaceholderText(translator.tr('search_placeholder'))
        
        # Update status bar
        self.update_status(translator.tr('ready'))

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
