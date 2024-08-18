import numpy as np
from scipy.integrate import odeint

# TODO: IMPLEMENTAR UMA CLASSE GENÉRICA PARA SISTEMAS

class InvertedPendulum:
    def __init__(self, m=0.1, M=1.0, L=0.5, g=9.8, d=0.1):
        self.m = m
        self.M = M
        self.L = L
        self.g = g
        self.d = d
        self.name = "Inverted Pendulum"

    def dynamics(self, state, t, u):
        x, x_dot, theta, theta_dot = state
        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)
        total_mass = self.m + self.M
        temp = (u[0] + self.m * self.L * theta_dot**2 * sin_theta - self.d * x_dot) / total_mass
        theta_acc = (self.g * sin_theta - cos_theta * temp) / (self.L * (4/3 - self.m * cos_theta**2 / total_mass))
        x_acc = temp - self.m * self.L * theta_acc * cos_theta / total_mass
        return [x_dot, x_acc, theta_dot, theta_acc]

    def simulate(self, state, t, u):
        state_trajectory = odeint(self.dynamics, state, t, args=(u,))
        return state_trajectory

    def initial_state(self):
        return np.array([0, 0, np.pi, 0])  # Estado inicial [x, x_dot, theta, theta_dot]