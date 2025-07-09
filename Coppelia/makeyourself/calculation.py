# calculation
# 計算用

import numpy as np
from init_parameter import num_agents, frame_time
from SecondD_ani_init import agent_positions
from target_move import target_velocity, target_pos
from visionSensor import sim, visionSensorHandles


def calculate(animate):
    for j in range(num_agents):
        ro_i = None  # VisionSensorでの距離計測値
        try:
            visionSensorHandle = visionSensorHandles[j]
            result = sim.getVisionSensorDepth(visionSensorHandle)
            if result is not None:
                depthBuffer, resolution = result
                depthArray = np.array(depthBuffer, dtype=np.float64)
                if len(resolution) == 2:
                    depthArray = depthArray.reshape(resolution)
                nearClip = sim.getObjectFloatParam(
                    visionSensorHandle, sim.visionfloatparam_near_clipping
                )
                farClip = sim.getObjectFloatParam(
                    visionSensorHandle, sim.visionfloatparam_far_clipping
                )
                realDepth = nearClip + (farClip - nearClip) * depthArray
                valid_mask = realDepth < (farClip - 1e-4)
                if np.any(valid_mask):
                    minDist = np.min(realDepth[valid_mask])
                    if np.isfinite(minDist):
                        ro_i = minDist
                        print(f"[Drone{j+1}] VisionSensorで検知: ro_i = {ro_i:.2f} m")
                    else:
                        print(f"[Drone{j+1}] VisionSensor: 有効な物体なし")
                else:
                    print(f"[Drone{j+1}] VisionSensor: 物体未検知")
        except Exception as e:
            print(f"[Drone{j+1}] VisionSensor error: {e}")

        if ro_i is None:
            vec = agent_positions[j] - np.array(target_pos)
            ro_i = np.linalg.norm(vec)
            print(f"[Drone{j+1}] 計算値: ro_i = {ro_i:.2f} m")

        # --- ローカル座標系の定義: x軸=target方向, y軸=その直交方向 ---
        if ro_i > 0:
            e_r = vec / ro_i  # target方向の単位ベクトル（ローカルx軸）
            e_theta = np.array([-e_r[1], e_r[0]])  # ローカルy軸
            # ローカル座標系でtargetや隣接エージェントの情報を取得
            # targetの相対速度（ローカル）
            agent_velocity = (
                agent_positions[j] - animate.prev_agent_pos[j]
            ) / frame_time
            relative_velocity = agent_velocity - target_velocity
            relative_velocity_local = np.array(
                [np.dot(relative_velocity, e_r), np.dot(relative_velocity, e_theta)]
            )
            # 隣接エージェントのローカル角度
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
            theta_now_local = 0.0  # 自分自身から見たtarget方向は常に0
            # ローカル角速度
            if not hasattr(animate, "prev_theta_local"):
                animate.prev_theta_local = np.zeros(num_agents)
            omega_i_local = theta_now_local - animate.prev_theta_local[j]
            omega_i_local = (omega_i_local + np.pi) % (2 * np.pi) - np.pi
            animate.prev_theta_local[j] = theta_now_local
            # 隣接エージェントのローカル角速度
            if not hasattr(animate, "prev_theta_plus_local"):
                animate.prev_theta_plus_local = np.zeros(num_agents)
            if not hasattr(animate, "prev_theta_minus_local"):
                animate.prev_theta_minus_local = np.zeros(num_agents)
            omega_i_plus_local = theta_plus_local - animate.prev_theta_plus_local[j]
            omega_i_plus_local = (omega_i_plus_local + np.pi) % (2 * np.pi) - np.pi
            omega_i_minus_local = theta_minus_local - animate.prev_theta_minus_local[j]
            omega_i_minus_local = (omega_i_minus_local + np.pi) % (2 * np.pi) - np.pi
            animate.prev_theta_plus_local[j] = theta_plus_local
            animate.prev_theta_minus_local[j] = theta_minus_local
            # ローカル角距離
            alpha_i_local = abs(theta_plus_local - theta_now_local)
            alpha_i_minus_local = abs(theta_minus_local - theta_now_local)
            # --- 制御プロトコルu_iの計算（ローカル座標系） ---
            eta = relative_velocity_local[0]
            eta_norm = abs(eta)
    return (
        eta_norm,
        ro_i,
        omega_i_local,
        omega_i_plus_local,
        omega_i_minus_local,
        alpha_i_local,
        alpha_i_minus_local,
        e_r
    )
