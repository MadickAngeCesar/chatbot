from PyQt6.QtWidgets import (QApplication, QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QPushButton, QLabel, QMessageBox, QFileDialog,
                           QMenu, QFrame, QToolButton, QDialog,
                           QSizePolicy)
from PyQt6.QtCore import Qt, QThread
from datetime import datetime
import os
from app.tts_worker import OfflineTTSWorker
from app.tts_worker import OnlineTTSWorker  
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl
import subprocess
import platform
import shutil

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
            # Note: This method handles Text-to-Speech (TTS), not Speech-to-Text (STT)
            # For offline STT implementation, see the VoiceWorker.record() method
            
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
                player.errorOccurred.connect(lambda _error, errorString: 
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
        self.tts_thread = None
        
    def __del__(self):
        """Destructor to ensure threads are cleaned up when object is garbage collected."""
        self._cleanup_threads()
        
    def _cleanup_threads(self):
        """Ensure all threads are properly terminated before object destruction."""
        try:
            if hasattr(self, 'tts_thread') and self.tts_thread is not None and self.tts_thread.isRunning():
                if hasattr(self, 'tts_worker') and hasattr(self.tts_worker, 'cancel'):
                    self.tts_worker.cancel()
                self.tts_thread.quit()
                # Use longer timeout and check if thread actually finished
                if not self.tts_thread.wait(3000):  # Wait up to 3 seconds for thread to finish
                    self.tts_thread.terminate()  # Force termination if necessary
                    self.tts_thread.wait()  # Wait for termination to complete
        except RuntimeError:
            # Handle case where thread might already be deleted
            pass
            self.tts_thread.quit()
            # Use longer timeout and check if thread actually finished
            if not self.tts_thread.wait(3000):  # Wait up to 3 seconds for thread to finish
                self.tts_thread.terminate()  # Force termination if necessary
                self.tts_thread.wait()  # Wait for termination to complete
