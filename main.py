import sys
from PyQt6.QtWidgets import QApplication, QDialog
from chatbot import ChatBotWindow
from splash_screen import SplashScreen
from icon_manager import IconManager
from welcome_screen import WelcomeScreen
from PyQt6.QtCore import QTimer

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Ensure icon directory exists
    IconManager.ensure_icon_directory()
    
    # Show splash screen
    splash = SplashScreen()
    splash.show()
    # Close splash after 2 seconds
    QTimer.singleShot(2000, splash.close)
    
    # Run setup wizard
    wizard = WelcomeScreen()
    user_settings = {}
    if wizard.exec() == QDialog.DialogCode.Accepted:
        user_settings = wizard.get_settings()
    
    # Create main window
    window = ChatBotWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
