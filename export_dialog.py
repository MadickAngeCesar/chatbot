from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QRadioButton, 
                           QPushButton, QGroupBox,
                           QLineEdit, QFormLayout, QSpinBox)
import json
import datetime
import markdown

class ExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Chat")
        self.setMinimumWidth(500)
        self.setMinimumHeight(350)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Format selection
        format_group = QGroupBox("Export Format")
        format_layout = QVBoxLayout()
        
        self.format_json = QRadioButton("JSON")
        self.format_json.setChecked(True)
        self.format_json.toggled.connect(self.update_options)
        
        self.format_txt = QRadioButton("Plain Text")
        self.format_txt.toggled.connect(self.update_options)
        
        self.format_md = QRadioButton("Markdown")
        self.format_md.toggled.connect(self.update_options)
        
        self.format_html = QRadioButton("HTML")
        self.format_html.toggled.connect(self.update_options)
        
        format_layout.addWidget(self.format_json)
        format_layout.addWidget(self.format_txt)
        format_layout.addWidget(self.format_md)
        format_layout.addWidget(self.format_html)
        format_group.setLayout(format_layout)
        
        # Options
        self.options_group = QGroupBox("Export Options")
        self.options_layout = QFormLayout()
        
        # File name template
        self.filename_template = QLineEdit("chat_export_%Y%m%d_%H%M%S")
        self.options_layout.addRow("Filename Template:", self.filename_template)
        
        # Include metadata
        self.include_metadata = QCheckBox()
        self.include_metadata.setChecked(True)
        self.options_layout.addRow("Include Metadata:", self.include_metadata)
        
        # Limit conversations
        self.limit_count = QSpinBox()
        self.limit_count.setRange(0, 1000)
        self.limit_count.setValue(0)
        self.limit_count.setSpecialValueText("All")
        self.options_layout.addRow("Max Conversations:", self.limit_count)
        
        self.options_group.setLayout(self.options_layout)
        
        # HTML options (hidden by default)
        self.html_options = QGroupBox("HTML Options")
        html_options_layout = QFormLayout()
        
        self.include_css = QCheckBox()
        self.include_css.setChecked(True)
        html_options_layout.addRow("Include CSS Styling:", self.include_css)
        
        self.include_timestamp = QCheckBox()
        self.include_timestamp.setChecked(True)
        html_options_layout.addRow("Include Timestamps:", self.include_timestamp)
        
        self.html_options.setLayout(html_options_layout)
        self.html_options.setVisible(False)
        
        # Add components to main layout
        layout.addWidget(format_group)
        layout.addWidget(self.options_group)
        layout.addWidget(self.html_options)
        
        # Add buttons
        button_layout = QHBoxLayout()
        export_button = QPushButton("Export")
        export_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(export_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def update_options(self):
        """Update visible options based on selected format"""
        if self.format_html.isChecked():
            self.html_options.setVisible(True)
        else:
            self.html_options.setVisible(False)
            
    def get_export_settings(self):
        """Get the export settings from dialog"""
        format_type = ""
        if self.format_json.isChecked():
            format_type = "json"
        elif self.format_txt.isChecked():
            format_type = "txt"
        elif self.format_md.isChecked():
            format_type = "md"
        elif self.format_html.isChecked():
            format_type = "html"
        
        return {
            "format": format_type,
            "filename_template": self.filename_template.text(),
            "include_metadata": self.include_metadata.isChecked(),
            "limit": self.limit_count.value() if self.limit_count.value() > 0 else None,
            "html_options": {
                "include_css": self.include_css.isChecked(),
                "include_timestamp": self.include_timestamp.isChecked()
            }
        }
        
    @staticmethod
    def export_conversations(conversations, settings, output_path=None):
        """Export conversations based on settings"""
        if not output_path:
            current_time = datetime.datetime.now()
            filename = current_time.strftime(settings["filename_template"])
            output_path = f"{filename}.{settings['format']}"
            
        # Limit conversations if specified
        if settings["limit"]:
            conversations = conversations[:settings["limit"]]
            
        # Export based on format
        if settings["format"] == "json":
            ExportDialog.export_json(conversations, settings, output_path)
        elif settings["format"] == "txt":
            ExportDialog.export_text(conversations, settings, output_path)
        elif settings["format"] == "md":
            ExportDialog.export_markdown(conversations, settings, output_path)
        elif settings["format"] == "html":
            ExportDialog.export_html(conversations, settings, output_path)
            
        return output_path
        
    @staticmethod
    def export_json(conversations, settings, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            if settings["include_metadata"]:
                json.dump({
                    "metadata": {
                        "exported_at": datetime.datetime.now().isoformat(),
                        "conversation_count": len(conversations)
                    },
                    "conversations": [
                        {
                            "timestamp": conv[1],
                            "model": conv[2],
                            "user_message": conv[3],
                            "ai_response": conv[4],
                            "session": conv[5] if len(conv) > 5 else "Default"
                        } for conv in conversations
                    ]
                }, f, indent=2)
            else:
                json.dump([
                    {
                        "timestamp": conv[1],
                        "model": conv[2],
                        "user_message": conv[3],
                        "ai_response": conv[4]
                    } for conv in conversations
                ], f, indent=2)
                
    @staticmethod
    def export_text(conversations, settings, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            if settings["include_metadata"]:
                f.write(f"Exported at: {datetime.datetime.now()}\n")
                f.write(f"Total conversations: {len(conversations)}\n\n")
                f.write("-" * 80 + "\n\n")
                
            for conv in conversations:
                timestamp, model, user_msg, ai_resp = conv[1:5]
                session = conv[5] if len(conv) > 5 else "Default"
                
                if settings["include_metadata"]:
                    f.write(f"Time: {timestamp}\n")
                    f.write(f"Model: {model}\n")
                    f.write(f"Session: {session}\n\n")
                    
                f.write(f"User: {user_msg}\n\n")
                f.write(f"AI: {ai_resp}\n\n")
                f.write("-" * 80 + "\n\n")
                
    @staticmethod
    def export_markdown(conversations, settings, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            if settings["include_metadata"]:
                f.write(f"# Chat Export\n\n")
                f.write(f"**Exported at:** {datetime.datetime.now()}\n\n")
                f.write(f"**Total conversations:** {len(conversations)}\n\n")
                f.write("---\n\n")
                
            for i, conv in enumerate(conversations):
                timestamp, model, user_msg, ai_resp = conv[1:5]
                session = conv[5] if len(conv) > 5 else "Default"
                
                if settings["include_metadata"]:
                    f.write(f"### Conversation {i+1}\n\n")
                    f.write(f"**Time:** {timestamp}  \n")
                    f.write(f"**Model:** {model}  \n")
                    f.write(f"**Session:** {session}  \n\n")
                    
                f.write(f"**User:**\n\n{user_msg}\n\n")
                f.write(f"**AI:**\n\n{ai_resp}\n\n")
                f.write("---\n\n")
                
    @staticmethod
    def export_html(conversations, settings, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            # HTML header
            f.write("<!DOCTYPE html>\n")
            f.write("<html>\n<head>\n")
            f.write("<title>Chat Export</title>\n")
            f.write("<meta charset='utf-8'>\n")
            
            # CSS styling
            if settings["html_options"]["include_css"]:
                f.write("<style>\n")
                f.write("body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }\n")
                f.write("h1 { color: #333; }\n")
                f.write(".conversation { border-bottom: 1px solid #eee; padding: 10px 0; }\n")
                f.write(".metadata { color: #666; font-size: 0.8em; margin-bottom: 10px; }\n")
                f.write(".user-message { background-color: #e3f2fd; padding: 10px; border-radius: 10px; margin: 10px 0; }\n")
                f.write(".ai-message { background-color: #f5f5f5; padding: 10px; border-radius: 10px; margin: 10px 0; }\n")
                f.write("pre { background-color: #272822; color: #f8f8f2; padding: 10px; border-radius: 5px; overflow-x: auto; }\n")
                f.write("</style>\n")
                
            f.write("</head>\n<body>\n")
            
            # Header information
            f.write("<h1>Chat Export</h1>\n")
            
            if settings["include_metadata"]:
                f.write(f"<p>Exported at: {datetime.datetime.now()}</p>\n")
                f.write(f"<p>Total conversations: {len(conversations)}</p>\n")
                f.write("<hr>\n")
                
            # Conversations
            for i, conv in enumerate(conversations):
                timestamp, model, user_msg, ai_resp = conv[1:5]
                session = conv[5] if len(conv) > 5 else "Default"
                
                f.write(f"<div class='conversation' id='conv-{i+1}'>\n")
                
                if settings["include_metadata"]:
                    f.write("<div class='metadata'>\n")
                    if settings["html_options"]["include_timestamp"]:
                        f.write(f"<p>Time: {timestamp}</p>\n")
                    f.write(f"<p>Model: {model}</p>\n")
                    f.write(f"<p>Session: {session}</p>\n")
                    f.write("</div>\n")
                    
                f.write("<div class='user-message'>\n")
                f.write(f"<strong>User:</strong>\n<p>{user_msg}</p>\n")
                f.write("</div>\n")
                
                f.write("<div class='ai-message'>\n")
                f.write(f"<strong>AI:</strong>\n<div>{markdown.markdown(ai_resp)}</div>\n")
                f.write("</div>\n")
                
                f.write("</div>\n")
                
            # Close HTML
            f.write("</body>\n</html>")
