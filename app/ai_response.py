from PyQt6.QtCore import QThread, pyqtSignal

class AIResponseThread(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, llm, prompt, parent=None):
        super().__init__(parent)
        self.llm = llm
        self.prompt = prompt
        
    def run(self):
        try:
            # Generate response using the LLM
            response = self.llm.invoke(self.prompt)
            
            # Emit the response signal
            self.response_ready.emit(response)
            
        except Exception as e:
            # Emit the error signal
            self.error_occurred.emit(str(e))