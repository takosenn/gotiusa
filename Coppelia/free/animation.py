import numpy as np
from connect_Coppelia import Simulation
from parameter import num_agents, frame_time, omega_target, radius_limit, radius
from various_calculation import Various
from caluculation import caluculate
from csv_save import set_csv_header, save_csv_data
from datetime import datetime

"""現実時間の日本時間"""
Japan_time = datetime.now()

"""CSVのヘッダーを設定"""
set_csv_header(Japan_time, "ro_i")
set_csv_header(Japan_time, "theta")
set_csv_header(Japan_time, "alpha_i")
set_csv_header(Japan_time, "alpha_i_minus")
set_csv_header(Japan_time, "omega_i")
set_csv_header(Japan_time, "eta")
set_csv_header(Japan_time, "e_i_1")
set_csv_header(Japan_time, "e_i_2")
set_csv_header(Japan_time, "fi")


class Animation:
    def __init__(self):
        self.sim = Simulation()
        self.various = Various()
        self.ro_i = [
            radius_limit,
            radius_limit,
            radius_limit,
            radius_limit,
            radius_limit,
            radius_limit,
        ]  # [m]
        self.prev_ro_i = [
            radius_limit,
            radius_limit,
            radius_limit,
            radius_limit,
            radius_limit,
            radius_limit,
        ]
        self.target_position = [0, radius, 2]
        self.prev_target_position = self.target_position.copy()
        self.current_world_agent_positions = []
        for i in range(num_agents):
            current_world_agent_positions = [
                radius_limit * np.cos(i * np.pi / 3),
                radius + radius_limit * np.sin(i * np.pi / 3),
                2,
            ]
            self.current_world_agent_positions.append(current_world_agent_positions)
        self.prev_world_agent_positions = [
            pos.copy() for pos in self.current_world_agent_positions
        ]
        self.prev_prev_world_agent_positions = [
            pos.copy() for pos in self.prev_world_agent_positions
        ]
        self.local_agent_positions = []
        for i in range(num_agents):
            local_agent_positions = np.array(
                self.current_world_agent_positions[i] - np.array(self.target_position)
            )
            self.local_agent_positions.append(local_agent_positions)
        self.prev_local_agent_positions = [
            pos.copy() for pos in self.local_agent_positions
        ]
        self.target_theta = 0  # ターゲットの絶対角度
        self.theta = []
        for i in range(num_agents):
            theta = i * np.pi / 3
            self.theta.append(theta)
        self.prev_theta = self.theta.copy()
        self.omega_i = [0, 0, 0, 0, 0, 0]
        self.omega_i_plus = [0, 0, 0, 0, 0, 0]
        self.omega_i_minus = [0, 0, 0, 0, 0, 0]
        self.alpha_i = []
        for i in range(num_agents):
            alpha_i = i * np.pi / 3
            self.alpha_i.append(alpha_i)
        self.alpha_i_minus = self.alpha_i.copy()
        self.current_world_agent_velocities = [[0, 0, 0] for _ in range(num_agents)]
        self.e_i_1 = [0, 0, 0, 0, 0, 0]
        self.e_i_2 = [0, 0, 0, 0, 0, 0]
        self.eta = [0, 0, 0, 0, 0, 0]
        self.relative_velocity = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
        self.fi = [0, 0, 0, 0, 0, 0]

    def animate(self, i):
        # ここから下はtargetの位置更新
        self.target_theta = -omega_target * i * frame_time + np.pi / 2  # [rad]
        current_time = i * frame_time
        print(f"現在の経過時間：{current_time}")
        target_x = radius * np.cos(self.target_theta)  # [m]
        target_y = radius * np.sin(self.target_theta)  # [m]
        self.target_position = [target_x, target_y, 2]
        self.target_velocity = np.array(
            [
                (self.target_position[0] - self.prev_target_position[0])
                / frame_time,  # x方向の速度成分
                (self.target_position[1] - self.prev_target_position[1])
                / frame_time,  # y方向の速度成分
            ]
        )  # [m/s]

        # --- PHASE 1: 全エージェントについて theta, ro_i, eta, omega を計算（alphaは raw 値を集める） ---
        for j in range(num_agents):
            j_plus = (j + 1) % num_agents
            j_minus = (j - 1) % num_agents

            # ローカル座標系の位置・距離・角度
            self.local_agent_positions[j] = np.array(
                self.current_world_agent_positions[j]
            ) - np.array(self.target_position)
            self.ro_i[j] = np.linalg.norm(self.local_agent_positions[j])
            self.theta[j] = self.various.Theta(self.local_agent_positions[j])
            self.prev_theta[j] = self.various.Theta(self.prev_local_agent_positions[j])

            # 距離の時間差分（eta）
            self.eta[j] = (self.ro_i[j] - self.prev_ro_i[j]) / frame_time

            # 角速度 omega_i
            delta_theta = np.arctan2(
                np.sin(self.theta[j] - self.prev_theta[j]),
                np.cos(self.theta[j] - self.prev_theta[j]),
            )
            self.omega_i[j] = delta_theta / frame_time

        # raw alpha を全エージェント分計算（まだスケーリングはしない）
        for j in range(num_agents):
            j_plus = (j + 1) % num_agents
            j_minus = (j - 1) % num_agents
            alpha_raw, alpha_minus_raw = self.various.Angular_distance(
                self.theta[j], self.theta[j_plus], self.theta[j_minus]
            )
            self.alpha_i[j] = alpha_raw
            self.alpha_i_minus[j] = alpha_minus_raw

        # --- 正規化: 全体合計が 2π になるよう一度だけスケール ---
        total = sum(self.alpha_i)
        if total == 0:
            # 万が一全てゼロなら均等分配（安全策）
            uniform = 2 * np.pi / num_agents
            for j in range(num_agents):
                self.alpha_i[j] = uniform
                self.alpha_i_minus[j] = uniform
        else:
            scale = 2 * np.pi / total
            for j in range(num_agents):
                self.alpha_i[j] = self.alpha_i[j] * scale
                self.alpha_i_minus[j] = self.alpha_i_minus[j] * scale

        # --- PHASE 2: 各エージェントについて制御入力を計算し位置更新 ---
        for j in range(num_agents):
            j_plus = (j + 1) % num_agents
            j_minus = (j - 1) % num_agents

            # Agent のワールド速度（1ステップ差分）
            agent_velocity = self.various.Velocity(
                self.current_world_agent_positions[j],
                self.prev_world_agent_positions[j],
            )

            # 相対速度（ワールド座標系）とローカル変換
            relative_velocity_world = -self.target_velocity + agent_velocity[:2]
            cos_alpha = np.cos(self.theta[j])
            sin_alpha = np.sin(self.theta[j])
            A_inv = np.array([[cos_alpha, sin_alpha], [-sin_alpha, cos_alpha]])
            self.relative_velocity[j] = A_inv @ relative_velocity_world

            # 隣接の角速度
            self.omega_i_plus[j] = np.copy(self.omega_i[j_plus])
            self.omega_i_minus[j] = np.copy(self.omega_i[j_minus])

            # ローカル基底
            e_i_x = np.array(
                [
                    self.local_agent_positions[j][0] / self.ro_i[j],
                    self.local_agent_positions[j][1] / self.ro_i[j],
                ]
            )
            e_i_y = np.array([-e_i_x[1], e_i_x[0]])

            # caluculate に必要な引数を渡して制御入力を受け取る
            u_r, u_theta, self.e_i_1[j], self.e_i_2[j], self.fi[j] = caluculate(
                i,
                j,
                self.alpha_i[j],
                self.alpha_i_minus[j],
                self.omega_i_plus[j],
                self.omega_i[j],
                self.omega_i_minus[j],
                self.ro_i[j],
                self.eta[j],
            )

            # ローカル->ワールド変換して速度・位置更新
            A = np.array([[cos_alpha, -sin_alpha], [sin_alpha, cos_alpha]])
            u_local = np.array([u_r, u_theta])
            u_world_2d = A @ u_local
            u_world = np.append(u_world_2d, 0)

            new_velocity = u_world * frame_time + np.array(
                self.current_world_agent_velocities[j]
            )
            self.current_world_agent_velocities[j] = new_velocity.tolist()
            updated_position = (
                np.array(self.current_world_agent_positions[j])
                + new_velocity * frame_time
            )
            self.current_world_agent_positions[j] = updated_position.tolist()

            # 前回値の更新
            self.prev_ro_i[j] = np.copy(self.ro_i[j])
            self.prev_theta[j] = np.copy(self.theta[j])
            self.prev_local_agent_positions[j] = np.copy(self.local_agent_positions[j])
            self.prev_prev_world_agent_positions[j] = np.copy(
                self.prev_world_agent_positions[j]
            )
            self.prev_world_agent_positions[j] = np.copy(
                self.current_world_agent_positions[j]
            )

        self.prev_target_position = np.copy(self.target_position)

        # CSV 保存
        save_csv_data(Japan_time, current_time, self.ro_i, "ro_i")
        save_csv_data(Japan_time, current_time, self.alpha_i, "alpha_i")
        save_csv_data(Japan_time, current_time, self.alpha_i_minus, "alpha_i_minus")
        save_csv_data(Japan_time, current_time, self.omega_i, "omega_i")
        save_csv_data(Japan_time, current_time, self.eta, "eta")
        save_csv_data(Japan_time, current_time, self.e_i_1, "e_i_1")
        save_csv_data(Japan_time, current_time, self.e_i_2, "e_i_2")
        save_csv_data(Japan_time, current_time, self.theta, "theta")
        save_csv_data(Japan_time, current_time, self.fi, "fi")

        # Coppelia への同期
        self.sim.setAgentposition(j, self.current_world_agent_positions)
        self.sim.settargetposition(self.target_position)
        print("\n")