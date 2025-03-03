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
    def __init__(self, is_user=False, chat_window=None):
        super().__init__()
        
        self.is_user = is_user
        self.chat_window = chat_window
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI components of the message bubble"""
        # Set frame style
        if self.is_user:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2196F3;
                    border-radius: 10px;
                    margin-left: 80px;
                    margin-right: 10px;
                    padding: 10px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #444444;
                    border-radius: 10px;
                    margin-left: 10px;
                    margin-right: 80px;
                    padding: 10px;
                }
            """)
            
        # Create layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        
        # Top bar with timestamp
        top_layout = QHBoxLayout()
        
        # Sender label (User/AI)
        self.sender_label = QLabel("User" if self.is_user else "AI")
        self.sender_label.setStyleSheet("color: white; font-weight: bold;")
        top_layout.addWidget(self.sender_label)
        
        top_layout.addStretch()
        
        # Timestamp label
        self.timestamp = QLabel()
        self.timestamp.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 10px;")
        top_layout.addWidget(self.timestamp)
        
        main_layout.addLayout(top_layout)
        
        # Message content
        self.content = QTextEdit()
        self.content.setReadOnly(True)
        self.content.setFrameStyle(QFrame.Shape.NoFrame)
        if self.is_user:
            self.content.setStyleSheet("""
                QTextEdit {
                    background-color: transparent;
                    color: white;
                    border: none;
                }
            """)
        else:
            self.content.setStyleSheet("""
                QTextEdit {
                    background-color: transparent;
                    color: white;
                    border: none;
                }
                a {
                    color: #bb86fc;
                }
                pre {
                    background-color: #2d2d2d;
                    padding: 10px;
                    border-radius: 5px;
                    font-family: 'Courier New', monospace;
                }
            """)
        
        self.content.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.content.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        main_layout.addWidget(self.content)
        
        # Add action buttons if not a user message
        if not self.is_user and self.chat_window:
            button_layout = QHBoxLayout()
            button_layout.setSpacing(5)
            
            # Copy button
            copy_btn = QPushButton("Copy")
            copy_btn.setStyleSheet("""
                QPushButton {
                    background-color: #555555;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #666666;
                }
            """)
            copy_btn.clicked.connect(self.copy_content)
            button_layout.addWidget(copy_btn)
            
            # Speak button (text-to-speech)
            speak_btn = QPushButton("Speak")
            speak_btn.setStyleSheet("""
                QPushButton {
                    background-color: #555555;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #666666;
                }
            """)
            speak_btn.clicked.connect(self.speak_content)
            button_layout.addWidget(speak_btn)
            
            button_layout.addStretch()
            main_layout.addLayout(button_layout)
            
    def set_content(self, text, timestamp=""):
        """Set the content of the message bubble"""
        self.content.setText(text)
        if timestamp:
            self.timestamp.setText(timestamp)
            
        # Adjust text edit height to fit content
        document_height = self.content.document().size().height()
        scrollbar_height = self.content.horizontalScrollBar().height()
        content_margins = self.content.contentsMargins()
        
        # Calculate and set the minimum height (with a maximum limit)
        min_height = min(document_height + scrollbar_height + content_margins.top() + content_margins.bottom() + 10, 300)
        self.content.setMinimumHeight(int(min_height))
        
    def copy_content(self):
        """Copy the content to clipboard"""
        if hasattr(self.chat_window, 'clipboard'):
            self.chat_window.clipboard().setText(self.content.toPlainText())
            if hasattr(self.chat_window, 'update_status'):
                self.chat_window.update_status("Content copied to clipboard")
        
    def speak_content(self):
        """Speak the content using text-to-speech"""
        if hasattr(self.chat_window, 'tts_engine'):
            text = self.content.toPlainText()
            self.chat_window.tts_engine.say(text)
            self.chat_window.tts_engine.runAndWait()
