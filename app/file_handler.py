import os
import json
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import Qt

class FileHandler:
    def __init__(self, main_window=None):
        self.main_window = main_window
        self.attached_files = {}
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit

        # Define text-based file types
        self.text_extensions = ['.txt', '.json', '.md', '.py', '.js', '.html', '.css', '.csv', 
                      '.xml', '.yaml', '.yml', '.ini', '.cfg', '.conf', '.sh', '.bat']
        self.code_extensions = ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', 
                      '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.ts']

    def attach_file(self, input_box=None, files_list=None):
        """Allow the user to attach a file to the conversation"""
        if not self.main_window:
            return None, "No main window reference"
            
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self.main_window, "Attach File", "", 
                "Text Files (*.txt);;JSON Files (*.json);;Markdown (*.md);;Python (*.py);;CSV (*.csv);;HTML (*.html);;All Files (*.*)")
            
            if not file_path or not os.path.exists(file_path):
                return None, "No file selected"
            
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                QMessageBox.warning(self.main_window, "File Too Large", 
                          "File size exceeds 10MB limit.")
                return None, "File too large"
                
            file_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_name)[1].lower()
            
            # Store file reference
            self.attached_files[file_name] = file_path
            
            # Process text-based files
            file_content = None
            if file_extension in self.text_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    # Format JSON content
                    if file_extension == '.json':
                        try:
                            json_data = json.loads(file_content)
                            file_content = json.dumps(json_data, indent=2)
                        except json.JSONDecodeError:
                            QMessageBox.warning(self.main_window, "Invalid JSON", 
                                      "The JSON file is not properly formatted.")
                    
                    # Determine language for code files
                    language = ""
                    if file_extension in self.code_extensions:
                        language = file_extension[1:]  # Remove the dot
                    
                    # Ask if user wants to insert content or just reference
                    if file_content and input_box:
                        reply = QMessageBox.question(self.main_window, "File Attached", 
                                     f"Do you want to send the contents of {file_name} to the AI?",
                                     QMessageBox.StandardButton.Yes | 
                                     QMessageBox.StandardButton.No)
                        
                        if reply == QMessageBox.StandardButton.Yes:
                            current_text = input_box.toPlainText().strip()
                            
                            # Format code blocks properly based on file type
                            if file_extension in self.code_extensions or file_extension in ['.json', '.md', '.csv']:
                                prefix = f"Content of {file_name}:\n\n```{language}\n"
                                suffix = "\n```"
                            else:
                                prefix = f"Content of {file_name}:\n\n"
                                suffix = ""
                            
                            if current_text:
                                input_box.setPlainText(f"{current_text}\n\n{prefix}{file_content}{suffix}")
                            else:
                                input_box.setPlainText(f"{prefix}{file_content}{suffix}")
                            
                            if self.main_window:
                                self.main_window.update_status(f"File content added to input")
                                
                            # Add to files list if provided
                            if files_list:
                                self._update_files_list(files_list, file_name)
                                
                            return file_path, "File content added"
                except UnicodeDecodeError:
                    QMessageBox.warning(self.main_window, "Binary File Detected", 
                              f"{file_name} appears to be a binary file and cannot be displayed directly.")
                except Exception as e:
                    QMessageBox.warning(self.main_window, "Error Reading File", 
                              f"Could not read the file: {str(e)}")
            else:
                # Binary file handling
                QMessageBox.information(self.main_window, "Binary File", 
                             f"{file_name} is a binary file. Only the file reference will be added.")
            
            # Default: just attach file reference
            if input_box:
                current_text = input_box.toPlainText()
                file_text = f"\n[Attached file: {file_name}]\n"
                input_box.setPlainText(current_text + file_text if current_text else file_text)
            
            # Add to files list if provided
            if files_list:
                self._update_files_list(files_list, file_name)
                
            if self.main_window:
                self.main_window.update_status(f"File '{file_name}' attached")
                
            return file_path, f"File '{file_name}' attached"
            
        except Exception as e:
            error_msg = f"Failed to attach file: {str(e)}"
            if self.main_window:
                QMessageBox.critical(self.main_window, "Error", error_msg)
            return None, error_msg
    
    def _update_files_list(self, files_list, file_name):
        """Add file to the files list widget if not already present"""
        existing_items = [files_list.item(i).text() for i in range(files_list.count())]
        if file_name not in existing_items:
            files_list.addItem(file_name)

    def export_chat(self, conversations=None):
        """Export chat history to a file"""
        if not self.main_window:
            return False, "No main window reference"
            
        filename, _ = QFileDialog.getSaveFileName(
            self.main_window, "Export Chat History", "", 
            "JSON Files (*.json);;Text Files (*.txt);;Markdown (*.md)")
            
        if not filename:
            return False, "Export cancelled"
            
        if not conversations:
            if hasattr(self.main_window, 'db'):
                conversations = self.main_window.db.get_recent_conversations()
            else:
                return False, "No conversations to export"
        
        try:
            if filename.endswith('.json'):
                with open(filename, 'w') as f:
                    json.dump([{
                        'timestamp': conv[1],
                        'model': conv[2],
                        'user_message': conv[3],
                        'ai_response': conv[4]
                    } for conv in conversations], f, indent=2)
            elif filename.endswith('.md'):
                with open(filename, 'w') as f:
                    f.write("# Chat History\n\n")
                    for conv in conversations:
                        f.write(f"## {conv[1]} - Model: {conv[2]}\n\n")
                        f.write(f"**User**: {conv[3]}\n\n")
                        f.write(f"**AI**: {conv[4]}\n\n")
            else:
                # Default to plain text format
                with open(filename, 'w') as f:
                    for conv in conversations:
                        f.write(f"Time: {conv[1]}\nModel: {conv[2]}\n")
                        f.write(f"User: {conv[3]}\nAI: {conv[4]}\n\n")
            
            if self.main_window:
                self.main_window.update_status(f"Chat history exported to {filename}")
            return True, f"Chat history exported to {filename}"
            
        except Exception as e:
            error_msg = f"Error exporting chat history: {str(e)}"
            if self.main_window:
                self.main_window.update_status(error_msg)
                QMessageBox.critical(self.main_window, "Export Error", error_msg)
            return False, error_msg

    def get_file_content(self, filename):
        """Get content of an attached file by name"""
        if filename not in self.attached_files:
            return None, f"File '{filename}' not found in attachments"
            
        file_path = self.attached_files[filename]
        if not os.path.exists(file_path):
            return None, f"File '{filename}' does not exist on disk"
            
        file_extension = os.path.splitext(filename)[1].lower()
        
        try:
            if file_extension in self.text_extensions:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content, f"File '{filename}' content retrieved"
            else:
                return None, f"File '{filename}' is not a text file"
        except Exception as e:
            return None, f"Error reading file '{filename}': {str(e)}"

    def view_file(self, filename):
        """Open a dialog to view file content"""
        if not self.main_window or filename not in self.attached_files:
            return False
            
        content, message = self.get_file_content(filename)
        if not content:
            QMessageBox.warning(self.main_window, "File Error", message)
            return False
            
        # Create dialog to view file
        dialog = QMessageBox(self.main_window)
        dialog.setWindowTitle(f"File: {filename}")
        dialog.setText(content[:1000] + ("..." if len(content) > 1000 else ""))
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        dialog.exec()
        return True

    def remove_attached_file(self, filename, files_list=None):
        """Remove an attached file from the list"""
        if filename in self.attached_files:
            del self.attached_files[filename]
            
            # Remove from UI list if provided
            if files_list:
                items = files_list.findItems(filename, Qt.MatchExactly)
                for item in items:
                    row = files_list.row(item)
                    files_list.takeItem(row)
                    
            if self.main_window:
                self.main_window.update_status(f"File '{filename}' removed")
                
            return True, f"File '{filename}' removed"
        return False, f"File '{filename}' not found"

    def get_all_attached_files(self):
        """Get a list of all attached files"""
        return list(self.attached_files.keys())