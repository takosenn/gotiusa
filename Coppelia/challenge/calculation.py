from parameter import R, Omega


def calculate_e_i(i, ro_i, omega_i_local, eta_norm):
    if i == 0:
        tau_i_1 = 0
        tau_i_2 = 0
    else:
        tau_i_1 = 0.5
        tau_i_2 = 0.5
    e_i_1 = tau_i_1 * abs(ro_i - R + eta_norm)
    e_i_2 = tau_i_2 * abs(ro_i * (omega_i_local + Omega - omega_i_local))

    return e_i_1, e_i_2
