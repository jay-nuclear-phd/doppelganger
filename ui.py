import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QFrame, QSizePolicy, QGroupBox,
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QGridLayout, QStackedLayout
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor
from simulation import ReactorSimulator

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

class ReactorSimulatorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NETL TRIGA Reactor Simulator ver.1.3")

        self.sim = ReactorSimulator()

        self.rod_keymap = {
            Qt.Key_Q: ("Tran", "_up"), Qt.Key_A: ("Tran", "_down"),
            Qt.Key_W: ("Shim1", "_up"), Qt.Key_S: ("Shim1", "_down"),
            Qt.Key_E: ("Shim2", "_up"), Qt.Key_D: ("Shim2", "_down"),
            Qt.Key_R: ("Reg", "_up"), Qt.Key_F: ("Reg", "_down")
        }

        self.init_ui()

        self.log_file = open("keff_log.csv", "w", newline="")
        self.logger = csv.writer(self.log_file)
        self.logger.writerow(["time", "keff", "rho", "T", "power"] + self.sim.rod_names)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(100)

    def init_ui(self):
        self.title = QLabel("TRIGA Doppelganger")
        self.title.setStyleSheet("font-size: 40px; font-weight: bold;")
        
        self.manual_button = QPushButton("Manual")
        self.auto_button = QPushButton("Auto")
        self.powercal_button = QPushButton("Wtr Circ")
        self.pulse_button = QPushButton("Pulse")
        
        self.manual_button.setMinimumSize(120, 50)
        self.auto_button.setMinimumSize(120, 50)
        self.powercal_button.setMinimumSize(120, 50)
        self.pulse_button.setMinimumSize(120, 50)
        
        self.default_style = """
            font-size: 18px;
            font-weight: bold;
            border: 2px solid #999;
            border-radius: 5px;
            padding: 5px;
        """
        self.selected_style = self.default_style + "background-color: lightgreen;"
        self.powercal_on_style = self.default_style + "background-color: blue;"
        self.pulse_active_style = self.default_style + "background-color: red;"

        self.manual_button.clicked.connect(self.select_manual)
        self.manual_button.setStyleSheet(self.selected_style)
        
        self.auto_button.clicked.connect(self.select_auto)
        self.auto_button.setStyleSheet(self.default_style)
        
        self.powercal_button.setCheckable(True)
        self.powercal_button.setStyleSheet(self.default_style)
        self.powercal_button.clicked.connect(self.toggle_powercal)
        
        self.pulse_button.pressed.connect(self.pulse_pressed)
        self.pulse_button.setStyleSheet(self.default_style)
        self.pulse_button.released.connect(self.pulse_released)
        
        mode_grid = QGridLayout()
        mode_grid.addWidget(self.manual_button, 0, 0)
        mode_grid.addWidget(self.auto_button, 0, 1)
        mode_grid.addWidget(self.pulse_button, 1, 0)
        mode_grid.addWidget(self.powercal_button, 1, 1)
        
        self.start_button = QPushButton("Start")
        self.hold_button = QPushButton("Hold")
        self.reset_button = QPushButton("Reset")
        self.quit_button = QPushButton("Quit")
        
        self.start_button.clicked.connect(self.start_simulation)
        self.hold_button.clicked.connect(self.hold_simulation)
        self.reset_button.clicked.connect(self.reset_simulation)
        self.quit_button.clicked.connect(QApplication.quit)
        self.start_button.setMinimumSize(120, 50)
        self.hold_button.setMinimumSize(120, 50)
        self.reset_button.setMinimumSize(120, 50)
        self.quit_button.setMinimumSize(120, 50)
        self.start_button.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.hold_button.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.reset_button.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.quit_button.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        button_grid = QGridLayout()
        button_grid.addWidget(self.start_button, 0, 0)
        button_grid.addWidget(self.hold_button, 0, 1)
        button_grid.addWidget(self.reset_button, 1, 0)
        button_grid.addWidget(self.quit_button, 1, 1)

        self.scram_button = QPushButton("SCRAM")
        self.scram_button.setStyleSheet("background-color: red; color: white; font-weight: bold; font-size: 40px;")
        self.scram_button.setMinimumSize(300, 100)
        self.scram_button.clicked.connect(self.activate_scram)

        mode_group = QGroupBox("Mode Selection")
        mode_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        mode_group.setLayout(mode_grid)

        button_group = QGroupBox("Simulation Control")
        button_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        button_group.setLayout(button_grid)
        
        top_button_layout = QHBoxLayout()
        top_button_layout.addWidget(self.title)
        top_button_layout.addStretch()
        
        top_button_layout.addWidget(mode_group)
        top_button_layout.addWidget(button_group)
        top_button_layout.addWidget(self.scram_button)

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
        from functools import partial
        for i, name in enumerate(self.sim.rod_names):
            label = QLabel(f"0.0")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 18px; font-weight: bold;")
            self.rod_labels[name] = label
            up_btn = QPushButton(f"▲ {name}")
            down_btn = QPushButton(f"▼ {name}")
            up_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
            down_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
            up_btn.setMinimumSize(140, 50)
            down_btn.setMinimumSize(140, 50)
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
        
            
        self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.tight_layout()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.ax_keff = self.axes[0, 0]
        self.ax_power = self.axes[0, 1]
        self.ax_rod = self.axes[1, 0]
        self.ax_temp = self.axes[1, 1]

        self.line_keff, = self.ax_keff.plot([], [], label='keff', color='blue')
        self.ax_keff.axhline(1.0, color='red', linestyle='--', linewidth=1, alpha=0.5)
        self.ax_keff.set_ylim(0.95, 1.10)
        self.ax_keff.set_ylabel('keff')
        self.ax_keff.set_xlabel('Time (s)')
        self.ax_keff.grid(True)
        self.ax_keff.legend()
        
        self.line_power, = self.ax_power.plot([], [], label='Power', color='orange')
        self.ax_power.set_xlabel('Time (s)')
        self.ax_power.set_ylim(1e-5, 2.5e7)
        self.ax_power.set_yscale('log')
        self.ax_power.grid(True, which='both', linestyle='--', linewidth=0.5)
        self.ax_power.yaxis.set_major_locator(LogLocator(base=10.0, subs=(1.0,), numticks=10))
        self.ax_power.legend()
        tick_values = [1e-3, 1, 1e3, 1e6]
        tick_labels = ['mW', 'W', 'kW', 'MW']
        for y, label in zip(tick_values, tick_labels):
            self.ax_power.axhline(y, color='gray', linestyle='--', linewidth=1, alpha=0.5)
            self.ax_power.annotate(
                label,
                xy=(0.01, y * 0.95),
                xycoords=('axes fraction', 'data'),
                fontsize=9,
                color='gray',
                ha='left',
                va='top'
            )

        self.line_temp, = self.ax_temp.plot([], [], label='Temperature', color='green')
        self.ax_temp.set_xlabel('Time (s)')
        self.ax_temp.set_ylim(0, 400)
        self.ax_temp.grid(True)
        self.ax_temp.legend()

        self.rod_lines = {}
        self.ax_rod.set_ylim(self.sim.min_position - 40, self.sim.max_position + 40)
        self.ax_rod.set_ylabel('Rod Position')
        self.ax_rod.set_xlabel('Time (s)')
        self.ax_rod.grid(True)
        for name in self.sim.rod_names:
            line, = self.ax_rod.plot([], [], label=name)
            self.rod_lines[name] = line
        self.ax_rod.legend()
        
        right_column = QVBoxLayout()
        
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.addWidget(self.canvas)
        
        chat_status_container = QWidget()
        chat_status_layout = QHBoxLayout(chat_status_container)
        chat_status_layout.setContentsMargins(0, 0, 0, 0)

        simulator_status_label = QLabel("Simulator Status")
        simulator_status_label.setAlignment(Qt.AlignCenter)
        simulator_status_label.setStyleSheet("""
            background-color: #eeeeee;
            font-size: 20px;
            font-weight: bold;
            border: 1px solid #ccc;
            padding: 10px;
        """)
        chat_status_layout.addWidget(simulator_status_label, 3)

        chatbot_label = QLabel("Chatbot")
        chatbot_label.setAlignment(Qt.AlignCenter)
        chatbot_label.setStyleSheet("""
            background-color: #eeeeee;
            font-size: 24px;
            font-weight: bold;
            border: 1px solid #ccc;
            padding: 20px;
        """)
        chat_status_layout.addWidget(chatbot_label, 7)
        
        
        right_column.addWidget(chat_status_container, 4)
        right_column.addWidget(canvas_container, 6)
        
        layout = QGridLayout()
        layout.addLayout(top_button_layout, 0, 0, 1, 2)
        layout.addLayout(right_column, 1, 1, 2, 1)
        layout.addLayout(left_layout, 1, 0, 2, 1)
        layout.addLayout(control_grid, 1, 0, 2, 1)
        self.setLayout(layout)

    def keyPressEvent(self, event):
        if event.key() in self.rod_keymap:
            rod, direction = self.rod_keymap[event.key()]
            self.sim.pressed_state[rod + direction] = True

    def keyReleaseEvent(self, event):
        if event.key() in self.rod_keymap:
            rod, direction = self.rod_keymap[event.key()]
            self.sim.pressed_state[rod + direction] = False

    def set_button_state(self, name, state):
        self.sim.pressed_state[name] = state

    def activate_scram(self):
        self.sim.scram_active = True

    def start_simulation(self):
        self.sim.running = True

    def hold_simulation(self):
        self.sim.running = False

    def reset_simulation(self):
        self.sim.reset_simulation()
        self.line_keff.set_data([], [])
        self.line_power.set_data([], [])
        self.line_temp.set_data([], [])
        for name in self.sim.rod_names:
            self.rod_lines[name].set_data([], [])
        self.canvas.draw()

    def select_manual(self):
        self.mode_selected = "Manual"
        self.manual_button.setStyleSheet(self.selected_style)
        self.auto_button.setStyleSheet(self.default_style)

    def select_auto(self):
        self.mode_selected = "Auto"
        self.auto_button.setStyleSheet(self.selected_style)
        self.manual_button.setStyleSheet(self.default_style)

    def pulse_pressed(self):
        self.pulse_button.setStyleSheet(self.pulse_active_style)

    def pulse_released(self):
        self.pulse_button.setStyleSheet(self.default_style)

    def toggle_powercal(self):
        if self.powercal_button.isChecked():
            self.powercal_button.setStyleSheet(self.powercal_on_style)
        else:
            self.powercal_button.setStyleSheet(self.default_style)

    def format_power_with_unit(self, power_value):
        if power_value < 1e-3:
            return f"{power_value * 1e3:.3f} mW"
        elif power_value < 1:
            return f"{power_value:.3f} W"
        elif power_value < 1e3:
            return f"{power_value:.3f} W"
        elif power_value < 1e6:
            return f"{power_value / 1e3:.3f} kW"
        else:
            return f"{power_value / 1e6:.3f} MW"
        
    def update_gui(self):
        self.sim.update_simulation(0.1)

        self.line_keff.set_data(self.sim.time_history, self.sim.keff_history)
        if hasattr(self, 'keff_text') and self.keff_text:
            self.keff_text.remove()
        self.keff_text = self.ax_keff.annotate(
            f"{self.sim.keff:.5f}",
            xy=(self.sim.current_time, self.sim.keff),  
            xytext=(-50, 5),  
            textcoords='offset points',
            fontsize=10,
            color='blue',
            ha='left',
            va='bottom',
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.7)
        )
        
        self.line_power.set_data(self.sim.time_history, self.sim.power_history)
        if hasattr(self, 'power_text') and self.power_text:
            self.power_text.remove()
        formatted_power = self.format_power_with_unit(self.sim.power)
        self.power_text = self.ax_power.annotate(
            formatted_power,
            xy=(self.sim.current_time, self.sim.power),
            xytext=(-70, 0),
            textcoords='offset points',
            fontsize=10,
            color='darkorange',
            ha='left',
            va='bottom',
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.7)
        )
        
        self.line_temp.set_data(self.sim.time_history, self.sim.temp_history)
        for ax in [self.ax_keff, self.ax_power, self.ax_rod, self.ax_temp]:
            ax.set_xlim(self.sim.current_time - 10, self.sim.current_time)
        
        for name in self.sim.rod_names:
            self.rod_data = {name: [] for name in self.sim.rod_names}
            self.rod_data[name].append(self.sim.rod_positions[name])
            self.rod_lines[name].set_data(self.sim.time_history, self.sim.rod_data[name])

        self.canvas.draw()

        self.logger.writerow([self.sim.current_time, self.sim.keff, (self.sim.keff - 1) / self.sim.keff * 100 / 0.007, self.sim.temperature, self.sim.power] + [self.sim.rod_positions[name] for name in self.sim.rod_names])

        for name in self.sim.rod_names:
            self.rod_labels[name].setText(f"{int(self.sim.rod_positions[name])}")
            self.rod_overlay.set_position(name, self.sim.rod_positions[name])
