from patroll import Patroll
from Encircle import Siege
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
        self.theta = np.zeros(self.num_agents)

    def run(self):
        try:
            self.sim.connect()
            self.sim.start_simulation()
            self.sim.initial_settargetposition(self.target_position)
            self.sim.initial_setAgentpositions(self.agent_position)
            time.sleep(2)
            k = 0
            for i in range(Params["frames"]):
                print(f"現在のfor文を読んだ回数: {i}回目")
                current_time = i * self.frame_time
                print(f"現在の経過時間：{current_time}")

                # ターゲット位置を更新
                self.target_position += np.array([-0.05, -0.05, 0], dtype=float)
                self.prev_target_position = np.copy(self.target_position)

                # 距離判定
                if any(
                    d <= Params["distance_threshold"] for d in self.distance
                ):  # 一つでも距離が閾値以下になったとき対象を囲む
                    k += 1
                    print(f"Encircleモード (k={k})")
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
                    if k == 1 or k == 100:
                        sorted_idx = sorted(
                            range(self.num_agents), key=lambda j: self.theta[j]
                        )
                        print(f"ハンドルを切り替える (sorted_idx={sorted_idx})")
                        self.sim.change_handles(sorted_idx)
                else:  # 通常時巡回
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
    target_position=Params["target_position"],
    agent_positions=Params["agent_position"],
)
controller.run()
