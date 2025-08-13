from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QGridLayout, QStackedLayout, QFileDialog, QHeaderView, QButtonGroup, QGroupBox, QLineEdit, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal

class TopPanel(QWidget):
    save_data_signal = pyqtSignal()
    reset_simulation_signal = pyqtSignal()

    def __init__(self, sim, default_style, mode_button_style, parent=None):
        super().__init__(parent)
        self.sim = sim
        self.default_style = default_style
        self.mode_button_style = mode_button_style

        self.applied_speed_value = 1.0 # Initial value
        self.applied_demand_value = 0.0 # Initial value
        self.applied_demand_unit = "W" # Initial value

        self.title = QLabel("TRIGA Doppelganger")
        self.title.setStyleSheet("font-size: 40px; font-weight: bold;")
        
        self.manual_button = QPushButton("Manual")
        self.auto_button = QPushButton("Auto")
        self.square_button = QPushButton("Square")
        self.pulse_button = QPushButton("Pulse")
        
        self.manual_button.setMinimumSize(100, 50)
        self.auto_button.setMinimumSize(100, 50)
        self.square_button.setMinimumSize(100, 50)
        self.pulse_button.setMinimumSize(100, 50)
        
        self.manual_button.clicked.connect(self.select_manual)
        self.manual_button.setStyleSheet(self.mode_button_style)
        
        self.auto_button.clicked.connect(self.select_auto)
        self.auto_button.setStyleSheet(self.mode_button_style)

        self.pulse_button.clicked.connect(self.select_pulse)
        self.pulse_button.setStyleSheet(self.mode_button_style)
        
        self.square_button.clicked.connect(self.select_square)
        self.square_button.setStyleSheet(self.mode_button_style)
                
        self.mode_button_group = QButtonGroup(self)
        self.mode_button_group.setExclusive(True)

        self.manual_button.setCheckable(True)
        self.auto_button.setCheckable(True)
        self.pulse_button.setCheckable(True)
        self.square_button.setCheckable(True)

        self.mode_button_group.addButton(self.manual_button)
        self.mode_button_group.addButton(self.auto_button)
        self.mode_button_group.addButton(self.square_button)
        self.mode_button_group.addButton(self.pulse_button)
        self.manual_button.setChecked(True)

        mode_grid = QGridLayout()
        mode_grid.addWidget(self.manual_button, 0, 0)
        mode_grid.addWidget(self.auto_button, 0, 1)
        mode_grid.addWidget(self.pulse_button, 1, 0)
        mode_grid.addWidget(self.square_button, 1, 1)

        # Light Group
        self.light_on_button = QPushButton("ON")
        self.light_off_button = QPushButton("OFF")

        self.light_on_button.setMinimumSize(70, 50)
        self.light_off_button.setMinimumSize(70, 50)

        self.light_on_button.clicked.connect(self.select_manual) # Placeholder
        self.light_off_button.clicked.connect(self.select_auto) # Placeholder

        self.light_on_button.setStyleSheet(self.mode_button_style)
        self.light_off_button.setStyleSheet(self.mode_button_style)

        self.light_button_group = QButtonGroup(self)
        self.light_button_group.setExclusive(True)

        self.light_on_button.setCheckable(True)
        self.light_off_button.setCheckable(True)

        self.light_button_group.addButton(self.light_on_button)
        self.light_button_group.addButton(self.light_off_button)
        self.light_on_button.setChecked(True) # Default to ON

        light_grid = QGridLayout()
        light_grid.addWidget(self.light_on_button, 0, 0)
        light_grid.addWidget(self.light_off_button, 1, 0)

        # Speed Group
        self.speed_input = QLineEdit()
        self.speed_input.setText("1.0") # Default value
        self.speed_input.setStyleSheet("background-color: white;" + self.default_style)
        self.speed_input.setFixedSize(80, 50) # Fixed width 80, height 50

        self.speed_apply_button = QPushButton("Apply")
        self.speed_apply_button.setStyleSheet(self.default_style)
        self.speed_apply_button.setFixedSize(80, 50) # Fixed height
        self.speed_apply_button.clicked.connect(self.apply_speed) # Connect to a new method

        speed_layout = QVBoxLayout()
        speed_layout.addWidget(self.speed_input)
        speed_layout.addWidget(self.speed_apply_button)

        # Demand Group
        self.demand_input = QLineEdit()
        self.demand_input.setText("0") # Set default value to 0
        self.demand_input.setStyleSheet("background-color: white;" + self.default_style) # Set background to white
        self.demand_input.setFixedSize(50, 50)

        self.demand_unit_combo = QComboBox()
        self.demand_unit_combo.addItems(["W", "kW", "MW"])
        self.demand_unit_combo.setStyleSheet("background-color: white;" + self.default_style) # Set background to white
        self.demand_unit_combo.setFixedSize(70, 50)

        self.demand_apply_button = QPushButton("Apply")
        self.demand_apply_button.setStyleSheet(self.default_style)
        self.demand_apply_button.setFixedHeight(50) # Fixed height at 50
        self.demand_apply_button.clicked.connect(self.apply_demand) # Connect to a new method

        demand_grid = QGridLayout()
        demand_grid.addWidget(self.demand_input, 0, 0)
        demand_grid.addWidget(self.demand_unit_combo, 0, 1)
        demand_grid.addWidget(self.demand_apply_button, 1, 0, 1, 2) # Span two columns

        self.pump_on_button = QPushButton("ON")
        self.pump_off_button = QPushButton("OFF")

        self.pump_on_button.setMinimumSize(70, 50)
        self.pump_off_button.setMinimumSize(70, 50)

        # Connect to dummy functions for now, replace with actual logic later
        self.pump_on_button.clicked.connect(self.select_manual) # Placeholder
        self.pump_off_button.clicked.connect(self.select_auto) # Placeholder

        self.pump_on_button.setStyleSheet(self.mode_button_style)
        self.pump_off_button.setStyleSheet(self.mode_button_style)

        self.pump_button_group = QButtonGroup(self)
        self.pump_button_group.setExclusive(True)

        self.pump_on_button.setCheckable(True)
        self.pump_off_button.setCheckable(True)

        self.pump_button_group.addButton(self.pump_on_button)
        self.pump_button_group.addButton(self.pump_off_button)
        self.pump_on_button.setChecked(True) # Default to ON

        pump_grid = QGridLayout()
        pump_grid.addWidget(self.pump_on_button, 0, 0)
        pump_grid.addWidget(self.pump_off_button, 1, 0)

        self.source_out_button = QPushButton("OUT")
        self.source_in_button = QPushButton("IN")
        
        self.source_out_button.setMinimumSize(70, 50)
        self.source_in_button.setMinimumSize(70, 50)
        
        self.source_out_button.setStyleSheet(self.mode_button_style)
        self.source_in_button.setStyleSheet(self.mode_button_style)
                
        self.source_button_group = QButtonGroup(self)
        self.source_button_group.setExclusive(True)

        self.source_out_button.setCheckable(True)
        self.source_in_button.setCheckable(True)

        self.source_button_group.addButton(self.source_out_button)
        self.source_button_group.addButton(self.source_in_button)
        self.source_out_button.setChecked(True)

        source_grid = QGridLayout()
        source_grid.addWidget(self.source_out_button, 0, 0)
        source_grid.addWidget(self.source_in_button, 1, 0)
        
        self.start_button = QPushButton("Start")
        self.hold_button = QPushButton("Hold")
        self.reset_button = QPushButton("Reset")
        self.save_button = QPushButton("Save")
        
        self.start_button.clicked.connect(self.start_simulation)
        self.hold_button.clicked.connect(self.hold_simulation)
        self.reset_button.clicked.connect(self.reset_simulation_signal.emit) # Emit signal
        self.save_button.clicked.connect(self.save_data_signal.emit) # Emit signal
        
        self.start_button.setMinimumSize(100, 50)
        self.hold_button.setMinimumSize(100, 50)
        self.reset_button.setMinimumSize(100, 50)
        self.save_button.setMinimumSize(100, 50)
        
        self.start_button.setCheckable(True)
        self.start_button.setStyleSheet(self.mode_button_style)
        self.hold_button.setCheckable(True)
        self.hold_button.setStyleSheet(self.mode_button_style)
        
        self.sim_control_button_group = QButtonGroup(self)
        self.sim_control_button_group.setExclusive(True)
        self.sim_control_button_group.addButton(self.start_button)
        self.sim_control_button_group.addButton(self.hold_button)
        self.hold_button.setChecked(True)

        self.reset_button.setStyleSheet(self.default_style)
        self.save_button.setStyleSheet(self.default_style)
        
        button_grid = QGridLayout()
        button_grid.addWidget(self.start_button, 0, 0)
        button_grid.addWidget(self.hold_button, 0, 1)
        button_grid.addWidget(self.reset_button, 1, 0)
        button_grid.addWidget(self.save_button, 1, 1)

        self.scram_button = QPushButton("SCRAM")
        self.scram_button.setStyleSheet("background-color: red; color: white; font-weight: bold; font-size: 40px; border-radius: 15px; box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.5);")
        self.scram_button.setMinimumSize(200, 120)
        self.scram_button.clicked.connect(self.activate_scram)

        source_group = QGroupBox("Source")
        source_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        source_group.setLayout(source_grid)

        pump_group = QGroupBox("Pump")
        pump_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        pump_group.setLayout(pump_grid)

        demand_group = QGroupBox("Demand")
        demand_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        demand_group.setLayout(demand_grid)
        demand_group.setMaximumWidth(150)

        speed_group = QGroupBox("Speed")
        speed_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        speed_group.setLayout(speed_layout)
        speed_group.setMaximumWidth(100) # Limit width to prevent extra space

        light_group = QGroupBox("Light")
        light_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        light_group.setLayout(light_grid)
        light_group.setMaximumWidth(100) # Limit width to prevent extra space

        mode_group = QGroupBox("Mode Selection")
        mode_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        mode_group.setLayout(mode_grid)

        button_group = QGroupBox("Simulation Control")
        button_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        button_group.setLayout(button_grid)
        
        top_button_layout = QHBoxLayout()
        top_button_layout.addWidget(self.title)
        top_button_layout.addStretch()
        
        top_button_layout.addWidget(light_group)
        top_button_layout.addWidget(speed_group)
        top_button_layout.addWidget(demand_group)
        top_button_layout.addWidget(pump_group)
        top_button_layout.addWidget(source_group)
        top_button_layout.addWidget(mode_group)
        top_button_layout.addWidget(button_group)
        top_button_layout.addWidget(self.scram_button)

        self.setLayout(top_button_layout)

    def select_manual(self):
        self.sim.mode_selected = "Manual"

    def select_auto(self):
        self.sim.mode_selected = "Auto"
    
    def select_pulse(self):
        self.sim.mode_selected = "Pulse"
    
    def select_square(self):
        self.sim.mode_selected = "Square"

    def start_simulation(self):
        self.sim.running = True

    def hold_simulation(self):
        self.sim.running = False

    def activate_scram(self):
        self.sim.scram_active = True

    def apply_demand(self):
        try:
            value = float(self.demand_input.text())
            unit = self.demand_unit_combo.currentText()
            self.applied_demand_value = value
            self.applied_demand_unit = unit
            print(f"Demand applied: {self.applied_demand_value} {self.applied_demand_unit}")
        except ValueError:
            print("Invalid demand value entered.")

    def apply_speed(self):
        try:
            value = float(self.speed_input.text())
            self.applied_speed_value = value
            print(f"Speed applied: {self.applied_speed_value}")
        except ValueError:
            print("Invalid speed value entered.")

    def turn_light_on(self):
        print("Light ON button clicked!")

    def turn_light_off(self):
        print("Light OFF button clicked!")

    def get_demand_value(self):
        return self.applied_demand_value

    def get_demand_unit(self):
        return self.applied_demand_unit

    def get_speed_value(self):
        return self.applied_speed_value

    def get_pump_state(self):
        if self.pump_on_button.isChecked():
            return "ON"
        else:
            return "OFF"

    def get_source_state(self):
        if self.source_out_button.isChecked():
            return "OUT"
        else:
            return "IN"

    def get_mode_state(self):
        if self.manual_button.isChecked():
            return "Manual"
        elif self.auto_button.isChecked():
            return "Auto"
        elif self.pulse_button.isChecked():
            return "Pulse"
        elif self.square_button.isChecked():
            return "Square"
        return "Manual" # Default or error case
