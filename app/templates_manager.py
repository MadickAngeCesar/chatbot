import json
import os
from datetime import datetime

class TemplateManager:
    def __init__(self, template_file='templates.json'):
        self.template_file = template_file
        self.templates = self.load_templates()
        
    def load_templates(self):
        """Load templates from file or return defaults if file doesn't exist"""
        if os.path.exists(self.template_file):
            try:
                with open(self.template_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default templates
        return {
            "Code Explanation": {
                "prompt": "Explain this code in detail:\n```\n{input}\n```",
                "description": "Get a detailed explanation of code",
                "category": "development",
                "created": datetime.now().isoformat()
            },
            "Summarize": {
                "prompt": "Please summarize the following text:\n\n{input}",
                "description": "Create a concise summary of text",
                "category": "writing",
                "created": datetime.now().isoformat()
            },
            "Translate": {
                "prompt": "Translate the following text to {language}:\n\n{input}",
                "description": "Translate text to another language",
                "category": "language",
                "created": datetime.now().isoformat()
            },
            "Pros and Cons": {
                "prompt": "List the pros and cons of {input}",
                "description": "Analyze advantages and disadvantages",
                "category": "analysis",
                "created": datetime.now().isoformat()
            },
            "Writing Assistant": {
                "prompt": "Help me write {input}",
                "description": "Get assistance with writing",
                "category": "writing",
                "created": datetime.now().isoformat()
            },
            "Data Analysis": {
                "prompt": "Analyze this dataset and provide insights:\n\n{input}",
                "description": "Get insights from data",
                "category": "analysis",
                "created": datetime.now().isoformat()
            }
        }
        
    def save_templates(self):
        """Save templates to file"""
        with open(self.template_file, 'w') as f:
            json.dump(self.templates, f, indent=2)
            
    def get_template(self, name):
        """Get template by name"""
        return self.templates.get(name, {}).get("prompt", "")
        
    def add_template(self, name, prompt, description="", category="custom"):
        """Add a new template"""
        self.templates[name] = {
            "prompt": prompt,
            "description": description,
            "category": category,
            "created": datetime.now().isoformat()
        }
        self.save_templates()
        
    def delete_template(self, name):
        """Delete a template by name"""
        if name in self.templates:
            del self.templates[name]
            self.save_templates()
            
    def get_all_templates(self):
        """Get all templates"""
        return self.templates
        
    def get_template_categories(self):
        """Get unique categories from templates"""
        return list(set(template.get("category", "custom") for template in self.templates.values()))
        
    def get_templates_by_category(self, category):
        """Get templates filtered by category"""
        return {name: template for name, template in self.templates.items() 
                if template.get("category", "custom") == category}
