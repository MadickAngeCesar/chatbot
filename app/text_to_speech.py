import pyttsx3
from PyQt6.QtCore import QObject, pyqtSignal, QThread
import re

class TextToSpeechEngine(QObject):
    """Handles text-to-speech conversion"""
    
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            self.engine = pyttsx3.init()
            self.configure_engine()
            self.available = True
        except Exception as e:
            self.error.emit(f"TTS initialization error: {str(e)}")
            self.available = False
    
    def configure_engine(self):
        """Configure TTS engine settings"""
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
        
        # Get available voices
        voices = self.engine.getProperty('voices')
        if voices:
            # Use the first available voice by default
            self.engine.setProperty('voice', voices[0].id)
    
    def set_voice(self, voice_index):
        """Set the voice by index"""
        voices = self.engine.getProperty('voices')
        if 0 <= voice_index < len(voices):
            self.engine.setProperty('voice', voices[voice_index].id)
    
    def set_rate(self, rate):
        """Set the speech rate (words per minute)"""
        self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume):
        """Set the volume (0.0 to 1.0)"""
        self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
    
    def get_available_voices(self):
        """Get list of available voices"""
        voices = self.engine.getProperty('voices')
        return [(voice.id, voice.name) for voice in voices]
    
    def clean_text_for_tts(self, text):
        """Clean markdown and code blocks from text for better TTS"""
        # Remove code blocks
        text = re.sub(r'```[\s\S]*?```', 'Code block removed for speech.', text)
        # Remove markdown links and replace with just the text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Remove other markdown syntax
        text = re.sub(r'[*_~`#]', '', text)
        # Replace multiple newlines with a single one
        text = re.sub(r'\n{2,}', '\n', text)
        return text
    
    def speak(self, text):
        """Speak text asynchronously"""
        if not self.available:
            self.error.emit("Text-to-speech is not available")
            return
            
        text = self.clean_text_for_tts(text)
        
        # Create a speaking thread
        self.speak_thread = SpeakThread(self.engine, text)
        self.speak_thread.finished.connect(self.finished)
        self.speak_thread.start()
    
    def stop_speaking(self):
        """Stop current speech"""
        if self.available:
            self.engine.stop()

class SpeakThread(QThread):
    """Thread for non-blocking text-to-speech"""
    
    def __init__(self, engine, text):
        super().__init__()
        self.engine = engine
        self.text = text
        
    def run(self):
        self.engine.say(self.text)
        self.engine.runAndWait()
