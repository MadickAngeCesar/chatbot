from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QPushButton, QScrollArea,
                           QComboBox, QLabel, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from langchain_ollama import OllamaLLM
from database import ChatDatabase
import sys

class ChatBotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Madick AI Chatbot")
        self.setMinimumSize(1000, 700)
        
        # Initialize database
        self.db = ChatDatabase()
        
        # Available models
        self.models = ["llama3.2:1b", "deepseek-r1", "mistral:7b", "llama2:13b"]
        self.current_model = "llama3.2:1b"
        self.llm = OllamaLLM(model=self.current_model)
        
        self.setup_ui()
        self.load_chat_history()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Model selection area
        model_layout = QHBoxLayout()
        model_label = QLabel("Select Model:")
        model_label.setStyleSheet("color: white;")
        self.model_combo = QComboBox()
        self.model_combo.addItems(self.models)
        self.model_combo.setStyleSheet("""
            QComboBox {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        self.model_combo.currentTextChanged.connect(self.change_model)
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        model_layout.addStretch()
        
        # Clear chat button
        self.clear_button = QPushButton("Clear Chat")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        self.clear_button.clicked.connect(self.clear_chat)
        model_layout.addWidget(self.clear_button)
        
        layout.addLayout(model_layout)
        
        # Chat display area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3f3f3f;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }
        """)
        
        # Input area
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
        
        # Send button
        self.send_button = QPushButton("Send")
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
        
        # Layout assembly
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_button)
        
        layout.addWidget(self.chat_area)
        layout.addLayout(input_layout)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
            }
        """)

    def send_message(self):
        user_message = self.input_box.toPlainText().strip()
        if not user_message:
            return
            
        # Display user message
        self.chat_area.append(f"<span style='color: #4CAF50;'>You:</span> {user_message}")
        
        # Get AI response
        try:
            response = self.llm.invoke(user_message)
            self.chat_area.append(f"<span style='color: #2196F3;'>AI:</span> {response}\n")
            
            # Save to database
            self.db.save_conversation(self.current_model, user_message, response)
        except Exception as e:
            self.chat_area.append(f"<span style='color: #f44336;'>Error:</span> Could not get response from AI.\n")
            
        # Clear input box
        self.input_box.clear()

    def change_model(self, model_name):
        self.current_model = model_name
        self.llm = OllamaLLM(model=model_name)
        self.chat_area.append(f"<span style='color: #ff9800;'>System:</span> Switched to {model_name} model\n")

    def clear_chat(self):
        reply = QMessageBox.question(self, 'Clear Chat', 
                                   'Are you sure you want to clear the chat history?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.chat_area.clear()
            self.db.clear_history()

    def load_chat_history(self):
        conversations = self.db.get_recent_conversations()
        for conv in conversations[::-1]:  # Display in chronological order
            _, timestamp, model, user_msg, ai_resp = conv
            self.chat_area.append(f"<span style='color: #4CAF50;'>You:</span> {user_msg}")
            self.chat_area.append(f"<span style='color: #2196F3;'>AI:</span> {ai_resp}\n")

def main():
    app = QApplication(sys.argv)
    window = ChatBotWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
