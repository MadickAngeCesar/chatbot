# Madick AI Chatbot

A feature-rich desktop chatbot application built with PyQt6 and Ollama LLMs.

## Features

- Multiple model support (llama3, deepseek, mistral, llama2)
- Chat session management
- Conversation history with search capability
- Streaming responses
- Voice input support
- Template system for quick prompts
- Dark and light themes
- File attachments
- Exportable chat history (JSON, TXT, HTML, MD)
- System tray integration
- Keyboard shortcuts

## Installation

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
   - Pull models: `ollama pull llama3.2:1b mistral:7b llama2:13b`

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

## License

MIT
