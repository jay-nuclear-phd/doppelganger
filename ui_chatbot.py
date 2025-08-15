from PyQt5.QtWidgets import (
    QVBoxLayout, QGroupBox, QLabel, QPushButton, QHBoxLayout, QComboBox, QTextEdit, QFrame
)
from PyQt5.QtCore import Qt
import re
import html

class ChatbotPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Chatbot", parent)
        self.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        main_layout = QVBoxLayout()
        
        # Top control layout
        control_layout = QHBoxLayout()

        # Chatbot type dropdown
        self.chatbot_type_label = QLabel("Chatbot type:")
        self.chatbot_type_label.setStyleSheet("font-size: 16px; font-weight: normal;")
        self.chatbot_type_combo = QComboBox()
        self.chatbot_type_combo.addItem("--- select chatbot type ---")
        self.chatbot_type_combo.addItems(["Full description", "Step by step"])
        self.chatbot_type_combo.setStyleSheet("font-size: 16px; font-weight: normal;")
        self.chatbot_type_combo.setFixedHeight(35)

        # Simulator mode dropdown
        self.simulator_mode_label = QLabel("Simulator mode:")
        self.simulator_mode_label.setStyleSheet("font-size: 16px; font-weight: normal;")
        self.simulator_mode_combo = QComboBox()
        self.simulator_mode_combo.addItem("--- select simulator mode ---")
        self.simulator_mode_combo.addItems(["Manual", "Auto", "Square wave", "Pulse"])
        self.simulator_mode_combo.setStyleSheet("font-size: 16px; font-weight: normal;")
        self.simulator_mode_combo.setFixedHeight(35)

        # Restart Button
        self.restart_button = QPushButton("Restart")
        restart_button_style = """
            font-size: 16px;
            font-weight: normal;
            border: 1px solid #999; /* Match combobox border */
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
        self.restart_button.setStyleSheet(restart_button_style)
        self.restart_button.setFixedHeight(35)
        self.restart_button.setFixedWidth(100)

        control_layout.addWidget(self.chatbot_type_label)
        control_layout.addWidget(self.chatbot_type_combo)
        control_layout.addSpacing(20) # Add some space
        control_layout.addWidget(self.simulator_mode_label)
        control_layout.addWidget(self.simulator_mode_combo)
        control_layout.addStretch() # Pushes restart button to the right
        control_layout.addWidget(self.restart_button)

        # Text display area
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setStyleSheet("font-size: 16px; font-weight: normal;")

        # Step-by-step controls
        self.step_controls_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.step_label = QLabel("")
        self.step_label.setStyleSheet("font-size: 16px; font-weight: normal;")
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

        # Load and parse manual
        self.load_manual()

        # State variables for step-by-step
        self.steps = []
        self.current_step_index = 0

        # Hide step controls initially
        self.set_step_controls_visible(False)

        # Connect signals
        self.chatbot_type_combo.currentIndexChanged.connect(self.update_display)
        self.simulator_mode_combo.currentIndexChanged.connect(self.update_display)
        self.prev_button.clicked.connect(self.prev_step)
        self.next_button.clicked.connect(self.next_step)
        self.restart_button.clicked.connect(self.restart_chatbot)

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
        simulator_mode = self.simulator_mode_combo.currentText()

        if "---" in simulator_mode or "---" in chatbot_type:
            self.text_display.clear()
            self.set_step_controls_visible(False)
            return

        description = self.manual_data.get(simulator_mode, "Description not found.")
        
        if chatbot_type == "Full description":
            self.set_step_controls_visible(False)
            self.display_full_description(description)
        elif chatbot_type == "Step by step":
            self.steps = self.extract_steps(description)
            self.current_step_index = 0
            self.set_step_controls_visible(True)
            self.display_current_step()

    def format_description_to_html(self, description):
        html_content = "<style>td { vertical-align: top; padding-right: 10px; } table { width: 100%; }</style><table>"
        lines = description.split('\n')
        
        for line in lines:
            indent_level = (len(line) - len(line.lstrip(' '))) // 4
            stripped_line = line.lstrip()
            if not stripped_line:
                continue

            padding = indent_level * 20

            match = re.match(r'([_a-zA-Z0-9]+\.)\s*(.*)', stripped_line)
            if match:
                number = html.escape(match.group(1))
                text = html.escape(match.group(2))
                html_content += f"<tr><td style='width: 40px; padding-left: {padding}px;'>{number}</td><td>{text}</td></tr>"
            else:
                text = html.escape(stripped_line)
                note_padding = padding + 40
                html_content += f"<tr><td></td><td style='padding-left: {note_padding}px;'><i>{text}</i></td></tr>"

        html_content += "</table>"
        return html_content

    def display_full_description(self, description):
        html = self.format_description_to_html(description)
        self.text_display.setHtml(html)

    def extract_steps(self, description):
        lines = description.split('\n')
        steps = [line.lstrip() for line in lines if re.match(r'^\s*[_a-zA-Z0-9]+\.', line.lstrip())]
        return steps

    def display_current_step(self):
        if 0 <= self.current_step_index < len(self.steps):
            step_text = self.steps[self.current_step_index]
            html = self.format_description_to_html(step_text)
            self.text_display.setHtml(html)
            
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
        self.text_display.clear()
        self.set_step_controls_visible(False)
        self.steps = []
        self.current_step_index = 0