"""
agent_animation.py
エージェントのアニメーション更新ロジック（animate関数本体）を担当。
"""

import numpy as np
from config import *
from animation_core import (
    ro_i_history,
    eta_i_history,
    omega_i_history,
    alpha_i_history,
    u_vec_history,
    a_vec_history,
    e_i_1_integral,
    e_i_2_integral,
)


def agent_animate_update(
    i, agent_positions, target_pos, target_velocity, agent_colors, roi_text
):
    fps = 1 / frame_time
    roi_lines = []
    if not hasattr(agent_animate_update, "prev_agent_pos"):
        agent_animate_update.prev_agent_pos = agent_positions.copy()
    if not hasattr(agent_animate_update, "prev_target_pos"):
        agent_animate_update.prev_target_pos = np.array(target_pos)
    for j in range(num_agents):
        vec = agent_positions[j] - np.array(target_pos)
        ro_i = np.linalg.norm(vec)
        if ro_i > 0:
            e_r = vec / ro_i
            e_theta = np.array([-e_r[1], e_r[0]])
            agent_velocity = (
                agent_positions[j] - agent_animate_update.prev_agent_pos[j]
            ) / frame_time
            relative_velocity = agent_velocity - target_velocity
            relative_velocity_local = np.array(
                [np.dot(relative_velocity, e_r), np.dot(relative_velocity, e_theta)]
            )
            idx_plus = (j + 1) % num_agents
            idx_minus = (j - 1) % num_agents
            vec_plus = agent_positions[idx_plus] - agent_positions[j]
            vec_minus = agent_positions[idx_minus] - agent_positions[j]
            theta_plus_local = np.arctan2(
                np.dot(vec_plus, e_theta), np.dot(vec_plus, e_r)
            )
            theta_minus_local = np.arctan2(
                np.dot(vec_minus, e_theta), np.dot(vec_minus, e_r)
            )
            theta_now_local = 0.0
            if not hasattr(agent_animate_update, "prev_theta_local"):
                agent_animate_update.prev_theta_local = np.zeros(num_agents)
            omega_i_local = theta_now_local - agent_animate_update.prev_theta_local[j]
            omega_i_local = (omega_i_local + np.pi) % (2 * np.pi) - np.pi
            agent_animate_update.prev_theta_local[j] = theta_now_local
            if not hasattr(agent_animate_update, "prev_theta_plus_local"):
                agent_animate_update.prev_theta_plus_local = np.zeros(num_agents)
            if not hasattr(agent_animate_update, "prev_theta_minus_local"):
                agent_animate_update.prev_theta_minus_local = np.zeros(num_agents)
            omega_i_plus_local = (
                theta_plus_local - agent_animate_update.prev_theta_plus_local[j]
            )
            omega_i_plus_local = (omega_i_plus_local + np.pi) % (2 * np.pi) - np.pi
            omega_i_minus_local = (
                theta_minus_local - agent_animate_update.prev_theta_minus_local[j]
            )
            omega_i_minus_local = (omega_i_minus_local + np.pi) % (2 * np.pi) - np.pi
            agent_animate_update.prev_theta_plus_local[j] = theta_plus_local
            agent_animate_update.prev_theta_minus_local[j] = theta_minus_local
            alpha_i_local = abs(theta_plus_local - theta_now_local)
            alpha_i_minus_local = abs(theta_minus_local - theta_now_local)
            eta = relative_velocity_local[0]
            eta_norm = abs(eta)
            if i == 0:
                e_i_1 = 0
                e_i_2 = 0
            else:
                tau_i_1 = 0.5
                tau_i_2 = 0.5
                e_i_1 = tau_i_1 * abs(ro_i - R + eta_norm)
                e_i_2 = tau_i_2 * abs(ro_i * (omega_i_local + Omega - omega_i_local))
            e_i_1_integral[j] += e_i_1 * frame_time
            e_i_2_integral[j] += e_i_2 * frame_time
            fi = (d_i * alpha_i_local - d_i * alpha_i_minus_local) / (2 * d_i)
            zi = (
                d_i * (omega_i_plus_local - omega_i_local)
                - d_i * (omega_i_local - omega_i_minus_local)
            ) / (2 * d_i)
            u_r = (
                -ro_i * omega_i_local**2
                - eta_norm
                - e_i_1_integral[j] * np.sign(ro_i - R + eta_norm)
            )
            u_theta = (
                (omega_i_local + Omega + fi) * eta_norm
                + zi * ro_i
                + e_i_2_integral[j] * np.sign(fi + Omega - omega_i_local)
            )
            if ro_i > 1.2 * R or ro_i < 0.8 * R:
                u_r = u_r * 0.5
            else:
                u_r = u_r * 0.2
            if alpha_i_local < np.pi / 3.5 or alpha_i_local > np.pi / 2.5:
                u_theta = u_theta * 2
            else:
                u_theta = u_theta * 1
            theta_global = np.arctan2(e_r[1], e_r[0])
            A = np.array(
                [
                    [np.cos(theta_global), -np.sin(theta_global)],
                    [np.sin(theta_global), np.cos(theta_global)],
                ]
            )
            u_vec_local = np.array([u_r, u_theta])
            u_vec = A @ u_vec_local
            # --- ここから距離R未満に近づかない制御を追加 ---
            next_pos = agent_positions[j] + u_vec * frame_time
            vec_next = next_pos - np.array(target_pos)
            ro_i_next = np.linalg.norm(vec_next)
            if ro_i_next < R:
                # Rの円周上に投影
                next_pos = np.array(target_pos) + R * (vec_next / (ro_i_next + 1e-8))
            agent_positions[j] = next_pos
            # --- ここまで追加 ---
            omega_i_sec = omega_i_local * fps
            u_vec_sec = u_vec * fps
            ro_i_history[j].append(ro_i)
            eta_i_history[j].append(eta)
            omega_i_history[j].append(omega_i_sec)
            alpha_i_history[j].append(alpha_i_local)
            u_vec_history[j].append(u_vec_sec.copy())
            if len(u_vec_history[j]) > 1:
                a_vec = (u_vec_history[j][-1] - u_vec_history[j][-2]) / frame_time
                a_vec_history[j].append(np.linalg.norm(a_vec))
            else:
                a_vec_history[j].append(0.0)
        else:
            roi_lines.append(f"Agent{j+1}")
            roi_lines.append(f"  ro_i={ro_i:.2f} (<=0, skipped)")
            roi_lines.append(f"  --- skipped ---")
    roi_text.set_text("\n".join(roi_lines))
    agent_animate_update.prev_agent_pos = agent_positions.copy()
    agent_animate_update.prev_target_pos = np.array(target_pos)
