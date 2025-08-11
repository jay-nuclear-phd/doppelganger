from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QGridLayout, QStackedLayout, QFileDialog, QHeaderView, QButtonGroup, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal # Import pyqtSignal

class TopPanel(QWidget):
    # Define signals
    save_data_signal = pyqtSignal()
    reset_simulation_signal = pyqtSignal()

    def __init__(self, sim, default_style, mode_button_style, parent=None):
        super().__init__(parent)
        self.sim = sim
        self.default_style = default_style
        self.mode_button_style = mode_button_style

        self.title = QLabel("TRIGA Doppelganger")
        self.title.setStyleSheet("font-size: 40px; font-weight: bold;")
        
        self.manual_button = QPushButton("Manual")
        self.auto_button = QPushButton("Auto")
        self.powercal_button = QPushButton("Square")
        self.pulse_button = QPushButton("Pulse")
        
        self.manual_button.setMinimumSize(100, 50)
        self.auto_button.setMinimumSize(100, 50)
        self.powercal_button.setMinimumSize(100, 50)
        self.pulse_button.setMinimumSize(100, 50)
        
        self.manual_button.clicked.connect(self.select_manual)
        self.manual_button.setStyleSheet(self.mode_button_style)
        
        self.auto_button.clicked.connect(self.select_auto)
        self.auto_button.setStyleSheet(self.mode_button_style)
        self.powercal_button.setStyleSheet(self.mode_button_style)
        self.powercal_button.clicked.connect(self.toggle_powercal)
        
        self.pulse_button.setStyleSheet(self.mode_button_style)

        self.mode_button_group = QButtonGroup(self)
        self.mode_button_group.setExclusive(True)

        self.manual_button.setCheckable(True)
        self.auto_button.setCheckable(True)
        self.pulse_button.setCheckable(True)

        self.mode_button_group.addButton(self.manual_button)
        self.mode_button_group.addButton(self.auto_button)
        self.mode_button_group.addButton(self.powercal_button)
        self.mode_button_group.addButton(self.pulse_button)
        self.manual_button.setChecked(True)

        mode_grid = QGridLayout()
        mode_grid.addWidget(self.manual_button, 0, 0)
        mode_grid.addWidget(self.auto_button, 0, 1)
        mode_grid.addWidget(self.pulse_button, 1, 0)
        mode_grid.addWidget(self.powercal_button, 1, 1)
        
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

        self.reset_button.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.save_button.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        button_grid = QGridLayout()
        button_grid.addWidget(self.start_button, 0, 0)
        button_grid.addWidget(self.hold_button, 0, 1)
        button_grid.addWidget(self.reset_button, 1, 0)
        button_grid.addWidget(self.save_button, 1, 1)

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

        self.setLayout(top_button_layout)

    def select_manual(self):
        self.sim.mode_selected = "Manual"

    def select_auto(self):
        self.sim.mode_selected = "Auto"

    def start_simulation(self):
        self.sim.running = True

    def hold_simulation(self):
        self.sim.running = False

    def activate_scram(self):
        self.sim.scram_active = True

    def toggle_powercal(self):
        for button in self.mode_button_group.buttons():
            if button is self.powercal_button:
                button.setChecked(True)
            else:
                button.setChecked(False)