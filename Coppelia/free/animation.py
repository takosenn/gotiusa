import numpy as np
from connect_Coppelia import Simulation
from parameter import Params
from various_calculation import Various
from caluculation import caluculate
from csv_save import set_csv_header, save_csv_data, set_error_csv_header
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
    set_error_csv_header(Japan_time)  # 誤差データ用のヘッダーを追加


class Animation:
    def __init__(self):
        self.sim = Simulation()
        self.various = Various()
        self.initialized = False  # 初期化フラグ
        self.target_initial_z = 0  # z座標の初期値（後で設定）
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
        self.fi = [0.0] * Params["num_agents"]
        self.agent_index_mapping = list(
            range(Params["num_agents"])
        )  # theta順のインデックスマッピング
        self.mapping_initialized = False  # マッピングが初期化されたか
        self.sort_interval = 30  # theta順ソートの更新間隔（ステップ）
        self.last_sort_step = -1  # 最後にソートを実行したステップ

    def animate(self, i, target_position_from_sim, agent_positions_from_sim):
        # CoppeliaSim から取得した座標を使用
        current_time = i * Params["frame_time"]
        print(f"現在の経過時間：{current_time}")

        # 初回呼び出し時（i==0）に実座標から初期化
        if not self.initialized:
            print("CoppeliaSim から取得した実座標で初期化中...")
            # ターゲットのz座標を取得
            self.target_initial_z = target_position_from_sim[2]
            # ターゲットの初期位置をCoppeliaSimから取得した位置に設定
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
                distance = self.various.Distance(local_pos)
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

        # ターゲットの位置を更新（CoppeliaSim から取得した位置を使用）
        # main.pyで位置が更新されているため、そのまま使用
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
            self.ro_i[j] = self.various.Distance(self.local_agent_positions[j])
            self.theta[j] = self.various.Theta(self.local_agent_positions[j])
            self.prev_theta[j] = self.various.Theta(self.prev_local_agent_positions[j])

            # 距離の時間差分（eta）
            self.eta[j] = (self.ro_i[j] - self.prev_ro_i[j]) / Params["frame_time"]

            # 角速度 omega_i
            self.omega_i[j] = self.various.Angular_velocity(
                self.theta[j], self.prev_theta[j]
            )

        # theta値でエージェントをソートして、インデックスマッピングを作成（30ステップごと）
        if (
            not self.mapping_initialized
            or (i - self.last_sort_step) >= self.sort_interval
        ):
            theta_with_index = [(j, self.theta[j]) for j in range(Params["num_agents"])]
            theta_with_index.sort(key=lambda x: x[1])  # theta値でソート（小さい順）

            # ソート結果をマッピングに格納
            # self.agent_index_mapping[論理インデックス] = 実際のエージェントインデックス
            self.agent_index_mapping = [agent_idx for agent_idx, _ in theta_with_index]

            if not self.mapping_initialized:
                print(
                    "\n--- 円形フォーメーション: theta順のエージェント割り当て（初回） ---"
                )
            else:
                print(
                    f"\n--- ステップ{i}: theta順のエージェント割り当て（再ソート） ---"
                )

            for logical_idx in range(Params["num_agents"]):
                actual_idx = self.agent_index_mapping[logical_idx]
                print(
                    f"  論理Agent[{logical_idx}] = 実際のAgent[{actual_idx}], theta={self.theta[actual_idx]:.3f} rad"
                )
            print()

            self.mapping_initialized = True
            self.last_sort_step = i

        # raw alpha を全エージェント分計算（theta順に基づいて隣接関係を決定）
        for logical_j in range(Params["num_agents"]):
            actual_j = self.agent_index_mapping[logical_j]
            logical_j_plus = (logical_j + 1) % Params["num_agents"]
            logical_j_minus = (logical_j - 1) % Params["num_agents"]
            actual_j_plus = self.agent_index_mapping[logical_j_plus]
            actual_j_minus = self.agent_index_mapping[logical_j_minus]

            alpha_raw, alpha_minus_raw = self.various.Angular_distance(
                self.theta[actual_j],
                self.theta[actual_j_plus],
                self.theta[actual_j_minus],
            )
            self.alpha_i[actual_j] = alpha_raw
            self.alpha_i_minus[actual_j] = alpha_minus_raw

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
        for logical_j in range(Params["num_agents"]):
            actual_j = self.agent_index_mapping[logical_j]
            logical_j_plus = (logical_j + 1) % Params["num_agents"]
            logical_j_minus = (logical_j - 1) % Params["num_agents"]
            actual_j_plus = self.agent_index_mapping[logical_j_plus]
            actual_j_minus = self.agent_index_mapping[logical_j_minus]

            # Agent のワールド速度（1ステップ差分）
            agent_velocity = self.various.Velocity(
                self.current_world_agent_positions[actual_j],
                self.prev_world_agent_positions[actual_j],
            )

            # 隣接の角速度
            self.omega_i_plus[actual_j] = np.copy(self.omega_i[actual_j_plus])
            self.omega_i_minus[actual_j] = np.copy(self.omega_i[actual_j_minus])

            # caluculate に必要な引数を渡して制御入力を受け取る
            (
                u_r,
                u_theta,
                self.e_i_1[actual_j],
                self.e_i_2[actual_j],
                self.fi[actual_j],
            ) = caluculate(
                i,
                actual_j,
                self.alpha_i[actual_j],
                self.alpha_i_minus[actual_j],
                self.omega_i_plus[actual_j],
                self.omega_i[actual_j],
                self.omega_i_minus[actual_j],
                self.ro_i[actual_j],
                self.eta[actual_j],
                logical_j,  # 論理インデックス（theta順）を渡す
            )

            # ローカル->ワールド変換して速度・位置更新
            u_world_2d = self.various.coordinate_trans(
                self.theta[actual_j], [u_r, u_theta]
            )
            u_world = np.append(u_world_2d, 0)

            new_velocity = u_world * Params["frame_time"] + np.array(
                self.current_world_agent_velocities[actual_j]
            )
            self.current_world_agent_velocities[actual_j] = new_velocity.tolist()
            updated_position = (
                np.array(self.current_world_agent_positions[actual_j])
                + new_velocity * Params["frame_time"]
            )
            self.current_world_agent_positions[actual_j] = updated_position.tolist()

            # 前回値の更新
            self.prev_ro_i[actual_j] = np.copy(self.ro_i[actual_j])
            self.prev_theta[actual_j] = np.copy(self.theta[actual_j])
            self.prev_local_agent_positions[actual_j] = np.copy(
                self.local_agent_positions[actual_j]
            )
            self.prev_prev_world_agent_positions[actual_j] = np.copy(
                self.prev_world_agent_positions[actual_j]
            )
            self.prev_world_agent_positions[actual_j] = np.copy(
                self.current_world_agent_positions[actual_j]
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
        # ターゲット位置の反映はmain.pyで行うため、ここでは不要
        print("\n")
