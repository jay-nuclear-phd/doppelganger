import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QFrame, QSizePolicy, QGroupBox,
    QApplication, QWidget, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QGridLayout, QStackedLayout, QFileDialog, QHeaderView, QButtonGroup
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor
from simulation import ReactorSimulator

# Import the new UI components
from ui_top import TopPanel
from ui_left import LeftPanel
from ui_right import RightPanel

class ReactorSimulatorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NETL TRIGA Reactor Simulator ver.1.3")
        self.setStyleSheet("background-color: white;")

        self.sim = ReactorSimulator()

        self.rod_keymap = {
            Qt.Key_Q: ("Tran", "_up"), Qt.Key_A: ("Tran", "_down"),
            Qt.Key_W: ("Shim1", "_up"), Qt.Key_S: ("Shim1", "_down"),
            Qt.Key_E: ("Shim2", "_up"), Qt.Key_D: ("Shim2", "_down"),
            Qt.Key_R: ("Reg", "_up"), Qt.Key_F: ("Reg", "_down")
        }

        self.init_ui()

        # CSV logging modification
        self.log_data = []
        self.log_data.append(["time", "rho", "temperature", "power"] + self.sim.rod_names)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(50)

    def init_ui(self):
        # Define common styles here, or pass them to sub-panels
        self.default_style = """
            font-size: 18px;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            padding: 5px;
            background-color: #d3d3d3;
            color: black;
        }
        QPushButton:hover {
            background-color: #b0b0b0;
        }
        """
        self.mode_button_style = """
            font-size: 18px;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            padding: 5px;
            background-color: #d3d3d3; /* Default background */
            color: black; /* Default text color */
        }
        QPushButton:hover {
            background-color: #b0b0b0; /* Hover effect */
        }
        QPushButton:checked {
            background-color: #BF5700; /* Background when checked */
            color: white; /* Text color when checked */
        }
        QPushButton:pressed {
            background-color: #808080; /* Darker gray when pressed */
            border-style: inset; /* Visual effect for pressed */
        }
        """

        self.top_panel = TopPanel(self.sim, self.default_style, self.mode_button_style)
        self.left_panel = LeftPanel(self.sim, self.mode_button_style)
        self.right_panel = RightPanel(self.sim, self.top_panel)

        # Connect signals from TopPanel
        self.top_panel.save_data_signal.connect(self.save_data)
        self.top_panel.reset_simulation_signal.connect(self.reset_simulation)

        layout = QGridLayout()
        layout.addWidget(self.top_panel, 0, 0, 1, 2) # Top panel spans 2 columns
        layout.addWidget(self.left_panel, 1, 0)
        layout.addWidget(self.right_panel, 1, 1)
        
        self.setLayout(layout)
        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 7)

    def keyPressEvent(self, event):
        if event.key() in self.rod_keymap:
            rod, direction = self.rod_keymap[event.key()]
            self.sim.pressed_state[rod + direction] = True
            # Update rod overlay in LeftPanel
            self.left_panel.rod_overlay.set_position(rod, 960 - self.sim.rod_positions[rod])

            # Programmatically press the button for visual feedback
            key_char = chr(event.key()).lower()
            if key_char in self.left_panel.control_buttons:
                self.left_panel.control_buttons[key_char].setDown(True)


    def keyReleaseEvent(self, event):
        if event.key() in self.rod_keymap:
            rod, direction = self.rod_keymap[event.key()]
            self.sim.pressed_state[rod + direction] = False

            # Programmatically release the button for visual feedback
            key_char = chr(event.key()).lower()
            if key_char in self.left_panel.control_buttons:
                self.left_panel.control_buttons[key_char].setDown(False)

    def update_gui(self):
        source_state = self.top_panel.get_source_state()
        self.sim.update_simulation(0.05, source_state)
        self.right_panel.update_plots(self.sim)
        
        # Get demand value and unit from TopPanel
        demand_value = self.top_panel.get_demand_value()
        demand_unit = self.top_panel.get_demand_unit()
        speed_value = self.top_panel.get_speed_value()
        pump_state = self.top_panel.get_pump_state()
        source_state = self.top_panel.get_source_state()
        mode_state = self.top_panel.get_mode_state()
        self.right_panel.update_status_table(self.sim, demand_value, demand_unit, speed_value, pump_state, source_state, mode_state)
        
        # Update rod labels in LeftPanel
        for name in self.sim.rod_names:
            self.left_panel.rod_overlay.set_position(name, 960 - self.sim.rod_positions[name])

        # CSV logging modification
        if self.sim.running: # Only log if simulation is running
            self.log_data.append([self.sim.current_time, self.sim.total_rho, self.sim.temperature, self.sim.power] + [self.sim.rod_positions[name] for name in self.sim.rod_names])

    def save_data(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Log File", "triga_doppelganger_log.csv", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(self.log_data)
            print(f"Data saved to {file_path}")

    def reset_simulation(self):
        self.sim.reset_simulation()
        # Reset plots in RightPanel
        self.right_panel.line_rho.set_data([], [])
        self.right_panel.line_power.set_data([], [])
        self.right_panel.line_F_Temp1.set_data([], [])
        self.right_panel.line_F_Temp2.set_data([], [])
        for name in self.sim.rod_names:
            self.right_panel.rod_lines[name].set_data([], [])
        self.right_panel.canvas.draw()

        # Clear log data and re-add header
        self.log_data.clear()
        self.log_data.append(["time", "rho", "temperature", "power"] + self.sim.rod_names)
