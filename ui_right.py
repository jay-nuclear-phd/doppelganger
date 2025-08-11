from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QSizePolicy, QHeaderView # Added for table
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class RightPanel(QWidget):
    def __init__(self, sim, top_panel, parent=None):
        super().__init__(parent)
        self.sim = sim
        self.top_panel = top_panel

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

        status_group = QGroupBox("Simulator Status")
        status_group.setStyleSheet("font-size: 24px; font-weight: bold;")
        status_layout = QVBoxLayout()
        self.status_table = QTableWidget(9, 4)
        self.status_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.status_table.setStyleSheet("font-size: 18px; border: none; QTableWidget::item { border: none; } gridline-color: transparent;") # Remove all borders and gridlines
        self.status_table.setShowGrid(False) # Ensure grid is not shown
        self.status_table.horizontalHeader().setVisible(False) # Hide horizontal header
        self.status_table.verticalHeader().setVisible(False) # Hide vertical header
        self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.status_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.status_table.setHorizontalHeaderLabels(["Parameter", "Value"])
        for i in range(9):
            self.status_table.setItem(i, 0, QTableWidgetItem(f"Param {i+1}"))
            self.status_table.setItem(i, 1, QTableWidgetItem(f"Value {i+1}"))
        status_layout.addWidget(self.status_table)
        status_group.setLayout(status_layout)
        chat_status_layout.addWidget(status_group, 3)

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
        
        self.setLayout(right_column)

    def format_power_with_unit(self, power_value):
        if power_value < 1e-3:
            return f"{power_value * 1e3:.3f} mW"
        elif power_value < 1:
            return f"{power_value:.3f} W"
        elif power_value < 1e3:
            return f"{power_value / 1e3:.3f} kW"
        elif power_value < 1e6:
            return f"{power_value / 1e6:.3f} MW"
        else:
            return f"{power_value / 1e6:.3f} MW"
        
    def update_plots(self, sim_data):
        self.line_keff.set_data(sim_data.time_history, sim_data.keff_history)
        if hasattr(self, 'keff_text') and self.keff_text:
            self.keff_text.remove()
        self.keff_text = self.ax_keff.annotate(
            f"{sim_data.keff:.5f}",
            xy=(sim_data.current_time, sim_data.keff),  
            xytext=(-50, 5),  
            textcoords='offset points',
            fontsize=10,
            color='blue',
            ha='left',
            va='bottom',
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.7)
        )
        
        self.line_power.set_data(sim_data.time_history, sim_data.power_history)
        if hasattr(self, 'power_text') and self.power_text:
            self.power_text.remove()
        formatted_power = self.format_power_with_unit(sim_data.power)
        self.power_text = self.ax_power.annotate(
            formatted_power,
            xy=(sim_data.current_time, sim_data.power),
            xytext=(-70, 0),
            textcoords='offset points',
            fontsize=10,
            color='darkorange',
            ha='left',
            va='bottom',
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.7)
        )
        
        self.line_temp.set_data(sim_data.time_history, sim_data.temp_history)
        for ax in [self.ax_keff, self.ax_power, self.ax_rod, self.ax_temp]:
            ax.set_xlim(sim_data.current_time - 10, sim_data.current_time)
        
        for name in self.sim.rod_names:
            self.rod_data = {name: [] for name in self.sim.rod_names} # This line might be problematic, it reinitializes rod_data
            self.rod_data[name].append(sim_data.rod_positions[name])
            self.rod_lines[name].set_data(sim_data.time_history, sim_data.rod_data[name])

        self.canvas.draw()

    def update_status_table(self, sim_data, demand_value, demand_unit, speed_value, pump_state, source_state, mode_state):
        # Update status table with current simulation data
        # Row 0: Demand
        item_demand_label = QTableWidgetItem("Demand:")
        item_demand_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_table.setItem(0, 0, item_demand_label)

        item_demand_value = QTableWidgetItem(f"{int(demand_value)} {demand_unit}")
        item_demand_value.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.status_table.setItem(0, 1, item_demand_value)

        # Row 1: Speed
        item_speed_label = QTableWidgetItem("Speed:")
        item_speed_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_table.setItem(1, 0, item_speed_label)

        item_speed_value = QTableWidgetItem(f"{speed_value:.1f}x")
        item_speed_value.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.status_table.setItem(1, 1, item_speed_value)

        # Row 2: Pump
        item_pump_label = QTableWidgetItem("Pump:")
        item_pump_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_table.setItem(2, 0, item_pump_label)

        item_pump_state = QTableWidgetItem(pump_state)
        item_pump_state.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.status_table.setItem(2, 1, item_pump_state)

        # Row 3: Source
        item_source_label = QTableWidgetItem("Source:")
        item_source_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_table.setItem(3, 0, item_source_label)

        item_source_state = QTableWidgetItem(source_state)
        item_source_state.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.status_table.setItem(3, 1, item_source_state)

        # Row 4: Mode
        item_mode_label = QTableWidgetItem("Mode:")
        item_mode_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_table.setItem(4, 0, item_mode_label)

        item_mode_state = QTableWidgetItem(mode_state)
        item_mode_state.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.status_table.setItem(4, 1, item_mode_state)

        # Control Rods
        rod_names = ["Tran", "Shim1", "Shim2", "Reg"]
        for i, rod_name in enumerate(rod_names):
            row_idx = 5 + i # Start from row 5
            
            item_rod_label = QTableWidgetItem(f"{rod_name}:")
            item_rod_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.status_table.setItem(row_idx, 0, item_rod_label)

            # Assuming sim_data.rod_positions is a dictionary with rod names as keys
            rod_position = sim_data.rod_positions.get(rod_name, 0) # Get position, default to 0 if not found
            item_rod_value = QTableWidgetItem(f"{int(rod_position)}")
            item_rod_value.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.status_table.setItem(row_idx, 1, item_rod_value)

        # Row 0: Power
        item_power_label = QTableWidgetItem("Pow:")
        item_power_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_table.setItem(0, 2, item_power_label)

        item_power_value = QTableWidgetItem(f"{sim_data.power:.3f}")
        item_power_value.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.status_table.setItem(0, 3, item_power_value)

        # Row 1: NM, NP, NPP
        item_nm_label = QTableWidgetItem("NM:")
        item_nm_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_table.setItem(1, 2, item_nm_label)
        self.status_table.setItem(1, 3, QTableWidgetItem("-"))

        item_np_label = QTableWidgetItem("NP:")
        item_np_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_table.setItem(2, 2, item_np_label)
        self.status_table.setItem(2, 3, QTableWidgetItem("-"))

        item_npp_label = QTableWidgetItem("NPP:")
        item_npp_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_table.setItem(3, 2, item_npp_label)
        self.status_table.setItem(3, 3, QTableWidgetItem("-"))

        # Row 4: keff
        item_keff_label = QTableWidgetItem("keff:")
        item_keff_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_table.setItem(4, 2, item_keff_label)

        item_keff_value = QTableWidgetItem(f"{sim_data.keff:.5f}")
        item_keff_value.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.status_table.setItem(4, 3, item_keff_value)

        # Row 5: Period
        item_period_label = QTableWidgetItem("Period:")
        item_period_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_table.setItem(5, 2, item_period_label)
        self.status_table.setItem(5, 3, QTableWidgetItem("-"))

        # Row 6: F.Temp1
        item_ftemp1_label = QTableWidgetItem("F.Temp1:")
        item_ftemp1_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_table.setItem(6, 2, item_ftemp1_label)
        self.status_table.setItem(6, 3, QTableWidgetItem("-"))

        # Row 7: F.Temp2
        item_ftemp2_label = QTableWidgetItem("F.Temp2:")
        item_ftemp2_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_table.setItem(7, 2, item_ftemp2_label)
        self.status_table.setItem(7, 3, QTableWidgetItem("-"))

        # Row 8: W.Temp
        item_wtemp_label = QTableWidgetItem("W.Temp:")
        item_wtemp_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_table.setItem(8, 2, item_wtemp_label)
        self.status_table.setItem(8, 3, QTableWidgetItem("-"))

        # Fill the rest of the table with placeholder values
        for row in range(9):
            for col in range(4):
                # Skip Demand, Speed, Pump, Source, Mode, Rods, and new columns
                if (row == 0 and (col == 0 or col == 1 or col == 2 or col == 3)) or \
                   (row == 1 and (col == 0 or col == 1 or col == 2 or col == 3)) or \
                   (row == 2 and (col == 0 or col == 1 or col == 2 or col == 3)) or \
                   (row == 3 and (col == 0 or col == 1 or col == 2 or col == 3)) or \
                   (row == 4 and (col == 0 or col == 1 or col == 2 or col == 3)) or \
                   (row >= 5 and row <= 8 and (col == 0 or col == 1 or col == 2 or col == 3)):
                    continue
                item = QTableWidgetItem(f"Row {row}, Col {col}")
                item.setTextAlignment(Qt.AlignCenter)
                self.status_table.setItem(row, col, item)

        # Example of updating other rows (adjust as needed)
        # self.status_table.setItem(1, 1, QTableWidgetItem(f"{sim_data.keff:.5f}"))
        # self.status_table.setItem(2, 1, QTableWidgetItem(f"{sim_data.power:.3f} W"))
