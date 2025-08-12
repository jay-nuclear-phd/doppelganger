import numpy as np

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
        # Point kinetics parameters
        self.beta_i = np.array([0.000215, 0.001424, 0.001274, 0.002568, 0.000748, 0.000273])
        self.lam_i  = np.array([0.0124,   0.0305,   0.111,    0.301,    1.14,     3.01   ])
        self.beta_eff = 0.007
        self.Lambda = 42e-6
        self.S = 2.54e-3 # Source term

        self.rod_positions = {name: 0 for name in self.rod_names}
        self.pressed_state = {name+"_up": False for name in self.rod_names}
        self.pressed_state.update({name+"_down": False for name in self.rod_names})
        self.scram_active = False

        # Initial conditions
        self.rod_rho = self.calculate_rod_rho()
        rho0 = self.rod_rho * 0.01 * self.beta_eff # convert to absolute
        if abs(rho0) > 1e-10:
            self.power = max(1e-20, -self.S * self.Lambda / rho0)
        else:
            self.power = 1e-6
        self.C = (self.beta_i / (self.Lambda * self.lam_i)) * self.power

        self.temperature = 18.0
        self.current_time = 0

        # Initialize and append initial state to history lists
        self.rod_rho_history = [self.rod_rho]
        self.power_history = [self.power]
        self.temp_history = [self.temperature]
        self.time_history = [self.current_time]
        self.rod_data = {name: [self.rod_positions[name]] for name in self.rod_names}

        self.heat_loss_coefficient = 0.01

    def reset_simulation_state(self):
        """Helper to set or reset the simulation state variables."""
        # This method is now primarily for setting the current state, not history.
        # History is handled in __init__ and reset_simulation.
        rho_cents = self.calculate_rod_rho()
        self.rod_rho = rho_cents
        
        rho0 = rho_cents * 0.01 * self.beta_eff # convert to absolute
        
        if abs(rho0) > 1e-10:
            n0 = max(1e-20, -self.S * self.Lambda / rho0)
        else:
            n0 = 1e-6
        
        self.power = n0
        self.C = (self.beta_i / (self.Lambda * self.lam_i)) * n0

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

        self.rod_rho = self.calculate_rod_rho()

        # Implicit solver for point kinetics
        r = self.rod_rho * 0.01 * self.beta_eff # convert cents to absolute

        A = np.zeros((7, 7))
        b = np.zeros(7)

        # Previous state y_k
        y_k = np.empty((7,))
        y_k[0] = self.power
        y_k[1:] = self.C

        # Matrix A for y_k+1 = inv(A) * b
        A[0, 0] = 1.0 - dt * (r - self.beta_eff) / self.Lambda
        for i in range(6):
            A[0, 1+i] = -dt * self.lam_i[i]
        
        for i in range(6):
            A[1+i, 0]   = -dt * (self.beta_i[i] / self.Lambda)
            A[1+i, 1+i] = 1.0 + dt * self.lam_i[i]

        # Vector b
        b[0] = y_k[0] + dt * self.S
        b[1:] = y_k[1:]

        # Solve for new state y_k+1
        y_k_plus_1 = np.linalg.solve(A, b)

        # Update state and apply floors
        self.power = max(y_k_plus_1[0], 1e-25)
        self.C = np.maximum(y_k_plus_1[1:], 0.0)

        # Append current state to history lists
        self.time_history.append(self.current_time)
        self.rod_rho_history.append(self.rod_rho)
        self.power_history.append(self.power)
        self.temperature += (self.power * 1e-6 * 0.001) - (self.temperature - 20) * self.heat_loss_coefficient * dt
        self.temperature = max(self.temperature, 20)
        self.temp_history.append(self.temperature)
        
        if self.current_time > 10:
            while self.time_history and self.time_history[0] < self.current_time - 10:
                self.time_history.pop(0)
                self.rod_rho_history.pop(0)
                self.power_history.pop(0)
                self.temp_history.pop(0) if self.temp_history else None
                for name in self.rod_names:
                    if self.rod_data[name]:
                        self.rod_data[name].pop(0)

        for name in self.rod_names:
            self.rod_data[name].append(self.rod_positions[name])

    def calculate_rod_rho(self):
        # Per user, this returns reactivity in cents
        rod_rho_worth = -750.5146318748818
        for name in self.rod_names:
            x = self.rod_positions[name]
            p = self.rod_params[name]
            worth = p["alpha"] / 4 / np.pi * (-p["L"] * np.sin(np.pi * 2 * p["beta"] / p["L"]) - p["L"] * np.sin(2 * np.pi * (x - p["beta"]) / p["L"]) + 2 * x * np.pi)
            rod_rho_worth += worth
        return rod_rho_worth

    def reset_simulation(self):
        self.running = False
        self.scram_active = False
        self.current_time = 0
        self.rod_positions = {name: 0 for name in self.rod_names}
        
        # Reset current state variables
        self.rod_rho = self.calculate_rod_rho()
        rho0 = self.rod_rho * 0.01 * self.beta_eff # convert to absolute
        if abs(rho0) > 1e-10:
            self.power = max(1e-20, -self.S * self.Lambda / rho0)
        else:
            self.power = 1e-6
        self.C = (self.beta_i / (self.Lambda * self.lam_i)) * self.power
        self.temperature = 18.0

        # Clear and re-append initial state to history lists
        self.rod_rho_history.clear()
        self.power_history.clear()
        self.temp_history.clear()
        self.time_history.clear()
        self.rod_data = {name: [] for name in self.rod_names}

        self.time_history.append(self.current_time)
        self.rod_rho_history.append(self.rod_rho)
        self.power_history.append(self.power)
        self.temp_history.append(self.temperature)
        for name in self.rod_names:
            self.rod_data[name].append(self.rod_positions[name])
