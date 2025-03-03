from PyQt6.QtWidgets import (QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QPushButton, QComboBox, QLabel, QProgressBar, QDialog,
                           QCheckBox)
from PyQt6.QtCore import pyqtSignal, QThread, QObject
import json
import speech_recognition as sr
from app.icon_manager import IconManager
import os
from app.chatbot_translator import Translator


# Create a global translator instance
translator = Translator()

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
                
                # Begin listening loop - continue until user stops
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
                            
                        # Emit the result but continue recording
                        self.partial_result.emit(text)
                        
                        # Don't break the loop - continue recording until user stops
                        
                    except sr.WaitTimeoutError:
                        # Just continue listening
                        continue
                    except sr.UnknownValueError:
                        # Emit error but continue recording
                        self.error.emit(translator.tr('speech_not_understood'))
                        continue
                    except sr.RequestError as e:
                        # Emit error but continue recording
                        self.error.emit(translator.tr('service_error', error=str(e)))
                        continue
                        
        except Exception as e:
            self.error.emit(translator.tr('recording_error', error=str(e)))
        finally:
            # When recording finally stops (user stops it), emit the finished signal
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
