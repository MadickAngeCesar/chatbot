from PyQt6.QtWidgets import QSplashScreen, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont

class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__(QPixmap(600, 300))
        self.progress_value = 0
        
        # Create pixmap for splash screen
        pixmap = QPixmap(600, 300)
        pixmap.fill(QColor("#1e1e1e"))
        self.setPixmap(pixmap)
        
        # Add progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(50, 200, 500, 20)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 5px;
                text-align: center;
                color: white;
                background-color: #2b2b2b;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.progress = 0
        
    def paintEvent(self, event):
        # Get a copy of the current pixmap
        base_pixmap = self.pixmap()
        temp_pixmap = base_pixmap.copy()  # create an independent copy

        # Draw our custom text on the temporary pixmap
        painter = QPainter(temp_pixmap)
        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        painter.drawText(0, 0, 600, 150, Qt.AlignmentFlag.AlignCenter, "Madick AI Chatbot")
        painter.setFont(QFont("Arial", 12))
        painter.drawText(0, 140, 600, 50, Qt.AlignmentFlag.AlignCenter, "Loading...")
        painter.end()

        # Now paint the modified pixmap onto the widget
        painter2 = QPainter(self)
        painter2.drawPixmap(0, 0, temp_pixmap)
        painter2.end()

        
    def update_progress(self, step=10):
        self.progress_value += step
        self.showMessage(f"Loading... {self.progress_value}%", 
                         Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, 
                         QColor("white"))
        if self.progress > 100:
            self.progress = 100
        self.progress_bar.setValue(self.progress)
        
    def show_and_finish(self, window, duration=2000):
        """Show splash screen and then transition to main window after duration"""
        self.show()
        
        # Simulate loading with a timer
        for i in range(1, 11):
            QTimer.singleShot(i * 200, lambda step=i: self.update_progress(10))
        
        # Close splash and show main window
        QTimer.singleShot(duration, lambda: (self.finish(window), self.close()))
        
    def finish_and_show(self, window):
        self.finish(window)
        window.show()
