from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
import os

class IconManager:
    _icons = {}
    
    @classmethod
    def get_icon(cls, name):
        """Get an icon by name, create it if it doesn't exist"""
        if name in cls._icons:
            return cls._icons[name]
            
        # Check if file exists
        icon_path = f"icons/{name}.png"
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
        else:
            # Create fallback icon
            icon = cls._create_fallback_icon(name)
            
        cls._icons[name] = icon
        return icon
    
    @staticmethod
    def _create_fallback_icon(name):
        """Create a fallback icon with the first letter of the name"""
        pixmap = QPixmap(32, 32)
        
        # Choose color based on name
        colors = {
            "app": QColor("#4CAF50"),
            "chat": QColor("#2196F3"),
            "settings": QColor("#FF9800"),
            "send": QColor("#4CAF50"),
            "attachment": QColor("#9C27B0"),
            "microphone": QColor("#F44336"),
            "copy": QColor("#2196F3"),
            "edit": QColor("#FF9800"),
            "speak": QColor("#795548"),
            "bookmark": QColor("#FFC107"),
            "trash": QColor("#F44336"),
            "export": QColor("#2196F3"),
            "template": QColor("#009688"),
            "history": QColor("#607D8B"),
            "file": QColor("#3F51B5"),
            "plus": QColor("#4CAF50")
        }
        
        color = colors.get(name, QColor("#757575"))  # Default gray
        
        pixmap.fill(color)
        
        # Add text
        painter = QPainter(pixmap)
        painter.setPen(QColor("white"))
        painter.drawText(0, 0, 32, 32, 0x124, name[0].upper())
        painter.end()
        
        return QIcon(pixmap)

    @classmethod
    def ensure_icon_directory(cls):
        """Create the icons directory if it doesn't exist"""
        if not os.path.exists("icons"):
            os.makedirs("icons")
