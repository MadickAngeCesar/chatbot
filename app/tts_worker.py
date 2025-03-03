from PyQt6.QtCore import QObject, pyqtSignal
import os
import tempfile
import time
import wave
import array
import pyttsx3  # For offline TTS
import requests # For online TTS
import json
import io

class TTSWorkerBase(QObject):
    # Base class remains unchanged
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    speech_ready = pyqtSignal(str)  # Path to generated audio file

    def __init__(self, text, voice_id=None, speech_rate=1.0):
        super().__init__()
        self.text = text
        self.voice_id = voice_id
        self.speech_rate = speech_rate
        self.is_cancelled = False
        
    def cancel(self):
        """Cancel the current TTS operation"""
        self.is_cancelled = True

class OfflineTTSWorker(TTSWorkerBase):
    """Worker for offline text-to-speech processing"""
    
    def __init__(self, text, model_path, speech_rate=1.0):
        super().__init__(text, None, speech_rate)
        self.model_path = model_path
        
    def generate_speech(self):
        """Generate speech using offline TTS model"""
        try:
            # Create temporary file for audio output
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_file.close()
            output_path = temp_file.name
            
            self.progress.emit(10)
            
            # Use pyttsx3 for offline TTS
            engine = pyttsx3.init()
            engine.setProperty('rate', int(engine.getProperty('rate') * self.speech_rate))
            
            # Set voice if available
            voices = engine.getProperty('voices')
            if voices and len(voices) > 0:
                engine.setProperty('voice', voices[0].id)
            
            self.progress.emit(30)
            
            # Save to file
            engine.save_to_file(self.text, output_path)
            
            self.progress.emit(70)
            
            # Wait for file generation to complete
            engine.runAndWait()
            
            self.progress.emit(100)
            self.speech_ready.emit(output_path)
            
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

class OnlineTTSWorker(TTSWorkerBase):
    """Worker for online text-to-speech processing using cloud services"""
    
    def __init__(self, text, voice_id="en-US-Neural2-F", speech_rate=1.0, api_key=None):
        super().__init__(text, voice_id, speech_rate)
        self.api_key = api_key
        
    def generate_speech(self):
        try:
            # Create temporary file for audio output
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_file.close()
            output_path = temp_file.name
            
            self.progress.emit(10)
            
            # Example using a generic TTS service API (replace with your preferred service)
            # This is a placeholder - you'll need to implement the specific API calls
            # for your chosen service (Google, AWS, Azure, etc.)
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "text": self.text,
                "voice": self.voice_id,
                "rate": self.speech_rate
            }
            
            self.progress.emit(30)
            
            # This is a placeholder for the API call
            # Replace with your actual API endpoint and implementation
            # response = requests.post("https://api.your-tts-service.com/synthesize", 
            #                         headers=headers, 
            #                         data=json.dumps(data))
            
            # For demo purposes, use pyttsx3 instead
            engine = pyttsx3.init()
            engine.setProperty('rate', int(engine.getProperty('rate') * self.speech_rate))
            
            # Try to find a matching voice
            voices = engine.getProperty('voices')
            for voice in voices:
                if self.voice_id.lower() in voice.id.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            self.progress.emit(70)
            
            # Save to file
            engine.save_to_file(self.text, output_path)
            engine.runAndWait()
            
            self.progress.emit(100)
            self.speech_ready.emit(output_path)
            
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()
