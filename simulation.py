import numpy as np
from utils import make_linear_interp_with_extrapolation

class ReactorSimulator:
    def __init__(self):
        self.rod_speed = 30 * 8  # unit/sec
        self.max_position = 960
        self.min_position = 0
        self.running = False

        self.rod_names = ["Tran", "Shim1", "Shim2", "Reg"]
        self.rod_params = {
            "Tran":  {"alpha": 0.5562, "beta": -218.81, "L": 1264.32},
            "Shim2": {"alpha": 0.4448, "beta": -249.84, "L": 1369.01},
            "Shim1": {"alpha": 0.5457, "beta": -212.14, "L": 1305.19},
            "Reg":   {"alpha": 0.5121, "beta": -342.84, "L": 1738.45}
        }

        self.rod_positions = {name: 0 for name in self.rod_names}
        self.pressed_state = {name+"_up": False for name in self.rod_names}
        self.pressed_state.update({name+"_down": False for name in self.rod_names})
        self.scram_active = False

        self.keff, _ = self.calculate_total_keff()
        self.power = 2.5e-4
        self.temperature = 18.0
        self.keff_history = []
        self.power_history = []
        self.temp_history = []
        self.time_history = []
        self.current_time = 0
        self.rho_interp = self.load_rho_vs_T()
        self.rod_data = {name: [] for name in self.rod_names}
        self.heat_loss_coefficient = 0.01
        self.rod_rho = 0

    def update_simulation(self, dt):
        if not self.running:
            return

        self.current_time += dt

        for name in self.rod_names:
            if self.scram_active:
                self.rod_positions[name] = max(self.rod_positions[name] - self.rod_speed * dt, self.min_position)
            else:
                if self.pressed_state[name+"_up"]:
                    self.rod_positions[name] = min(self.rod_positions[name] + self.rod_speed * dt, self.max_position)
                if self.pressed_state[name+"_down"]:
                    self.rod_positions[name] = max(self.rod_positions[name] - self.rod_speed * dt, self.min_position)

        if self.scram_active and all(pos <= self.min_position for pos in self.rod_positions.values()):
            self.scram_active = False

        keff, total_rod_worth = self.calculate_total_keff()
        self.keff = keff
        self.rod_rho = total_rod_worth
        self.keff_history.append(keff)

        rho = (keff - 1) / keff * 100 / 0.007
        T = self.rho_interp(abs(rho))
        if rho > 0:
            self.power *= 10 ** (dt / T)
        else:
            self.power *= 10 ** (-dt / T)
        self.power = max(self.power, 2.5e-4)
        self.power_history.append(self.power)
        # Temperature update (simple model)
        # Temperature increases with power, decreases due to heat loss
        self.temperature += (self.power * 1e-6 * 0.001) - (self.temperature - 20) * self.heat_loss_coefficient * dt # Assuming 1MW = 1 degree C/s, and 20 is ambient
        self.temperature = max(self.temperature, 20) # Prevent temperature from going below ambient
        self.temp_history.append(self.temperature)
        self.time_history.append(self.current_time)
        if self.current_time > 10:
            while self.time_history and self.time_history[0] < self.current_time - 10:
                self.time_history.pop(0)
                self.keff_history.pop(0)
                # self.rod_rho_history.pop(0)
                self.power_history.pop(0)
                self.temp_history.pop(0) if self.temp_history else None
                for name in self.rod_names:
                    if self.rod_data[name]:
                        self.rod_data[name].pop(0)

        for name in self.rod_names:
            self.rod_data[name].append(self.rod_positions[name])

    

    def calculate_total_keff(self):
        keff = 0.9474639757687583
        total_rod_worth = 0 # Initialize total rod worth
        for name in self.rod_names:
            x = self.rod_positions[name]
            p = self.rod_params[name]
            worth = p["alpha"] / 4 / np.pi * (-p["L"] * np.sin(np.pi * 2 * p["beta"] / p["L"]) - p["L"] * np.sin(2 * np.pi * (x - p["beta"]) / p["L"]) + 2 * x * np.pi)
            keff += worth * 0.01 * 0.007
            total_rod_worth += worth * 0.01 * 0.007 # Accumulate rod worth
        return keff, total_rod_worth

    def load_rho_vs_T(self):
        beta_eff = 0.007
        l = 42e-6
        T = np.logspace(-5, 10, 5000)
        f = np.array([0.038, 0.213, 0.188, 0.407, 0.128, 0.026])
        thalf = np.array([54.5, 21.8, 6.0, 2.23, 0.496, 0.179])
        lmbd = np.log(2) / thalf
        rho = []
        for j in range(len(T)):
            second_term = 0
            for i in range(6):
                second_term += f[i] / (1 + lmbd[i] * T[j])
            value = 100 / (1 + l / T[j]) * (l / beta_eff / T[j] + second_term)
            rho.append(value)
        rho = np.array(rho)
        return make_linear_interp_with_extrapolation(T, rho)

    def reset_simulation(self):
        self.running = False
        self.scram_active = False
        self.current_time = 0
        self.keff, self.rod_rho = self.calculate_total_keff()
        self.power = 2.5e-4
        self.keff_history.clear()
        self.power_history.clear()
        self.temp_history.clear()
        self.time_history.clear()
        self.rod_positions = {name: 0 for name in self.rod_names}
        self.rod_data = {name: [] for name in self.rod_names}
