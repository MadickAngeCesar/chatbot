def get_sidebar_button_style(selected=False):
    base_style = """
        QPushButton {
            background-color: %(bg_color)s;
            color: %(text_color)s;
            border: none;
            border-radius: 5px;
            padding: 10px;
            text-align: left;
            %(extra_style)s
        }
    """
    
    if selected:
        return base_style % {
            'bg_color': '#3f3f3f',
            'text_color': 'white',
            'extra_style': 'font-weight: bold;'
        }
    else:
        return base_style % {
            'bg_color': 'transparent',
            'text_color': '#bbbbbb',
            'extra_style': '''
            }
            QPushButton:hover {
                background-color: #3f3f3f;
                color: white;
            }'''
        }

def get_combo_style():
    return """
        QComboBox {
            background-color: #3f3f3f;
            color: white;
            border: 1px solid #555555;
            border-radius: 5px;
            padding: 5px;
            min-width: 150px;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox QAbstractItemView {
            background-color: #3f3f3f;
            color: white;
            selection-background-color: #4CAF50;
        }
    """

def get_button_style(color):
    return f"""
        QPushButton {{
            background-color: {color};
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 15px;
        }}
        QPushButton:hover {{
            background-color: {color}dd;
        }}
    """
