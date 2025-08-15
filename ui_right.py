from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox, QSizePolicy
)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from ui_status import StatusPanel

class RightPanel(QWidget):
    def __init__(self, sim, top_panel, parent=None):
        super().__init__(parent)
        self.sim = sim
        self.top_panel = top_panel

        self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.tight_layout()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.ax_rho = self.axes[0, 0]
        self.ax_power = self.axes[0, 1]
        self.ax_rod = self.axes[1, 0]
        self.ax_temp = self.axes[1, 1]

        self.line_rho, = self.ax_rho.plot([], [], label='rho', color='blue')
        self.ax_rho.axhline(1.0, color='red', linestyle='--', linewidth=1, alpha=0.5)
        self.ax_rho.set_ylim(-800, 800)
        self.ax_rho.set_ylabel('rho')
        self.ax_rho.set_xlabel('Time (s)')
        self.ax_rho.grid(True)
        self.ax_rho.legend()
        
        self.line_power, = self.ax_power.plot([], [], label='Power', color='orange')
        self.ax_power.set_xlabel('Time (s)')
        self.ax_power.set_ylim(1e-5, 1e11)
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

        self.line_F_Temp1, = self.ax_temp.plot([], [], label='F.Temp1', color='red')
        self.line_F_Temp2, = self.ax_temp.plot([], [], label='F.Temp2', color='purple')
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

        self.status_panel = StatusPanel()
        chat_status_layout.addWidget(self.status_panel, 3)

        chatbot_group = QGroupBox("Chatbot")
        chatbot_group.setStyleSheet("font-size: 24px; font-weight: bold;")
        chatbot_layout = QVBoxLayout()
        self.chatbot_content = QLabel("Chatbot content will appear here.")
        self.chatbot_content.setAlignment(Qt.AlignCenter)
        chatbot_layout.addWidget(self.chatbot_content)
        chatbot_group.setLayout(chatbot_layout)
        chat_status_layout.addWidget(chatbot_group, 7)

        right_column.addWidget(chat_status_container, 4)
        right_column.addWidget(canvas_container, 6)
        
        self.setLayout(right_column)

    def update_plots(self, sim_data):
        self.line_rho.set_data(sim_data.time_history, sim_data.total_rho_history)
        if hasattr(self, 'rho_text') and self.rho_text:
            self.rho_text.remove()
        self.rho_text = self.ax_rho.annotate(
            f"{sim_data.total_rho:.5f}",
            xy=(sim_data.current_time, sim_data.total_rho),  
            xytext=(-50, 5),  
            textcoords='offset points',
            fontsize=10,
            color='blue',
            ha='left',
            va='bottom',
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.7)
        )
        
        power_floor = 2.2e-5
        clipped_power_history = [max(p, power_floor) for p in sim_data.power_history]
        clipped_current_power = max(sim_data.power, power_floor)

        self.line_power.set_data(sim_data.time_history, clipped_power_history)
        if hasattr(self, 'power_text') and self.power_text:
            self.power_text.remove()
        
        formatted_power = self.status_panel.format_power_with_unit(clipped_current_power)
        self.power_text = self.ax_power.annotate(
            formatted_power,
            xy=(sim_data.current_time, clipped_current_power),
            xytext=(-70, 0),
            textcoords='offset points',
            fontsize=10,
            color='darkorange',
            ha='left',
            va='bottom',
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.7)
        )
        
        self.line_F_Temp1.set_data(sim_data.time_history, sim_data.F_Temp1_history)
        self.line_F_Temp2.set_data(sim_data.time_history, sim_data.F_Temp2_history)

        for ax in [self.ax_rho, self.ax_power, self.ax_rod, self.ax_temp]:
            ax.set_xlim(sim_data.current_time - 10, sim_data.current_time)
        
        for name in self.sim.rod_names:
            self.rod_lines[name].set_data(sim_data.time_history, sim_data.rod_data[name])

        self.canvas.draw()

    def update_status_table(self, sim_data, demand_value, demand_unit, speed_value, pump_state, source_state, mode_state):
        self.status_panel.update_status_table(sim_data, demand_value, demand_unit, speed_value, pump_state, source_state, mode_state)