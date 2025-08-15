from PyQt5.QtWidgets import (
    QVBoxLayout, QGroupBox, QLabel
)
from PyQt5.QtCore import Qt

class ChatbotPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Chatbot", parent)
        self.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        chatbot_layout = QVBoxLayout()
        self.chatbot_content = QLabel("Chatbot content will appear here.")
        self.chatbot_content.setAlignment(Qt.AlignCenter)
        
        chatbot_layout.addWidget(self.chatbot_content)
        self.setLayout(chatbot_layout)