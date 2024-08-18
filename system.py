import numpy as np
from scipy.integrate import odeint

class BaseSystem:
    def __init__(self, name):
        self.name = name

    def dynamics(self, state, t, u):
        raise NotImplementedError("This method should be overridden by subclasses")

    def simulate(self, state, t, u):
        state_trajectory = odeint(self.dynamics, state, t, args=(u,))
        return state_trajectory

class InvertedPendulum(BaseSystem):
    def __init__(self, m=0.1, M=1.0, L=0.5, g=9.8, d=0.1):
        super().__init__("Inverted Pendulum")
        self.m = m
        self.M = M
        self.L = L
        self.g = g
        self.d = d

    def dynamics(self, state, t, u):
        x, x_dot, theta, theta_dot = state
        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)
        total_mass = self.m + self.M
        temp = (u[0] + self.m * self.L * theta_dot**2 * sin_theta - self.d * x_dot) / total_mass
        theta_acc = (self.g * sin_theta - cos_theta * temp) / (self.L * (4/3 - self.m * cos_theta**2 / total_mass))
        x_acc = temp - self.m * self.L * theta_acc * cos_theta / total_mass
        return [x_dot, x_acc, theta_dot, theta_acc]