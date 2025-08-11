from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QGridLayout, QPushButton, QFrame, QSizePolicy, QLayout
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
        
        # Define the proportions
        proportions = [7, 8, 10, 8, 10, 8, 10, 8, 7]
        total_proportional_units = sum(proportions)
        
        unit_width = width / total_proportional_units
        
        # Calculate x positions and widths for each rod
        rod_data = [] # List of (x, bar_width) for each rod
        current_x = 0
        
        # Skip first empty space
        current_x += proportions[0] * unit_width 
        
        # Rod 1
        rod_width = proportions[1] * unit_width
        rod_data.append((current_x, rod_width))
        current_x += rod_width
        
        # Skip empty space 2
        current_x += proportions[2] * unit_width
        
        # Rod 2
        rod_width = proportions[3] * unit_width
        rod_data.append((current_x, rod_width))
        current_x += rod_width
        
        # Skip empty space 3
        current_x += proportions[4] * unit_width
        
        # Rod 3
        rod_width = proportions[5] * unit_width
        rod_data.append((current_x, rod_width))
        current_x += rod_width
        
        # Skip empty space 4
        current_x += proportions[6] * unit_width
        
        # Rod 4
        rod_width = proportions[7] * unit_width
        rod_data.append((current_x, rod_width))
        current_x += rod_width
        
        half_height = height // 2
        
        for i, name in enumerate(self.rod_names):
            pos = self.rod_positions[name]
            h = int((1 - pos / self.max_position) * half_height)

            x, bar_width = rod_data[i]
            x = int(x)
            bar_width = int(bar_width)
            y = 0

            painter.setBrush(QColor("gray"))
            painter.setPen(Qt.NoPen)
            painter.drawRect(x, y, bar_width, h)

            green_y = y + h
            
            yellow_height = int(0.1 * half_height)
            green_remaining_height = half_height - yellow_height

            # Draw the yellow part
            painter.setBrush(QColor("yellow"))
            painter.drawRect(x, green_y, bar_width, yellow_height)

            # Draw the remaining green part
            painter.setBrush(QColor("green"))
            painter.drawRect(x, green_y + yellow_height, bar_width, green_remaining_height)

class OverlayContainer(QWidget):
    def __init__(self, background_widget, overlay_widget, parent=None):
        super().__init__(parent)
        self.background_widget = background_widget
        self.overlay_widget = overlay_widget

        # Set up a layout for the background widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.background_widget)

        # Set the overlay widget as a child and raise it
        self.overlay_widget.setParent(self)
        self.overlay_widget.raise_()

    def resizeEvent(self, event):
        # Ensure the overlay widget matches the size of this container
        self.overlay_widget.setGeometry(self.rect())
        super().resizeEvent(event)

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
        background_layout.addWidget(blue_frame, stretch=11)
        background_layout.addWidget(red_frame, stretch=9)
        background_layout.setSpacing(0)

        self.rod_overlay = ControlRodOverlay(self.sim.rod_names, self.sim.max_position)
        self.rod_overlay.set_bar_width_ratio(0.4)
        self.rod_overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.rod_overlay.setStyleSheet("background-color: transparent;")
        self.rod_overlay.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        stack_container_widget = OverlayContainer(background, self.rod_overlay)

        rect_widget = QWidget()
        rect_layout = QVBoxLayout(rect_widget)
        rect_layout.setContentsMargins(0, 0, 0, 0)
        rect_layout.setSpacing(0)
        rect_layout.addWidget(stack_container_widget)
        
        control_grid = QGridLayout()
        rod_names_order = ["Tran", "Shim1", "Shim2", "Reg"] # Explicit order for columns
        key_map_up = {"Tran": "q", "Shim1": "w", "Shim2": "e", "Reg": "r"}
        key_map_down = {"Tran": "a", "Shim1": "s", "Shim2": "d", "Reg": "f"}
        air_magnet_texts = ["AIR", "MAGNET", "MAGNET", "MAGNET"]

        # Row 0: Headers
        for i, name in enumerate(rod_names_order):
            header_label = QLabel(name)
            header_label.setAlignment(Qt.AlignCenter)
            header_label.setStyleSheet("font-size: 16px; font-weight: bold;") # Adjust font size as needed
            control_grid.addWidget(header_label, 0, i)

        # Row 1: AIR/MAGNET buttons
        for i, text in enumerate(air_magnet_texts):
            btn = QPushButton(text)
            btn.setStyleSheet("font-size: 14px; font-weight: bold;") # Adjust font size as needed
            btn.setMinimumSize(120, 50) # Match existing button size
            # No connect for now
            control_grid.addWidget(btn, 1, i)

        # Rows 2 & 3: Up/Down buttons
        for i, name in enumerate(rod_names_order):
            up_btn = QPushButton(f"▲ ({key_map_up[name]})")
            down_btn = QPushButton(f"▼ ({key_map_down[name]})")
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
            control_grid.addWidget(up_btn, 2, i)
            control_grid.addWidget(down_btn, 3, i)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.media_label, 4)
        left_layout.addWidget(rect_widget, 4)
        left_layout.addLayout(control_grid, 2)
        
        self.setLayout(left_layout)

    def set_button_state(self, name, state):
        self.sim.pressed_state[name] = state
