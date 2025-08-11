from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QGridLayout, QStackedLayout, QFileDialog, QHeaderView, QButtonGroup, QGroupBox
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

        self.source_out_button = QPushButton("OUT")
        self.source_in_button = QPushButton("IN")
        
        self.source_out_button.setMinimumSize(70, 50)
        self.source_in_button.setMinimumSize(70, 50)
        
        self.source_out_button.clicked.connect(self.select_manual)
        self.source_out_button.setStyleSheet(self.mode_button_style)
        
        self.source_in_button.clicked.connect(self.select_auto)
        self.source_in_button.setStyleSheet(self.mode_button_style)
                
        self.mode_button_group = QButtonGroup(self)
        self.mode_button_group.setExclusive(True)

        self.source_out_button.setCheckable(True)
        self.source_in_button.setCheckable(True)

        self.mode_button_group.addButton(self.source_out_button)
        self.mode_button_group.addButton(self.source_in_button)
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
        self.scram_button.setStyleSheet("background-color: red; color: white; font-weight: bold; font-size: 40px;")
        self.scram_button.setMinimumSize(300, 100)
        self.scram_button.clicked.connect(self.activate_scram)

        source_group = QGroupBox("Source")
        source_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        source_group.setLayout(source_grid)

        mode_group = QGroupBox("Mode Selection")
        mode_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        mode_group.setLayout(mode_grid)

        button_group = QGroupBox("Simulation Control")
        button_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        button_group.setLayout(button_grid)
        
        top_button_layout = QHBoxLayout()
        top_button_layout.addWidget(self.title)
        top_button_layout.addStretch()
        
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
