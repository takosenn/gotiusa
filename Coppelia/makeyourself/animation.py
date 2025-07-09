# アニメーションのメイン関数(1フレームごとに呼ばれる)
import numpy as np
from init_parameter import num_agents, R, Omega, frame_time
from target_move import target_move, target_pos
from SecondD_ani_init import agent_positions,point, agent_dots, agent_colors
from calculation import calculate
from Data_storage import (
    e_i_1_integral,
    e_i_2_integral,
    ro_i_history,
    eta_i_history,
    omega_i_history,
    alpha_i_history,
    u_vec_history,
    a_vec_history,
)
from control_protcol import protcol
from global_trans import global_trans
from unit_trans import rad_per_sec, meter_per_sec

def animate(i):
    target_move()
    agent_dots.set_offsets(agent_positions)  # エージェントの位置を更新
    # 色分けを毎フレーム反映
    agent_dots.set_color(agent_colors)
    if not hasattr(animate, "prev_agent_pos"):
        animate.prev_agent_pos = agent_positions.copy()
    if not hasattr(animate, "prev_target_pos"):
        animate.prev_target_pos = np.array(target_pos)
    for j in range(num_agents):
        result = calculate(
            animate
        )  # 8つの変数を持つ(eta_norm,ro_i,omega_i_local,omega_i_plus_local,omega_i_minus_local,alpha_i_local,alpha_i_minus_local,e_r)
        tau_i_1 = 0.5
        tau_i_2 = 0.5
        if i == 0:
            e_i_1 = 0
            e_i_2 = 0
        else:
            e_i_1 = tau_i_1 * abs(result[1] - R + result[0])
            e_i_2 = tau_i_2 * abs(result[1] * (result[3] + Omega - result[3]))
        e_i_1_integral[j] += e_i_1 * frame_time
        e_i_2_integral[j] += e_i_2 * frame_time
        protcol_result = protcol(
            i,
            j,
            result[0],
            result[1],
            result[2],
            result[3],
            result[4],
            result[5],
            result[6],
            result[7],
        )
        theta_global = np.arctan2(result[7][1], result[7][0])
        u_vec = global_trans(theta_global, protcol_result[0], protcol_result[1])
        agent_positions[j] += u_vec * frame_time
        omega_i_sec = rad_per_sec(result[2])
        u_vec_sec = meter_per_sec(u_vec)
        ro_i_history[j].append(result[1])
        eta_i_history[j].append(result[0])
        omega_i_history[j].append(omega_i_sec)  # [rad/sec]で保存
        alpha_i_history[j].append(result[5])  # [rad]で保存
        u_vec_history[j].append(u_vec_sec.copy())
        # 加速度計算（2フレーム目以降)
        if len(u_vec_history[j]) > 1:
            a_vec = (u_vec_history[j][-1] - u_vec_history[j][-2]) / frame_time
            a_vec_history[j].append(np.linalg.norm(a_vec))  # 大きさ[m/s^2]
        else:
            a_vec_history[j].append(0.0)

    animate.prev_agent_pos = (
        agent_positions.copy()
    )  # 現在のエージェント位置を保存（次フレーム用）
    animate.prev_target_pos = np.array(
        target_pos
    )  # 現在のターゲット位置を保存（次フレーム用）

    # Artistオブジェクトを返す（matplotlibアニメーションに必要）
    return point, agent_dots
