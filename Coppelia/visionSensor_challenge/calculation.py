
import parameter as param
import numpy as np

class Calculation:
    def __init__(self, d_i, ro_i, omega_i_local, omega_i_plus_local, omega_i_minus_local, alpha_i_local, alpha_i_minus_local, eta_norm, e_i_1_integral, e_i_2_integral, j, i):
        self.d_i = d_i
        self.ro_i = ro_i
        self.omega_i_local = omega_i_local
        self.omega_i_plus_local = omega_i_plus_local
        self.omega_i_minus_local = omega_i_minus_local
        self.alpha_i_local = alpha_i_local
        self.alpha_i_minus_local = alpha_i_minus_local
        self.eta_norm = eta_norm
        self.e_i_1_integral = e_i_1_integral
        self.e_i_2_integral = e_i_2_integral
        self.j = j
        self.i = i
    
    def calculate_fi_zi(self):
        if self.i ==0:
            tau_i_1 = 0
            tau_i_2 = 0
        else:
            tau_i_1 = 0.5
            tau_i_2 = 0.5
        e_i_1 = tau_i_1 * abs(self.ro_i - param.R + self.eta_norm)
        e_i_2 = tau_i_2 * abs(self.ro_i * (self.omega_i_local + param.Omega - self.omega_i_local))

        self.e_i_1_integral[self.j] += e_i_1 * param.frame_time
        self.e_i_2_integral[self.j] += e_i_2 * param.frame_time
        fi = (self.d_i * self.alpha_i_local - self.d_i * self.alpha_i_minus_local) / (2 * self.d_i)
        zi = (self.d_i * (self.omega_i_plus_local - self.omega_i_local)- self.d_i * (self.omega_i_local - self.omega_i_minus_local)) / (2 * self.d_i)
        return fi , zi , self.e_i_1_integral , self.e_i_2_integral
    
    def calculate_u(self):
        fi , zi ,self.e_i_1_integral , self.e_i_2_integral = self.calculate_fi_zi()
        u_r = (-self.ro_i * self.omega_i_local**2- self.eta_norm- self.e_i_1_integral[self.j] * np.sign(self.ro_i - param.R + self.eta_norm))
        u_theta = ((self.omega_i_local + param.Omega + fi) * self.eta_norm+ zi * self.ro_i+ self.e_i_2_integral[self.j] * np.sign(fi + param.Omega - self.omega_i_local))
        if self.ro_i > 1.5 * param.R or self.ro_i < 0.5 * param.R:
            u_r = u_r * 0.5
        else:
            u_r = u_r * 0.2
        if self.alpha_i_local < np.pi / 3.4 or self.alpha_i_local > np.pi / 2.6:
            u_theta = u_theta * 2
        else:
            u_theta = u_theta * 1
        return u_r , u_theta