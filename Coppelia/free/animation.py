import numpy as np
from connect_Coppelia import Simulation
from parameter import Params
from various_calculation import Various
from caluculation import caluculate
from csv_save import set_csv_header, save_csv_data
from datetime import datetime

"""現実時間の日本時間"""
Japan_time = datetime.now()

"""CSVのヘッダーを設定（CSV保存が有効な場合のみ）"""
if Params["save_csv"]:
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
        self.initialized = False  # 初期化フラグ
        # 初期値は仮の値で設定（最初のanimate呼び出しで実座標から初期化される）
        self.ro_i = [0.0] * Params["num_agents"]
        self.prev_ro_i = [0.0] * Params["num_agents"]
        self.target_position = [0, 0, 0]
        self.prev_target_position = [0, 0, 0]
        self.current_world_agent_positions = [
            [0, 0, 0] for _ in range(Params["num_agents"])
        ]
        self.prev_world_agent_positions = [
            [0, 0, 0] for _ in range(Params["num_agents"])
        ]
        self.prev_prev_world_agent_positions = [
            [0, 0, 0] for _ in range(Params["num_agents"])
        ]
        self.local_agent_positions = [[0, 0, 0] for _ in range(Params["num_agents"])]
        self.prev_local_agent_positions = [
            [0, 0, 0] for _ in range(Params["num_agents"])
        ]
        self.target_theta = 0  # ターゲットの絶対角度
        self.theta = [0.0] * Params["num_agents"]
        self.prev_theta = [0.0] * Params["num_agents"]
        self.omega_i = [0.0] * Params["num_agents"]
        self.omega_i_plus = [0.0] * Params["num_agents"]
        self.omega_i_minus = [0.0] * Params["num_agents"]
        self.alpha_i = [0.0] * Params["num_agents"]
        self.alpha_i_minus = [0.0] * Params["num_agents"]
        self.current_world_agent_velocities = [
            [0, 0, 0] for _ in range(Params["num_agents"])
        ]
        self.e_i_1 = [0.0] * Params["num_agents"]
        self.e_i_2 = [0.0] * Params["num_agents"]
        self.eta = [0.0] * Params["num_agents"]
        self.relative_velocity = [[0, 0] for _ in range(Params["num_agents"])]
        self.fi = [0.0] * Params["num_agents"]

    def animate(self, i, target_position_from_sim, agent_positions_from_sim):
        # CoppeliaSim から取得した座標を使用
        current_time = i * Params["frame_time"]
        print(f"現在の経過時間：{current_time}")

        # 初回呼び出し時（i==0）に実座標から初期化
        if not self.initialized:
            print("CoppeliaSim から取得した実座標で初期化中...")
            self.target_position = list(target_position_from_sim)
            self.prev_target_position = self.target_position.copy()

            for j in range(Params["num_agents"]):
                self.current_world_agent_positions[j] = list(
                    agent_positions_from_sim[j]
                )
                self.prev_world_agent_positions[j] = list(agent_positions_from_sim[j])
                self.prev_prev_world_agent_positions[j] = list(
                    agent_positions_from_sim[j]
                )

                # ro_i と prev_ro_i を実座標から計算
                local_pos = np.array(agent_positions_from_sim[j]) - np.array(
                    target_position_from_sim
                )
                self.local_agent_positions[j] = local_pos
                self.prev_local_agent_positions[j] = local_pos.copy()
                distance = np.linalg.norm(local_pos)
                self.ro_i[j] = distance
                self.prev_ro_i[j] = distance

                # theta の初期値を計算
                self.theta[j] = self.various.Theta(local_pos)
                self.prev_theta[j] = self.theta[j]

                print(
                    f"  Agent[{j}]: 初期距離 ro_i = {distance:.3f} m, 初期角度 theta = {self.theta[j]:.3f} rad"
                )

            self.initialized = True
            print("初期化完了\n")

        # CoppeliaSim から取得した target の位置を使用
        self.target_position = list(target_position_from_sim)
        self.target_velocity = np.array(
            [
                (self.target_position[0] - self.prev_target_position[0])
                / Params["frame_time"],  # x方向の速度成分
                (self.target_position[1] - self.prev_target_position[1])
                / Params["frame_time"],  # y方向の速度成分
            ]
        )  # [m/s]

        # CoppeliaSim から取得した Agent の位置を使用
        for j in range(Params["num_agents"]):
            self.current_world_agent_positions[j] = list(agent_positions_from_sim[j])

        # --- PHASE 1: 全エージェントについて theta, ro_i, eta, omega を計算（alphaは raw 値を集める） ---
        for j in range(Params["num_agents"]):
            j_plus = (j + 1) % Params["num_agents"]
            j_minus = (j - 1) % Params["num_agents"]

            # ローカル座標系の位置・距離・角度
            self.local_agent_positions[j] = np.array(
                self.current_world_agent_positions[j]
            ) - np.array(self.target_position)
            self.ro_i[j] = np.linalg.norm(self.local_agent_positions[j])
            self.theta[j] = self.various.Theta(self.local_agent_positions[j])
            self.prev_theta[j] = self.various.Theta(self.prev_local_agent_positions[j])

            # 距離の時間差分（eta）
            self.eta[j] = (self.ro_i[j] - self.prev_ro_i[j]) / Params["frame_time"]

            # 角速度 omega_i
            delta_theta = np.arctan2(
                np.sin(self.theta[j] - self.prev_theta[j]),
                np.cos(self.theta[j] - self.prev_theta[j]),
            )
            self.omega_i[j] = delta_theta / Params["frame_time"]

        # raw alpha を全エージェント分計算（まだスケーリングはしない）
        for j in range(Params["num_agents"]):
            j_plus = (j + 1) % Params["num_agents"]
            j_minus = (j - 1) % Params["num_agents"]
            alpha_raw, alpha_minus_raw = self.various.Angular_distance(
                self.theta[j], self.theta[j_plus], self.theta[j_minus]
            )
            self.alpha_i[j] = alpha_raw
            self.alpha_i_minus[j] = alpha_minus_raw

        # --- 正規化: 全体合計が 2π になるよう一度だけスケール ---
        total = sum(self.alpha_i)
        if total == 0:
            # 万が一全てゼロなら均等分配（安全策）
            uniform = 2 * np.pi / Params["num_agents"]
            for j in range(Params["num_agents"]):
                self.alpha_i[j] = uniform
                self.alpha_i_minus[j] = uniform
        else:
            scale = 2 * np.pi / total
            for j in range(Params["num_agents"]):
                self.alpha_i[j] = self.alpha_i[j] * scale
                self.alpha_i_minus[j] = self.alpha_i_minus[j] * scale

        # --- PHASE 2: 各エージェントについて制御入力を計算し位置更新 ---
        for j in range(Params["num_agents"]):
            j_plus = (j + 1) % Params["num_agents"]
            j_minus = (j - 1) % Params["num_agents"]

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

            new_velocity = u_world * Params["frame_time"] + np.array(
                self.current_world_agent_velocities[j]
            )
            self.current_world_agent_velocities[j] = new_velocity.tolist()
            updated_position = (
                np.array(self.current_world_agent_positions[j])
                + new_velocity * Params["frame_time"]
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

        # CSV 保存（保存が有効な場合のみ）
        if Params["save_csv"]:
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
