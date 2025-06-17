# animation_core.py
import numpy as np
from config import *
from controls import angular_distance_rad
from init_plot import center, radius, agent_positions, agent_dots, agent_colors
from animation_data import (
    ro_i_history,
    eta_i_history,
    omega_i_history,
    alpha_i_history,
    u_vec_history,
    a_vec_history,
)


def animate(i):
    theta = omega_target * i
    x = center[0] + radius * np.sin(theta)
    y = center[1] + radius * np.cos(theta)
    point = agent_dots.axes.lines[0]  # pointはinit_plotで定義済み
    point.set_data([x], [y])
    agent_dots.set_offsets(agent_positions)
    agent_dots.set_color(agent_colors)

    if not hasattr(
        animate, "prev_agent_pos"
    ):  # 初期位置の時には前の情報がない．そのエラー回避？
        animate.prev_agent_pos = agent_positions.copy()
    if not hasattr(animate, "prev_target_pos"):
        animate.prev_target_pos = np.array([x, y])

    for j in range(num_agents):
        vec = agent_positions[j] - np.array([x, y])
        theta_now = np.arctan2(vec[1], vec[0])
        if not hasattr(animate, "prev_theta"):
            animate.prev_theta = np.zeros(num_agents)
        ro_i = np.linalg.norm(vec)
        omega_i = theta_now - animate.prev_theta[j]
        omega_i = (omega_i + np.pi) % (2 * np.pi) - np.pi
        animate.prev_theta[j] = theta_now
        if ro_i > 0:
            idx_plus = (j + 1) % num_agents
            idx_minus = (j - 1) % num_agents
            vec_plus = agent_positions[idx_plus] - np.array([x, y])
            vec_minus = agent_positions[idx_minus] - np.array([x, y])
            theta_plus = np.arctan2(vec_plus[1], vec_plus[0])
            theta_minus = np.arctan2(vec_minus[1], vec_minus[0])
            if not hasattr(animate, "prev_theta_plus"):
                animate.prev_theta_plus = np.zeros(num_agents)
            if not hasattr(animate, "prev_theta_minus"):
                animate.prev_theta_minus = np.zeros(num_agents)
            omega_i_plus = theta_plus - animate.prev_theta_plus[j]
            omega_i_plus = (omega_i_plus + np.pi) % (2 * np.pi) - np.pi
            omega_i_minus = theta_minus - animate.prev_theta_minus[j]
            omega_i_minus = (omega_i_minus + np.pi) % (2 * np.pi) - np.pi
            animate.prev_theta_plus[j] = theta_plus
            animate.prev_theta_minus[j] = theta_minus
            alpha_i = angular_distance_rad(theta_now, theta_plus)
            alpha_i_minus = angular_distance_rad(theta_now, theta_minus)
            fi = (d_i * alpha_i - d_i * alpha_i_minus) / (2 * d_i)
            zi = (d_i * (omega_i_plus - omega_i) - d_i * (omega_i - omega_i_minus)) / (
                2 * d_i
            )
            e_r = vec / ro_i
            e_theta = np.array([-e_r[1], e_r[0]])
            target_velocity = np.array(
                [
                    -radius * omega_target * np.cos(theta),
                    -radius * omega_target * np.sin(theta),
                ]
            )
            agent_velocity = (
                agent_positions[j] - animate.prev_agent_pos[j]
            ) / frame_time
            relative_velocity = agent_velocity - target_velocity
            relative_velocity_r = np.dot(relative_velocity, e_r)
            eta = relative_velocity_r
            eta_norm = abs(eta)
            u_r = -ro_i * omega_i**2 - eta_norm - l1 * np.sign(ro_i - R + eta_norm)
            u_theta = (
                (omega_i + Omega + fi) * eta_norm
                + zi * ro_i
                + l2 * np.sign(fi + Omega - omega_i)
            )
            u_vec = u_r * e_r + u_theta * e_theta
            agent_positions[j] += u_vec * 0.05
            omega_i_sec = omega_i * fps
            omega_i_plus_sec = omega_i_plus * fps
            omega_i_minus_sec = omega_i_minus * fps
            u_r_sec = u_r * fps
            u_theta_sec = u_theta * fps
            u_vec_sec = u_vec * fps
            ro_i_history[j].append(ro_i)
            eta_i_history[j].append(eta)
            omega_i_history[j].append(omega_i_sec)
            alpha_i_history[j].append(alpha_i)
            u_vec_history[j].append(u_vec_sec.copy())
            if len(u_vec_history[j]) > 1:
                a_vec = (u_vec_history[j][-1] - u_vec_history[j][-2]) / frame_time
                a_vec_history[j].append(np.linalg.norm(a_vec))
            else:
                a_vec_history[j].append(0.0)
        else:
            pass  # roi_linesやroi_textの処理を削除
    animate.prev_agent_pos = agent_positions.copy()
    animate.prev_target_pos = np.array([x, y])
    from init_plot import point

    return point, agent_dots
