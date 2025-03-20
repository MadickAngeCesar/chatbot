from PyQt6.QtCore import pyqtSignal, QThread

class AIResponseThread(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, llm, prompt):
        super().__init__() 
        self.llm = llm
        self.prompt = prompt

    def run(self):
        try:
            response = self.llm.invoke(self.prompt)
            self.response_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))