# Madick AI Chatbot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-green)](https://ollama.ai)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-41CD52)](https://www.riverbankcomputing.com/software/pyqt/)

A feature-rich desktop chatbot application built with PyQt6 and Ollama LLMs, designed for seamless local AI interactions.

<div align="center">
  <!-- Placeholder for a logo or screenshot -->
  <p><i>Intelligent conversations on your desktop - no cloud required</i></p>
</div>

## ✨ Features

- **Multiple LLM Support**: Seamlessly switch between various models:
  - Llama 3 (8B and 70B variants)
  - DeepSeek
  - Mistral (7B and Instruct)
  - Llama 2
  - Any other model supported by Ollama
- **Chat Management**:
  - Create, save, and load multiple chat sessions
  - Organize conversations by topic or project
- **Conversation History**: Full searchable history with metadata
- **Real-time Interactions**:
  - Streaming responses for natural conversation flow
  - Voice input support for hands-free operation
- **Productivity Tools**:
  - Template system for frequently used prompts
  - File attachments for context-aware conversations
  - Code syntax highlighting
- **User Experience**:
  - Dark and light themes
  - System tray integration
  - Comprehensive keyboard shortcuts
- **Export Options**: Save conversations in JSON, TXT, HTML, or MD formats

## 🚀 Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/madick-ai-chatbot.git
cd madick-ai-chatbot
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Make sure you have Ollama installed and running:
   - Download from [ollama.ai](https://ollama.ai)
   - Pull models: `ollama pull llama3.2:1b`
   - For more information about Ollama, see the [Ollama Documentation](OLLAMA.md)

## Usage

Run the application:
```
python main.py
```

Or on Windows, you can double-click the `run_chatbot.bat` file.

### Keyboard Shortcuts

- `Ctrl+Enter`: Send message
- `Ctrl+L`: Clear chat
- `Ctrl+E`: Export chat
- `Ctrl+F`: Search in chat
- `Ctrl+T`: Toggle theme
- `Ctrl+N`: New session
- `Ctrl+Shift+V`: Voice input
- `Ctrl+,`: Open settings

## Project Structure

- `main.py` - Application entry point
- `chatbot.py` - Main application window and UI
- `database.py` - SQLite database for conversation history
- `settings_dialog.py` - Settings configuration dialog
- `splash_screen.py` - Application splash screen
- `icon_manager.py` - Icon management and fallback icons
- `templates_manager.py` - Prompt template management
- `themes.py` - Theme management
- `welcome_screen.py` - First-run welcome wizard
- `export_dialog.py` - Dialog for exporting conversations

## Dependencies

- PyQt6
- langchain-ollama
- markdown
- pygments
- SpeechRecognition

## 🛠️ Development Setup

1. Set up a virtual environment (recommended):
```
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

2. Install the development dependencies:
```
pip install -r requirements-dev.txt
```

3. Run the application in development mode:
```
python main.py
```

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## License

MIT
