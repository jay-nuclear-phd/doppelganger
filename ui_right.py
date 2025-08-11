from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QSizePolicy, QHeaderView # Added for table
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class RightPanel(QWidget):
    def __init__(self, sim, parent=None):
        super().__init__(parent)
        self.sim = sim

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
        self.status_table = QTableWidget(9, 2)
        self.status_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.status_table.setStyleSheet("font-size: 14px;")
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

    def update_status_table(self, sim_data):
        # Update status table with current simulation data
        self.status_table.setItem(0, 1, QTableWidgetItem(f"{sim_data.keff:.5f}"))
        self.status_table.setItem(1, 1, QTableWidgetItem(f"{sim_data.power:.3f} W")) # Example
        # ... update other rows as needed
