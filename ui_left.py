from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QGridLayout, QPushButton, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QColor
from functools import partial
from simulation import ReactorSimulator # Assuming ReactorSimulator is needed here

class ControlRodOverlay(QWidget):
    def __init__(self, rod_names, max_position=960, parent=None):
        super().__init__(parent)
        self.rod_names = rod_names
        self.max_position = max_position
        self.rod_positions = {name: 0 for name in rod_names}
        self.bar_width_ratio = 0.3

    def set_position(self, name, pos):
        self.rod_positions[name] = pos
        self.update()

    def set_bar_width_ratio(self, ratio):
        self.bar_width_ratio = ratio
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        num_rods = len(self.rod_names)
        gap = width // num_rods
        bar_width = int(gap * self.bar_width_ratio)
        
        half_height = height // 2
        
        for i, name in enumerate(self.rod_names):
            pos = self.rod_positions[name]
            h = int((1 - pos / self.max_position) * half_height)

            x = gap * i + (gap - bar_width) // 2
            y = 0

            painter.setBrush(QColor("gray"))
            painter.setPen(Qt.NoPen)
            painter.drawRect(x, y, bar_width, h)

            green_y = y + h
            painter.setBrush(QColor("green"))
            painter.drawRect(x, green_y, bar_width, half_height)

class LeftPanel(QWidget):
    def __init__(self, sim, parent=None):
        super().__init__(parent)
        self.sim = sim

        self.media_label = QLabel()
        self.media_label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap("images.jpg")
        self.media_label.setPixmap(pixmap)
        self.media_label.setScaledContents(True)

        background = QWidget()
        background_layout = QVBoxLayout(background)
        background_layout.setContentsMargins(0, 0, 0, 0)

        blue_frame = QFrame()
        blue_frame.setStyleSheet("background-color: blue;")
        blue_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        red_frame = QFrame()
        red_frame.setStyleSheet("background-color: red;")
        red_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        background_layout.addWidget(blue_frame, stretch=9)
        background_layout.addWidget(red_frame, stretch=11)
        background_layout.setSpacing(0)

        self.rod_overlay = ControlRodOverlay(self.sim.rod_names, self.sim.max_position)
        self.rod_overlay.set_bar_width_ratio(0.4)
        self.rod_overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.rod_overlay.setStyleSheet("background-color: transparent;")
        self.rod_overlay.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        stack_widget = QWidget()
        stack_layout = QVBoxLayout(stack_widget)
        stack_layout.setContentsMargins(0, 0, 0, 0)
        stack_layout.setSpacing(0)
        stack_layout.addWidget(background)
        self.rod_overlay.setParent(stack_widget)
        self.rod_overlay.raise_()

        rect_widget = QWidget()
        rect_layout = QVBoxLayout(rect_widget)
        rect_layout.setContentsMargins(0, 0, 0, 0)
        rect_layout.setSpacing(0)
        rect_layout.addWidget(stack_widget)
        
        control_grid = QGridLayout()
        self.rod_labels = {}
        for i, name in enumerate(self.sim.rod_names):
            label = QLabel(f"0.0")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 18px; font-weight: bold;")
            self.rod_labels[name] = label
            up_btn = QPushButton(f"▲ {name}")
            down_btn = QPushButton(f"▼ {name}")
            up_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
            down_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
            up_btn.setMinimumSize(120, 50)
            down_btn.setMinimumSize(120, 50)
            up_btn.setAutoRepeat(True)
            down_btn.setAutoRepeat(True)
            up_btn.setAutoRepeatInterval(10)
            down_btn.setAutoRepeatInterval(10)
            up_btn.pressed.connect(partial(self.set_button_state, name+"_up", True))
            down_btn.pressed.connect(partial(self.set_button_state, name+"_down", True))
            up_btn.released.connect(partial(self.set_button_state, name+"_up", False))
            down_btn.released.connect(partial(self.set_button_state, name+"_down", False))
            control_grid.addWidget(label, 0, i)
            control_grid.addWidget(up_btn, 1, i)
            control_grid.addWidget(down_btn, 2, i)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.media_label, 4)
        left_layout.addWidget(rect_widget, 4)
        left_layout.addLayout(control_grid, 2)
        
        self.setLayout(left_layout)

    def set_button_state(self, name, state):
        self.sim.pressed_state[name] = state
