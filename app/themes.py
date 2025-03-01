from PyQt6.QtGui import QPalette, QColor

class ThemeManager:
    @staticmethod
    def apply_dark_theme(app):
        """Apply dark theme to the application"""
        palette = QPalette()
        
        # Set window and widget background colors
        palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#2b2b2b"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#3f3f3f"))
        
        # Text colors
        palette.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#bbbbbb"))
        
        # Button colors
        palette.setColor(QPalette.ColorRole.Button, QColor("#3f3f3f"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
        
        # Link colors
        palette.setColor(QPalette.ColorRole.Link, QColor("#4fc3f7"))
        
        # Highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#4CAF50"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        
        # Disabled colors
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor("#666666"))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#666666"))
        
        app.setPalette(palette)
        
        # Return additional stylesheet for custom widgets
        return """
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
            }
            QScrollArea {
                background-color: #2b2b2b;
                border: none;
            }
            QTextEdit {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QComboBox {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
            }
            QLineEdit {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
            }
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
            QToolTip {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3f3f3f;
                border-radius: 3px;
            }
        """

    @staticmethod
    def apply_light_theme(app):
        """Apply light theme to the application"""
        palette = QPalette()
        
        # Set window and widget background colors
        palette.setColor(QPalette.ColorRole.Window, QColor("#f5f5f5"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#212121"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#e0e0e0"))
        
        # Text colors
        palette.setColor(QPalette.ColorRole.Text, QColor("#212121"))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#757575"))
        
        # Button colors
        palette.setColor(QPalette.ColorRole.Button, QColor("#e0e0e0"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#212121"))
        
        # Link colors
        palette.setColor(QPalette.ColorRole.Link, QColor("#1976D2"))
        
        # Highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#4CAF50"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        
        # Disabled colors
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor("#9e9e9e"))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#9e9e9e"))
        
        app.setPalette(palette)
        
        # Return additional stylesheet for custom widgets
        return """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                background-color: #f5f5f5;
            }
            QScrollArea {
                background-color: #ffffff;
                border: none;
            }
            QTextEdit {
                background-color: #ffffff;
                color: #212121;
                border: 1px solid #bdbdbd;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                background-color: #e0e0e0;
                color: #212121;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QComboBox {
                background-color: #ffffff;
                color: #212121;
                border: 1px solid #bdbdbd;
                border-radius: 5px;
                padding: 5px;
            }
            QLineEdit {
                background-color: #ffffff;
                color: #212121;
                border: 1px solid #bdbdbd;
                border-radius: 5px;
                padding: 5px;
            }
            QTabWidget::pane {
                border: 1px solid #bdbdbd;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #757575;
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #212121;
            }
            QToolTip {
                background-color: #ffffff;
                color: #212121;
                border: 1px solid #bdbdbd;
                border-radius: 3px;
            }
        """

    @classmethod
    def get_bubble_style(cls, is_user=True, is_dark=True):
        """Get style for message bubbles based on theme and sender"""
        if is_dark:
            # Dark theme styles
            if is_user:
                return """
                    QFrame {
                        background-color: #2a5298;
                        border-radius: 10px;
                        margin-left: 80px;
                        margin-right: 10px;
                        padding: 10px;
                    }
                """
            else:
                return """
                    QFrame {
                        background-color: #3f3f3f;
                        border-radius: 10px;
                        margin-left: 10px;
                        margin-right: 80px;
                        padding: 10px;
                    }
                """
        else:
            # Light theme styles
            if is_user:
                return """
                    QFrame {
                        background-color: #2196F3;
                        color: white;
                        border-radius: 10px;
                        margin-left: 80px;
                        margin-right: 10px;
                        padding: 10px;
                    }
                """
            else:
                return """
                    QFrame {
                        background-color: #e0e0e0;
                        color: #212121;
                        border-radius: 10px;
                        margin-left: 10px;
                        margin-right: 80px;
                        padding: 10px;
                    }
                """
