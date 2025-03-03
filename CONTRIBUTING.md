# Contributing to Madick AI Chatbot

First off, thank you for considering contributing to Madick AI Chatbot! It's people like you that make this project such a great tool. We welcome contributions from everyone, regardless of experience level.

## 📋 Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/madick-ai-chatbot.git
   cd madick-ai-chatbot
   ```
3. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
5. Run the application in development mode:
   ```bash
   python main.py
   ```

### Environment Setup

- Ensure you have Ollama installed: [ollama.ai](https://ollama.ai)
- Pull at least one model for testing: `ollama pull llama3.2:1b` or another model

## 🛠 How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in the [Issues](https://github.com/yourusername/madick-ai-chatbot/issues)
2. If not, create a new issue with:
   - A clear title and description
   - As much relevant information as possible (OS, Python version, etc.)
   - Steps to reproduce the issue
   - Expected vs. actual behavior
   - Screenshots if applicable

### Suggesting Enhancements

1. Check if the enhancement has already been suggested
2. Create a new issue with:
   - A clear title and description
   - Explanation of why this enhancement would be useful
   - Any relevant examples or mockups

### Your First Code Contribution

1. Find an issue to work on or create a new one
2. Comment on the issue expressing your interest
3. Create a branch in your fork with a descriptive name:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. Make your changes, following our code style guidelines

### Pull Request Process

1. Update the README.md or documentation with details of changes if needed
2. Make sure your code passes all tests
3. Submit a pull request to the main repository:
   - Use a clear and descriptive title
   - Reference the issue it addresses
   - Describe the changes in detail
   - Explain how to test the changes

## 💻 Coding Guidelines

### Python Style

- Follow PEP 8 style guidelines
- Use 4 spaces for indentation (no tabs)
- Maximum line length of 100 characters
- Use docstrings for all classes, methods, and functions
- Use type hints where applicable

### PyQt Conventions

- UI files should be in the `ui/` directory
- Connect signals and slots using PyQt's `connect()` method
- Use Qt Designer for complex UI layouts when possible

### Git Commit Messages

- Use clear, concise messages in the imperative mood
- Example: "Add voice input feature" instead of "Added voice input feature"
- Reference issue numbers when applicable: "Fix crash on startup (#42)"

## 🧪 Testing

- Add tests for new features or bug fixes
- Make sure all tests pass before submitting a PR:
  ```bash
  pytest
  ```
- Include both unit and integration tests when applicable

## 📚 Documentation

- Keep documentation up-to-date with code changes
- Document all public APIs, classes, and functions
- Add comments for complex logic
- Update the README.md with any new features or changes to installation/usage

## 📁 Project Structure

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
- `tests/` - Test directory

## 🤝 Communication

- Join our [Discord](https://discord.gg/your-invite-link) for discussions
- Use GitHub Issues for bug reports and feature requests
- Tag maintainers when you need specific attention

## ⚙️ Development Workflow

1. Create a new branch for each feature or bugfix
2. Test your changes locally
3. Submit a PR for review
4. Address any requested changes
5. Once approved, your changes will be merged

Thank you for contributing to Madick AI Chatbot! Your efforts help make this project better for everyone.
