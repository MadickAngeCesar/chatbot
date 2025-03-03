import sys
from PyQt6.QtWidgets import QApplication, QDialog
from app.chatbot import ChatBotWindow
from app.welcome_screen import WelcomeScreen

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Run setup wizard
    wizard = WelcomeScreen()
    if wizard.exec() == QDialog.DialogCode.Accepted:
        user_settings = wizard.get_settings()
    
    # Create main window
    window = ChatBotWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
