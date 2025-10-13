import numpy as np
from connect_Coppelia import Simulation
from parameter import num_agents, frame_time, omega_target, radius_limit, radius
from various_calculation import Various
from caluculation import caluculate
from csv_save import set_csv_header, save_csv_data
import csv
from datetime import datetime

Japan_time = datetime.now()

set_csv_header(Japan_time)


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
        self.prev_prev_local_agent_positions = [
            pos.copy() for pos in self.prev_local_agent_positions
        ]
        self.target_theta = 0
        self.theta = []
        for i in range(num_agents):
            theta = i * np.pi / 3
            self.theta.append(theta)
        self.prev_theta = []
        for i in range(num_agents):
            prev_theta = i * np.pi / 3
            self.prev_theta.append(prev_theta)
        self.omega_i = [0, 0, 0, 0, 0, 0]
        self.omega_i_plus = [0, 0, 0, 0, 0, 0]
        self.omega_i_minus = [0, 0, 0, 0, 0, 0]
        self.alpha_i = []
        for i in range(num_agents):
            alpha_i = i * np.pi / 3
            self.alpha_i.append(alpha_i)
        self.alpha_i_minus = []
        for i in range(num_agents):
            alpha_i_minus = i * np.pi / 3
            self.alpha_i_minus.append(alpha_i_minus)
        self.current_world_agent_velocities = [[0, 0, 0] for _ in range(num_agents)]

    def animate(self, i):
        # ここから下はtargetの位置更新
        self.target_theta = omega_target * i * frame_time  # [rad]
        current_time = i * frame_time
        #print(f"現在の経過時間：{current_time}")
        # print(f"targetの角度: {self.target_theta}")
        target_x = radius * np.sin(self.target_theta)  # [m]
        target_y = radius * np.cos(self.target_theta)  # [m]
        self.target_position = [target_x, target_y, 2]
        # print(f"現在のtargetのWorld座標系の位置座標: {np.array(self.target_position)}")                                                                                                                   # 論文中のP_0(t)[m]
        self.target_velocity = np.array(
            [
                -radius * omega_target * np.cos(self.target_theta),  # x方向の速度成分
                -radius * omega_target * np.sin(self.target_theta),  # y方向の速度成分
            ]
        )  # [m/s]

        for j in range(num_agents):
            # ここから下はAgentの位置更新
            # j = i % num_agents
            j_plus = (j + 1) % num_agents
            j_minus = (j - 1) % num_agents
            print(f"現在のAgent[{j+1}]のWorld座標系の位置座標: {np.array(self.current_world_agent_positions[j])}")                          # 論文中のP_i(t)[m]

            self.local_agent_positions[j] = np.array(
                self.current_world_agent_positions[j]
            ) - np.array(
                self.target_position
            )  # targetから見たAgentの座標(x,y,zの要素3つ)
            # print(f"targetから見たAgent[{j + 1}]の座標: {self.local_agent_positions[j]}")                                             # vec # 論文中のP_bar_i(t)
            self.ro_i[j] = np.linalg.norm(
                self.local_agent_positions[j]
            )  # target-Agent間の距離(スカラー)
            # print(f"targetとAgent[{j+1}]の距離: {self.ro_i[j]}")                                                                    # 論文中のρ_i(t)

            self.theta[j] = self.various.Theta(self.local_agent_positions[j])
            # print(f"targetとAgent[{j+1}]とのなす角度: {self.theta[j]}")                                                                # 論文中のα[j]  # なす角を0~2πの範囲に

            # Agent[i]とAgent[i+1]の間の角距離(例: π/3とかπ/4など)

            self.alpha_i[j], self.alpha_i_minus[j] = self.various.Angular_distance(
                self.theta[j], self.theta[j_plus], self.theta[j_minus]
            )
            # print(f"Agent[{j+1}]とAgent[{j_plus+1}]の角距離: {self.alpha_i[j]}")                                                                                                                       # 論文中のα_hat[j]
            # print(f"Agent[{j+1}]とAgent[{j_minus+1}]の角距離: {self.alpha_i_minus[j]}")                                                                                                                # 論文中のα_hat[j_minus]

            agent_velocity = self.various.Velocity(
                self.current_world_agent_positions[j],
                self.prev_prev_world_agent_positions[j],
            )  # 論文中のv_i(t) 1ステップ差分に修正
            print(f"Agent[{j+1}]の速度: {agent_velocity}")  # ワールド座標系のAgentの速度

            # 論文の式(6)に従った相対速度の計算
            # ワールド座標系での相対速度を計算
            relative_velocity_world = -self.target_velocity + agent_velocity[:2]

            # ローカル座標系に変換（論文の式(5)の回転行列A_i(t)の逆行列を使用）
            # A_i(t) = [[cos(α_i), -sin(α_i)], [sin(α_i), cos(α_i)]]
            cos_alpha = np.cos(self.theta[j])
            sin_alpha = np.sin(self.theta[j])
            A_inv = np.array([[cos_alpha, sin_alpha], [-sin_alpha, cos_alpha]])
            relative_velocity = A_inv @ relative_velocity_world

            # print(f"ローカル座標系での相対速度: {relative_velocity}")                                                                     #別ファイルのrelative_velocity_rに当てはまる

            # print(np.array(self.prev_theta))
            self.omega_i[j] = relative_velocity[1]/self.ro_i[j]#self.various.Angular_velocity(self.theta[j], self.prev_theta[j])
            print(f"Agent[{j+1}]がtargetの周りを回る角速度: {self.omega_i[j]}")                                                                                                                           # 論文中のω_i[j]
            # 隣接Agentのtargetの周りを回る角速度(self.omega_iが更新されるごとにきちんと更新されている)
            # print(f"omega_i_plusを求める際に使う値: theta={self.theta[j_plus]} , prev_theta={self.prev_theta[j_plus]}")
            self.omega_i_plus[j] = np.copy(self.omega_i[j_plus])
            # print(f"Agent[{j_plus+1}]がtargetの周りを回る角速度: {self.omega_i_plus[j]}")
            # print(f"omega_i_minusを求める際に使う値: theta={self.theta[j_minus]} , prev_theta={self.prev_theta[j_minus]}")                                             # 論文中のω_i[j_plus]
            self.omega_i_minus[j] = np.copy(self.omega_i[j_minus])
            # print(f"Agent[{j_minus+1}]がtargetの周りを回る角速度: {self.omega_i_minus[j]}")                                                                                                                           # 論文中のω_i[j_minus]

            # print(f"targetから見たAgent[{j+1}]の前回のLocal座標系の位置: {np.array(self.prev_local_agent_positions[j])}")
            # print(f"targetから見たAgent[{j+1}]の前々回のLocal座標系の位置: {np.array(self.prev_prev_local_agent_positions[j])}")

            # 論文の式(5)に従ったローカル座標系の定義
            # x軸はターゲットからエージェントへの方向
            e_i_x = np.array(
                [
                    self.local_agent_positions[j][0] / self.ro_i[j],
                    self.local_agent_positions[j][1] / self.ro_i[j],
                ]
            )  # 論文中のe_i_x
            # y軸はx軸をπ/2回転（反時計回り）
            e_i_y = np.array([-e_i_x[1], e_i_x[0]])  # 論文中のe_i_y
            # print(f"ローカル座標系のx軸: {e_i_x}")
            # print(f"ローカル座標系のy軸: {e_i_y}")

            # print(f"targetの速度について: {self.target_velocity}")
            # print(f"Agent[{j+1}]の速度について: {agent_velocity[:2]}")

            # 論文の式(6)に従ったη_i（距離の時間微分）の計算
            eta = relative_velocity[0]  # ローカル座標系のx成分
            # print(f"targetとAgent[{j+1}]の距離の時間微分η_i: {eta}")
            # ro_iのスパイクを簡易検知（下側領域付近の挙動確認用）
            if self.ro_i[j] > 1.5 * radius:
                print(
                    f"[warn] ro_i spike: idx={j}, ro_i={self.ro_i[j]:.3f}, theta={self.theta[j]:.3f}"
                )

            u_r, u_theta = caluculate(
                i,
                j,
                self.alpha_i[j],
                self.alpha_i_minus[j],
                self.omega_i_plus[j],
                self.omega_i[j],
                self.omega_i_minus[j],
                self.ro_i[j],
                eta,
            )
            # print(f"Agent[{j+1}]のローカル制御入力: [u_r={u_r}, u_theta={u_theta}]")

            # 論文の式(5)に従ったローカル座標系からワールド座標系への変換
            # u_i(t) = A_i(t) * u^e_i(t)
            # ここでA_i(t)は回転行列
            cos_alpha = np.cos(self.theta[j])
            sin_alpha = np.sin(self.theta[j])
            A = np.array([[cos_alpha, -sin_alpha], [sin_alpha, cos_alpha]])

            # ローカル座標系での制御入力ベクトル
            u_local = np.array([u_r, u_theta])

            # ワールド座標系に変換
            u_world_2d = A @ u_local
            u_world = np.append(u_world_2d, 0)  # z成分を追加

            # print(f"ワールド座標系での制御入力: {u_world}")

            local_agent_velocity = self.various.coordinate_trans(
                self.theta[j], agent_velocity[:2]
            )
            # print(f"ローカル速度: {local_agent_velocity}")

            # 論文の式(2)に基づき、速度と位置を更新
            # v_new = v_old + u * dt
            new_velocity = (
                np.array(self.current_world_agent_velocities[j]) + u_world * frame_time
            )
            self.current_world_agent_velocities[j] = new_velocity.tolist()

            # p_new = p_old + v_new * dt
            updated_position = (
                np.array(self.current_world_agent_positions[j])
                + new_velocity * frame_time
            )
            self.current_world_agent_positions[j] = (
                updated_position.tolist()
            )  # 要素に追加

            # print(f"位置座標更新後のAgent[{j + 1}]のWorld座標系の位置: {np.array(self.current_world_agent_positions[j])}")

            # ここから上のself.prev_ro_iは前回のself.ro_iをコピーできてる
            self.prev_ro_i[j] = np.copy(self.ro_i[j])
            # print(f"前回のtargetとAgent[{j+1}]との距離を正しくコピーできているか確認: {self.prev_ro_i[j]}")
            self.prev_theta[j] = np.copy(self.theta[j])
            # print(f"前回のtargetとAgent[{j+1}]との角度を正しくコピーできているか確認: {self.prev_theta[j]}")
            self.prev_prev_local_agent_positions = np.copy(
                self.prev_local_agent_positions
            )
            # print(f"前回のtargetから見たAgent[{j+1}]の位置を正しくコピーできているか確認: {self.prev_prev_local_agent_positions[j]}")
            # ここから上はself.prev_agent_positionsは前回のself.aget_positionsをコピーできてる
            self.prev_local_agent_positions[j] = np.copy(self.local_agent_positions[j])
            # print(f"今回のtargetから見たAgent[{j+1}]の位置を正しくコピーできているか確認: {self.prev_local_agent_positions[j]}")
            self.prev_prev_world_agent_positions[j] = np.copy(
                self.prev_world_agent_positions[j]
            )
            #print(f"前回のAgent[{j+1}]の位置がコピーできているか確認: {self.prev_prev_world_agent_positions[j]}")
            self.prev_world_agent_positions[j] = np.copy(
                self.current_world_agent_positions[j]
            )
            #print(f"今回のAgent[{j+1}]の位置がコピーできているか確認: {self.prev_world_agent_positions[j]}")

            # print("\n")

        save_csv_data(Japan_time, current_time, self.ro_i, self.alpha_i, self.omega_i)

        """Coppeliasim上のAgentの位置同期"""
        # print(f"位置更新する際のAgentの位置: {np.array(self.current_world_agent_positions)}")
        # print(f"位置更新する際のtargetの位置: {np.array(self.target_position)}")
        self.sim.setAgentposition(j, self.current_world_agent_positions)
        self.sim.settargetposition(self.target_position)
        print("\n")
