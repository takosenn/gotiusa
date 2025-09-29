import numpy as np
import time
from various_calculation import (
    coordinate_trans,
    omega_i_local_calculation,
    Coordinate_Correction,
    velocity_calculation,
)
from parameter import (
    center,
    radius,
    max_speed,
    random_walk_sigma,
    frame_time,
    R,
    num_agents,
    d_i,
    target_pos,
    target_velocity,
    radius_limit,
)
from calculation import calculate_u
from DataStrage import e_i_1_integral, e_i_2_integral
import math
from simulation import Simulation


class Animation:
    def __init__(self):
        self.sim = Simulation()
        self.agent_positions = np.array(
            [
                (
                    center[0] + radius_limit * math.cos(2 * np.pi * i / num_agents),
                    center[1] + radius_limit * math.sin(2 * np.pi * i / num_agents),
                )
                for i in range(num_agents)
            ]
        )
        self.prev_agent_positions = self.agent_positions.copy()
        self.omega_i_local = np.zeros(num_agents)
        self.omega_i_plus_local = np.zeros(num_agents)
        self.omega_i_minus_local = np.zeros(num_agents)
        self.alpha_i_local = np.zeros(num_agents)

    def animate(self, i):
        if i == 0:
            self.sim.get_handles()
        global target_pos, target_velocity
        # targetのランダムウォーク
        # 速度にランダムな変化を加える。一瞬で枠外に飛び出さないように
        target_velocity += np.random.normal(0, random_walk_sigma, size=2)
        # 最大速度制限
        speed = np.linalg.norm(target_velocity)
        if speed > max_speed:
            target_velocity = max_speed

        # 位置を更新
        target_pos += target_velocity * frame_time

        for j in range(num_agents):

            # 隣接エージェントの番号
            idx_plus = (j + 1) % num_agents
            idx_minus = (j - 1) % num_agents

            ro_i = self.sim.get_visionSensor_distance(j)  # targetまでの距離
            print(f"visionSensorの距離測定に成功しました: 距離 = {ro_i:.3f} [m]")
            world_pos = np.round(
                self.sim.coodinate_target(j), 2
            )  # targetから見た自身の位置
            # print(f"Agent{j+1} visionSensor 座標変換成功: 座標 =[{world_pos[0]:.2f}, {world_pos[1]:.2f}]")

            Yaw = self.sim.visionSenor_orientation(
                j, world_pos
            )  # targetから見た自身のYaw角
            print(f"Agent{j+1}のいるべき角度: {Yaw/np.pi}π")
            time.sleep(0.5)

            # e_r[0]はcosでx成分、e_r[1]はsinでy成分
            e_r = (
                world_pos[0] / math.sqrt(world_pos[0] ** 2 + world_pos[1] ** 2),
                world_pos[1] / math.sqrt(world_pos[0] ** 2 + world_pos[1] ** 2),
            )

            # ローカル座標系の定義: x軸=target方向, y軸=その直交方向
            e_theta = np.array([-e_r[1], e_r[0]])  # ローカルy軸
            # ローカル座標系でtargetや隣接エージェントの情報を取得
            # targetの相対速度（ローカル）
            coordinate_correction = Coordinate_Correction(Yaw)  # 位置座標補正
            self.agent_positions[j] = world_pos[:2] + coordinate_correction
            print(
                f"Agent{j+1} visionSensor 座標変換成功: 座標 =[{self.agent_positions[j][0]:.2f}, {self.agent_positions[j][1]:.2f}]"
            )
            # print(f"これはself.agent_positionsです{self.agent_positions[j]}")
            print(
                f"前回の位置座標: [{self.prev_agent_positions[j][0]:.2f}, {self.prev_agent_positions[j][1]:.2f}]"
            )

            agent_velocity = velocity_calculation(
                self.agent_positions[j], self.prev_agent_positions[j]
            )
            print(
                f"これはAgent{j+1}の速度: [{agent_velocity[0]:.2f}, {agent_velocity[1]:.2f}]"
            )

            # 相対速度を計算(world_posは対象から見た自身の位置なので、速度はそのまま使える)
            relative_velocity = agent_velocity - target_velocity
            print(f"これはrelative_velocityです{relative_velocity}")
            # np.dot(relative_velocity, e_r)は接近・離反成分、np.dot(relative_velocity, e_theta)は周回・回転成分
            relative_velocity_local = np.array(
                [np.dot(relative_velocity, e_r), np.dot(relative_velocity, e_theta)]
            )
            print(f"これはrelative_velocity_localです{relative_velocity_local}")

            # 隣接エージェントの位置ベクトル(Agent[j+1]とAgent[j]との差)
            vec_plus = self.agent_positions[idx_plus] - self.agent_positions[j]
            vec_minus = self.agent_positions[idx_minus] - self.agent_positions[j]

            # ローカル角度
            # theta_plus_local = np.arctan2(np.dot(vec_plus, e_theta), np.dot(vec_plus, e_r))
            # print(f"これはtheta_plus_localです{theta_plus_local}")
            # theta_minus_local = np.arctan2(np.dot(vec_minus, e_theta), np.dot(vec_minus, e_r))
            # print(f"これはtheta_minus_localです{theta_minus_local}")
            ##theta_now_local = 0.0  # 自分自身から見たtarget方向は常に0
            # ローカル角速度 omega_i_local
            self.omega_i_local[j] = omega_i_local_calculation(ro_i, relative_velocity_local[1])
            # print(f"これは{self.omega_i_local[j]}")
            # prev_theta_local[j] = theta_now_local
            # 隣接エージェントのローカル角速度
            # omega_i_plus_local = theta_plus_local - prev_theta_plus_local[j]
            self.omega_i_plus_local[j] = self.omega_i_local[idx_plus]
            print(f"これはself.omega_i_plus_localです{self.omega_i_plus_local[j]}")
            # omega_i_minus_local = theta_minus_local - prev_theta_minus_local[j]
            self.omega_i_minus_local[j] = self.omega_i_local[idx_minus]
            print(f"これはself.omega_i_minus_localです{self.omega_i_minus_local[j]}")
            # prev_theta_local[] = theta_plus_local
            # prev_theta_minus_local[j] = theta_minus_local

            
            print(f"Agent[{idx_plus}]の位置: {self.agent_positions[idx_plus]}")
            print(f"Agent[{idx_minus}]の位置: {self.agent_positions[idx_minus]}")

            # ローカル角距離
            self.alpha_i_local = -np.arctan2(
                self.agent_positions[j][1], self.agent_positions[j][0]
            ) + np.arctan2(
                self.agent_positions[idx_plus][1], self.agent_positions[idx_plus][0]
            )
            print(f"Agent[{idx_plus}]との角距離: {self.alpha_i_local}")
            alpha_i_minus_local = np.arctan2(
                self.agent_positions[j][1], self.agent_positions[j][0]
            ) - np.arctan2(
                self.agent_positions[idx_minus][1], self.agent_positions[idx_minus][0]
            )
            print(f"Agent[{idx_minus}]との角距離: {alpha_i_minus_local}")
            # --- 制御プロトコルu_iの計算（ローカル座標系） ---
            eta = relative_velocity_local[0]  # relative_velocity_local[0]は接近・離反成分
            eta_norm = eta
            print(f"これはeta_normです{eta_norm}")
            # eta_norm = abs(eta)
            u = calculate_u(
                d_i,
                ro_i,
                self.omega_i_local[j],
                self.omega_i_plus_local[j],
                self.omega_i_minus_local[j],
                self.alpha_i_local,
                alpha_i_minus_local,
                eta_norm,
                e_i_1_integral,
                e_i_2_integral,
                j,
                i,
            )

            # --- ローカル→グローバル変換 ---
            theta_global = np.arctan2(e_r[1], e_r[0])
            u_vec = coordinate_trans(theta_global, u)
            print(f"Agent{j+1}の加速度: [{u_vec[0]}[m/s^2], {u_vec[1]}[m/s^2]]です")

            # 位置を仮更新
            new_pos = self.agent_positions[j] + u_vec * frame_time**2
            print(f"これはAgent{j+1}の新しい位置{new_pos}です")
            # targetとの距離を計算
            dist_to_target = np.linalg.norm(new_pos - target_pos)
            new_agent_positions = np.zeros((num_agents, 2))
            if dist_to_target >= R:
                new_agent_positions[j] = new_pos
            else:
                # R未満なら、targetから距離Rの位置に補正
                direction = (new_pos) / np.linalg.norm(new_pos)
                new_agent_positions[j] = direction * R

            Agents_pos_3d = [
                new_agent_positions[j][0],
                new_agent_positions[j][1],
                2.0,
            ]
            self.sim.set_agent_position(j, Agents_pos_3d)
            #agent_velocity_coppelia = self.sim.drone_speed(j)
            #print(agent_velocity_coppelia)
            
            # Coppeliasim側でtargetの緑の球(target)の位置同期
            target_pos_3d = [target_pos[0], target_pos[1], 2.0]
            self.sim.set_target_position(target_pos_3d)
            Yaw = self.sim.visionSenor_orientation(
                j, world_pos
            )  # targetから見た自身のYaw角
            print(f"\n\n")
            self.sim.step_simulation()
            time.sleep(0.5)

        self.prev_agent_positions = self.agent_positions.copy()
