from PyQt5.QtWidgets import (
    QVBoxLayout, QGroupBox, QLabel, QPushButton, QHBoxLayout, QComboBox, QTextEdit, QFrame
)
from PyQt5.QtCore import Qt
import re
import html

class ChatbotPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Chatbot", parent)
        # Base stylesheet without font-size, will be controlled by resizeEvent
        self.base_stylesheet = "QGroupBox { font-weight: bold; }"
        self.setStyleSheet(f"font-size: 24px; {self.base_stylesheet}")
        
        main_layout = QVBoxLayout()
        
        # Top control layout
        control_layout = QHBoxLayout()

        # Chatbot type dropdown
        self.chatbot_type_label = QLabel("Chatbot type:")
        self.chatbot_type_label.setStyleSheet("font-weight: normal;")
        self.chatbot_type_combo = QComboBox()
        self.chatbot_type_combo.addItem("--- select chatbot type ---")
        self.chatbot_type_combo.addItems(["Full description", "Step by step"])
        self.chatbot_type_combo.setStyleSheet("font-weight: normal;")
        self.chatbot_type_combo.setFixedHeight(35)

        # Simulator mode dropdown
        self.simulator_mode_label = QLabel("Simulator mode:")
        self.simulator_mode_label.setStyleSheet("font-weight: normal;")
        self.simulator_mode_combo = QComboBox()
        self.simulator_mode_combo.addItem("--- select simulator mode ---")
        self.simulator_mode_combo.addItems(["Manual", "Auto", "Square wave", "Pulse"])
        self.simulator_mode_combo.setStyleSheet("font-weight: normal;")
        self.simulator_mode_combo.setFixedHeight(35)

        # Restart Button
        self.restart_button = QPushButton("Restart")
        self.restart_button_style = """
            font-weight: normal;
            border: 1px solid #999;
            border-radius: 5px;
            padding: 5px;
            background-color: #d3d3d3;
            color: black;
        }
        QPushButton:hover {
            background-color: #b0b0b0;
        }
        QPushButton:pressed {
            background-color: #808080;
            border-style: inset;
        }
        """
        self.restart_button.setStyleSheet(self.restart_button_style)
        self.restart_button.setFixedHeight(35)
        self.restart_button.setFixedWidth(100)

        control_layout.addWidget(self.chatbot_type_label)
        control_layout.addWidget(self.chatbot_type_combo)
        control_layout.addSpacing(20)
        control_layout.addWidget(self.simulator_mode_label)
        control_layout.addWidget(self.simulator_mode_combo)
        control_layout.addStretch()
        control_layout.addWidget(self.restart_button)

        # Text display area
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)

        # Step-by-step controls
        self.step_controls_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.prev_button.setStyleSheet(self.restart_button_style)
        self.prev_button.setFixedHeight(35)
        self.prev_button.setFixedWidth(100)
        self.next_button.setStyleSheet(self.restart_button_style)
        self.next_button.setFixedHeight(35)
        self.next_button.setFixedWidth(100)
        self.step_label = QLabel("")
        self.step_label.setStyleSheet("font-weight: normal;")
        self.step_label.setAlignment(Qt.AlignCenter)

        self.step_controls_layout.addStretch()
        self.step_controls_layout.addWidget(self.prev_button)
        self.step_controls_layout.addWidget(self.step_label)
        self.step_controls_layout.addWidget(self.next_button)
        self.step_controls_layout.addStretch()

        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)

        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.text_display)
        main_layout.addWidget(self.separator)
        main_layout.addLayout(self.step_controls_layout)

        self.setLayout(main_layout)

        self.load_manual()

        self.steps = []
        self.current_step_index = 0
        self.current_simulator_mode = ""

        self.set_step_controls_visible(False)

        self.chatbot_type_combo.currentIndexChanged.connect(self.update_display)
        self.simulator_mode_combo.currentIndexChanged.connect(self.update_display)
        self.prev_button.clicked.connect(self.prev_step)
        self.next_button.clicked.connect(self.next_step)
        self.restart_button.clicked.connect(self.restart_chatbot)
        
        self.display_welcome_message()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        title_font_size = int(self.height() / 20) if self.height() > 50 else 10
        if title_font_size < 10: title_font_size = 10
        
        content_font_size = int(self.height() / 25) if self.height() > 50 else 8
        if content_font_size < 8: content_font_size = 8

        # This single stylesheet will control the font for the groupbox title and all children
        self.setStyleSheet(f"""
            QGroupBox {{ 
                font-size: {title_font_size}px; 
                font-weight: bold; 
            }}
            * {{ 
                font-size: {content_font_size}px; 
            }}
        """)
        # We need to re-apply specific styles that might be overridden by the wildcard
        self.restart_button.setStyleSheet(f"font-size: {content_font_size}px; {self.restart_button_style}")
        self.prev_button.setStyleSheet(f"font-size: {content_font_size}px; {self.restart_button_style}")
        self.next_button.setStyleSheet(f"font-size: {content_font_size}px; {self.restart_button_style}")

        # Force re-display to update HTML content font if necessary
        self.update_display()

    def set_step_controls_visible(self, visible):
        self.prev_button.setVisible(visible)
        self.next_button.setVisible(visible)
        self.step_label.setVisible(visible)
        self.separator.setVisible(visible)

    def load_manual(self):
        try:
            with open('manual_for_chatbot.md', 'r', encoding='utf-8') as f:
                content = f.read()
            self.manual_data = self.parse_manual_content(content)
        except FileNotFoundError:
            self.manual_data = {}
            print("Error: manual_for_chatbot.md not found.")

    def parse_manual_content(self, content):
        sections = {}
        parts = re.split(r'\n(?=\d+\.)', content)
        if parts and not parts[0].strip().startswith("1."):
            parts.pop(0)

        for i, part in enumerate(parts):
            lines = part.strip().split('\n')
            title_line = lines[0]
            body = '\n'.join(lines[1:]).strip()
            
            if "Manual Mode" in title_line:
                sections["Manual"] = body
            elif "Auto Mode" in title_line:
                sections["Auto"] = body
            elif "Square" in title_line and "Wave" in title_line:
                sections["Square wave"] = body
            elif "pulse" in title_line and "mode" in title_line:
                sections["Pulse"] = body
        return sections

    def update_display(self):
        chatbot_type = self.chatbot_type_combo.currentText()
        self.current_simulator_mode = self.simulator_mode_combo.currentText()

        if "---" in self.current_simulator_mode or "---" in chatbot_type:
            self.display_welcome_message()
            self.set_step_controls_visible(False)
            return

        description = self.manual_data.get(self.current_simulator_mode, "Description not found.")
        
        self.text_display.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        if chatbot_type == "Full description":
            self.set_step_controls_visible(False)
            self.display_full_description(description)
        elif chatbot_type == "Step by step":
            self.steps = self.extract_steps(description)
            self.current_step_index = 0
            self.set_step_controls_visible(True)
            self.display_current_step()

    def format_description_to_html(self, description, mode):
        html_content = "<style>td { vertical-align: top; padding-right: 10px; } table { width: 100%; }</style><table>"
        lines = description.split('\n')

        min_indent = -1
        if mode in ["Square wave", "Pulse"]:
            for l in lines:
                if re.match(r'^\s*[_a-zA-Z0-9]+\.', l):
                    current_indent = len(l) - len(l.lstrip())
                    if min_indent == -1 or current_indent < min_indent:
                        min_indent = current_indent

        for line in lines:
            stripped_line = line.lstrip()
            if not stripped_line:
                continue

            if stripped_line.lower().startswith("note:") or stripped_line.lower().startswith("_note:"):
                note_text = stripped_line.replace('_', '')
                html_content += f"<tr><td></td><td><b>{html.escape(note_text)}</b><br/></td></tr>"
                continue

            padding = 0
            if mode in ["Square wave", "Pulse"]:
                indent_level = len(line) - len(line.lstrip())
                base_indent = min_indent if min_indent != -1 else 0
                relative_indent = indent_level - base_indent
                padding = (relative_indent // 4) * 20
                if padding < 0: padding = 0

            match = re.match(r'([_a-zA-Z0-9]+\.)\s(.*)', stripped_line)
            if match:
                number = html.escape(match.group(1))
                text = html.escape(match.group(2))
                html_content += f"<tr><td style='width: 25px; padding-left: {padding}px;'>{number}</td><td>{text}</td></tr>"
            else:
                text = html.escape(stripped_line)
                note_padding = padding + 25
                html_content += f"<tr><td></td><td style='padding-left: {note_padding}px;'><i>{text}</i></td></tr>"

        html_content += "</table>"
        return html_content

    def display_full_description(self, description):
        html = self.format_description_to_html(description, self.current_simulator_mode)
        self.text_display.setHtml(html)

    def extract_steps(self, description):
        lines = description.split('\n')
        steps = [line.lstrip() for line in lines if re.match(r'^\s*[_a-zA-Z0-9]+\.', line.lstrip())]
        return steps

    def display_current_step(self):
        if 0 <= self.current_step_index < len(self.steps):
            step_text = self.steps[self.current_step_index]
            
            padding = 0
            if re.match(r'^\d+\.', step_text):
                padding = 15

            match = re.match(r'([_a-zA-Z0-9]+\.)\s(.*)', step_text)
            if match:
                number = html.escape(match.group(1))
                text = html.escape(match.group(2))
                html_content = "<style>td { vertical-align: top; }</style><table>"
                html_content += f"<tr><td style='width: 25px; padding-left: {padding}px;'>{number}</td><td>{text}</td></tr>"
                html_content += "</table>"
                self.text_display.setHtml(html_content)
            
            self.step_label.setText(f"Step {self.current_step_index + 1} of {len(self.steps)}")
            
            self.prev_button.setEnabled(self.current_step_index > 0)
            self.next_button.setEnabled(self.current_step_index < len(self.steps) - 1)

    def prev_step(self):
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self.display_current_step()

    def next_step(self):
        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1
            self.display_current_step()

    def restart_chatbot(self):
        self.chatbot_type_combo.setCurrentIndex(0)
        self.simulator_mode_combo.setCurrentIndex(0)
        self.display_welcome_message()
        self.set_step_controls_visible(False)
        self.steps = []
        self.current_step_index = 0
        
    def display_welcome_message(self):
        self.text_display.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        welcome_text = """
        This Chatbot provides brief instructions for each mode.
        <br><br>
        If you want to see the full description at once, select <b>Full description</b>.
        <br>
        If you want a step-by-step guide, select <b>Step by step</b>.
        <br><br>
        Please make a selection from the dropdown menus above.
        """
        # The font size will be controlled by the main stylesheet set in resizeEvent
        self.text_display.setHtml(f"<div>{welcome_text}</div>")
