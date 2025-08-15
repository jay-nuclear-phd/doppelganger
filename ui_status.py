from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
)
from PyQt5.QtCore import Qt

class StatusPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Simulator Status", parent)
        self.base_stylesheet = "font-weight: bold;"
        self.setStyleSheet(f"font-size: 24px; {self.base_stylesheet}")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        status_layout = QVBoxLayout()
        self.status_table = QTableWidget(9, 4)
        self.status_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table_base_stylesheet = "border: none; QTableWidget::item { border: none; } gridline-color: transparent;"
        self.status_table.setStyleSheet(f"font-size: 15px; {self.table_base_stylesheet}")
        self.status_table.setShowGrid(False)
        self.status_table.horizontalHeader().setVisible(False)
        self.status_table.verticalHeader().setVisible(False)
        self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.status_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.status_table.setHorizontalHeaderLabels(["Parameter", "Value"])
        for i in range(9):
            self.status_table.setItem(i, 0, QTableWidgetItem(f"Param {i+1}"))
            self.status_table.setItem(i, 1, QTableWidgetItem(f"Value {i+1}"))
        
        status_layout.addWidget(self.status_table)
        self.setLayout(status_layout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Adjust title font size
        title_font_size = int(self.height() / 20)
        if title_font_size < 10: title_font_size = 10
        self.setStyleSheet(f"font-size: {title_font_size}px; {self.base_stylesheet}")

        # Adjust table font size
        table_font_size = int(self.height() / 30)
        if table_font_size < 8: table_font_size = 8
        self.status_table.setStyleSheet(f"font-size: {table_font_size}px; {self.table_base_stylesheet}")

    def format_power_with_unit(self, power_value):
        if power_value < 1e-9:
            val, unit = power_value * 1e12, "pW"
        elif power_value < 1e-6:
            val, unit = power_value * 1e9, "nW"
        elif power_value < 1e-3:
            val, unit = power_value * 1e6, "µW"
        elif power_value < 1:
            val, unit = power_value * 1e3, "mW"
        elif power_value < 1e3:
            val, unit = power_value, "W"
        elif power_value < 1e6:
            val, unit = power_value / 1e3, "kW"
        elif power_value < 1e9:
            val, unit = power_value / 1e6, "MW"
        else:
            val, unit = power_value / 1e9, "GW"

        if val >= 1000:
            return f"{val:.0f} {unit}"
        elif val >= 100:
            return f"{val:.1f} {unit}"
        elif val >= 10:
            return f"{val:.2f} {unit}"
        else:
            return f"{val:.3f} {unit}"

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

        item_power_value = QTableWidgetItem(self.format_power_with_unit(max(sim_data.power, 2.2e-5)))
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

        # Row 4: rho
        item_rho_label = QTableWidgetItem("rho:")
        item_rho_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_table.setItem(4, 2, item_rho_label)

        item_rho_value = QTableWidgetItem(f"{sim_data.total_rho:.5f}")
        item_rho_value.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.status_table.setItem(4, 3, item_rho_value)

        # Row 5: Period
        item_period_label = QTableWidgetItem("Period:")
        item_period_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_table.setItem(5, 2, item_period_label)
        self.status_table.setItem(5, 3, QTableWidgetItem("-"))

        # Row 6: F.Temp1
        item_ftemp1_label = QTableWidgetItem("F.Temp1:")
        item_ftemp1_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_table.setItem(6, 2, item_ftemp1_label)
        item_ftemp1_value = QTableWidgetItem(f"{sim_data.F_Temp1_history[-1]:.2f}")
        item_ftemp1_value.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.status_table.setItem(6, 3, item_ftemp1_value)

        # Row 7: F.Temp2
        item_ftemp2_label = QTableWidgetItem("F.Temp2:")
        item_ftemp2_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_table.setItem(7, 2, item_ftemp2_label)
        item_ftemp2_value = QTableWidgetItem(f"{sim_data.F_Temp2_history[-1]:.2f}")
        item_ftemp2_value.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.status_table.setItem(7, 3, item_ftemp2_value)

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