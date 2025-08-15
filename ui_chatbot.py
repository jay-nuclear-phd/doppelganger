from PyQt5.QtWidgets import (
    QVBoxLayout, QGroupBox, QLabel, QPushButton, QHBoxLayout, QComboBox
)
from PyQt5.QtCore import Qt

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

        main_layout.addLayout(control_layout)
        main_layout.addStretch() # Pushes the controls to the top

        self.setLayout(main_layout)