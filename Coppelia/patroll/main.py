from patroll import Patroll
from Encircle import Siege
from LineFormation import LineFormation
from connect_coppelia import Simulation
from parameter import Params
import numpy as np
import time
from csv_save import set_csv_header
from datetime import datetime

"""現実時間の日本時間"""
Japan_time = datetime.now()
# """CSVのヘッダーを設定"""
# set_csv_header(Japan_time, "ro_i")
# set_csv_header(Japan_time, "theta")
# set_csv_header(Japan_time, "alpha_i")
# set_csv_header(Japan_time, "alpha_i_minus")
# set_csv_header(Japan_time, "omega_i")
# set_csv_header(Japan_time, "eta")
# set_csv_header(Japan_time, "e_i_1")
# set_csv_header(Japan_time, "e_i_2")
# set_csv_header(Japan_time, "fi")


class Main:
    def __init__(self, num_agents, frame_time, target_position, agent_positions):
        self.sim = Simulation()
        # Simulationのハンドルを取得してからAnimationに同じインスタンスを渡す
        self.sim.get_handles()
        self.num_agents = num_agents
        self.frame_time = frame_time
        self.target_position = target_position
        self.agent_position = list(agent_positions)
        self.prev_agent_positions = np.array([pos[:] for pos in self.agent_position])
        self.prev_target_position = np.copy(self.target_position)
        self.distance = []
        for i in range(self.num_agents):
            distance = np.linalg.norm(
                np.array(self.agent_position[i]) - self.target_position
            )
            self.distance.append(distance)
        self.patroll = Patroll(
            num_agents, self.target_position, self.agent_position, self.distance
        )
        self.siege = Siege(
            num_agents,
            frame_time,
            self.target_position,
            self.agent_position,
            self.distance,
        )
        self.line_formation = LineFormation(
            num_agents,
            frame_time,
            self.target_position,
            self.agent_position,
            self.distance,
        )
        self.theta = np.zeros(self.num_agents)

    def run(self):
        try:
            self.sim.connect()
            self.sim.start_simulation()
            self.sim.initial_settargetposition(self.target_position)
            self.sim.initial_setAgentpositions(self.agent_position)
            time.sleep(2)
            k = 0
            m = 0
            for i in range(Params["frames"]):
                print(f"現在のfor文を読んだ回数: {i}回目")
                current_time = i * self.frame_time
                print(f"現在の経過時間：{current_time}")

                # ターゲット位置を更新
                self.target_position += np.array(
                    Params["target_distance_traveled"], dtype=float
                )  # targetの移動距離を変更可能parameter.py参照

                # 最小距離を取得
                min_distance = min(self.distance)
                # 最大距離を取得
                max_distance = max(self.distance)
                # Rの最大値を取得（リストの場合）
                max_R = (
                    max(Params["R"]) if isinstance(Params["R"], list) else Params["R"]
                )

                # 距離判定：3つのモードを切り替え
                # 1. min_distance > distance_threshold: Patroll（巡回）
                # 2. 2*max_R < min_distance <= distance_threshold: LineFormation（直線配置）
                # 3. min_distance <= 2*max_R: Encircle（円形包囲）

                if min_distance > Params["distance_threshold"]:
                    # モード1: 通常時巡回
                    print(f"Patrollモード")
                    self.distance, self.prev_agent_positions, self.agent_position = (
                        self.patroll.animate()
                    )
                    # Patrollクラスのターゲット位置も更新
                    self.patroll.target_position = self.target_position
                    # 距離を再計算（ターゲットが移動したので）
                    for j in range(self.num_agents):
                        self.distance[j] = np.linalg.norm(
                            np.array(self.agent_position[j]) - self.target_position
                        )
                    print(
                        f"距離: {[f'{d:.2f}' for d in self.distance]}, 閾値: {Params['distance_threshold']}"
                    )

                elif (
                    max_distance > 5
                    and min_distance <= Params["distance_threshold"]
                ):
                    # モード2: 直線配置（ターゲットの進行方向に垂直）
                    k += 1
                    print(
                        f"LineFormationモード (距離: {min_distance:.2f}m, 閾値: 2*R={2*max_R:.2f}m)"
                    )
                    (
                        self.agent_position,
                        self.prev_agent_positions,
                        self.distance,
                    ) = self.line_formation.animate(
                        self.target_position,
                        self.prev_target_position,
                        self.agent_position,
                        self.prev_agent_positions,
                    )
                    if k % 10 == 0:
                        sorted_idx = sorted(
                            range(self.num_agents),
                            key=lambda j: self.theta[j],  # ,reverse = True
                        )
                        print(f"ハンドルを切り替える (sorted_idx={sorted_idx})")
                        # 切替: シミュレータ内ハンドルを入れ替え
                        self.sim.change_handles(sorted_idx)

                        # --- 追加: アプリ側の状態も同じ順序に並び替える ---
                        # agent_position
                        if isinstance(self.agent_position, np.ndarray):
                            self.agent_position = self.agent_position.tolist()
                        self.agent_position = [
                            self.agent_position[idx] for idx in sorted_idx
                        ]

                        # prev_agent_positions
                        try:
                            self.prev_agent_positions = np.array(
                                [self.prev_agent_positions[idx] for idx in sorted_idx]
                            )
                        except Exception:
                            self.prev_agent_positions = np.array(
                                [
                                    self.prev_agent_positions[idx].tolist()
                                    for idx in sorted_idx
                                ]
                            )

                        # distance と theta
                        self.distance = [self.distance[idx] for idx in sorted_idx]
                        try:
                            self.theta = [self.theta[idx] for idx in sorted_idx]
                        except Exception:
                            self.theta = list(self.theta)

                        # Siege と Patroll の内部状態も並び替え
                        try:
                            self.siege.reorder(sorted_idx)
                        except Exception as e:
                            print(f"警告: siege.reorder の実行に失敗しました: {e}")
                        try:
                            self.patroll.reorder(sorted_idx)
                        except Exception as e:
                            print(f"警告: patroll.reorder の実行に失敗しました: {e}")
                        try:
                            self.line_formation.reorder(sorted_idx)
                        except Exception as e:
                            print(
                                f"警告: line_formation.reorder の実行に失敗しました: {e}"
                            )

                        # 切り替え直後に位置を再設定して瞬間移動を防ぐ
                        self.sim.setAgentposition(self.agent_position)
                    print(f"距離: {[f'{d:.2f}' for d in self.distance]}")

                else:
                    # モード3: 円形包囲
                    m += 1
                    # kが50増えるごとに Params['Omega'] を指定シーケンスで切り替える
                    if m % 30 == 0:
                        # 三角波: 2,3,4,3,2,... を繰り返す
                        seq_index = (m // 50 - 1) % len(Params["omega_seq"])
                        Params["Omega"] = Params["omega_seq"][seq_index]
                        print(
                            f"Params['Omega'] を {Params['Omega']} に変更しました (m={m})"
                        )
                    print(f"Encircleモード (m={m})")
                    (
                        self.agent_position,
                        self.prev_agent_positions,
                        self.distance,
                        self.theta,
                    ) = self.siege.animate(
                        i,
                        Japan_time,
                        current_time,
                        self.agent_position,
                        self.prev_agent_positions,
                        self.prev_target_position,
                        self.target_position,
                    )
                    if m % 20 == 0:
                        sorted_idx = sorted(
                            range(self.num_agents), key=lambda j: self.theta[j]
                        )
                        print(f"ハンドルを切り替える (sorted_idx={sorted_idx})")
                        # 切替: シミュレータ内ハンドルを入れ替え
                        self.sim.change_handles(sorted_idx)

                        # --- 追加: アプリ側の状態も同じ順序に並び替える ---
                        # agent_position
                        if isinstance(self.agent_position, np.ndarray):
                            self.agent_position = self.agent_position.tolist()
                        self.agent_position = [
                            self.agent_position[idx] for idx in sorted_idx
                        ]

                        # prev_agent_positions
                        try:
                            self.prev_agent_positions = np.array(
                                [self.prev_agent_positions[idx] for idx in sorted_idx]
                            )
                        except Exception:
                            self.prev_agent_positions = np.array(
                                [
                                    self.prev_agent_positions[idx].tolist()
                                    for idx in sorted_idx
                                ]
                            )

                        # distance と theta
                        self.distance = [self.distance[idx] for idx in sorted_idx]
                        try:
                            self.theta = [self.theta[idx] for idx in sorted_idx]
                        except Exception:
                            self.theta = list(self.theta)

                        # Siege と Patroll の内部状態も並び替え
                        try:
                            self.siege.reorder(sorted_idx)
                        except Exception as e:
                            print(f"警告: siege.reorder の実行に失敗しました: {e}")
                        try:
                            self.patroll.reorder(sorted_idx)
                        except Exception as e:
                            print(f"警告: patroll.reorder の実行に失敗しました: {e}")
                        try:
                            self.line_formation.reorder(sorted_idx)
                        except Exception as e:
                            print(
                                f"警告: line_formation.reorder の実行に失敗しました: {e}"
                            )

                        # 切り替え直後に位置を再設定して瞬間移動を防ぐ
                        self.sim.setAgentposition(self.agent_position)

                # prev_target_positionを更新
                self.prev_target_position = np.copy(self.target_position)

                # エージェント位置を更新
                if isinstance(self.agent_position, list):
                    self.sim.setAgentposition(self.agent_position)
                else:
                    self.sim.setAgentposition(self.agent_position.tolist())
                # ターゲット位置を更新
                if isinstance(self.target_position, list):
                    self.sim.settargetposition(self.target_position)
                else:
                    self.sim.settargetposition(self.target_position.tolist())
                time.sleep(Params["frame_time"])
                self.sim.step_simulation()
        except KeyboardInterrupt:
            print("ctrl+Cが押されました。")
        finally:
            self.sim.stop_simulation()


controller = Main(
    num_agents=Params["num_agents"],
    frame_time=Params["frame_time"],
    target_position=Params[
        "target_position"
    ],  # targetの初期位置を変更可能parameter.py参照
    agent_positions=Params["agent_position"],
)
controller.run()
