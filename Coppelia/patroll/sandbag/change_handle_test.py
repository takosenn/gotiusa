import time
from connect_coppelia import Simulation
from parameter import Params


class Main:
    def __init__(self, agent_positions):
        self.sim = Simulation()
        self.sim.get_handles()
        self.agent_positions = list(agent_positions)
        self.k = 0
        self.direction = [0.0, 0.15, -0.15, -0.1, 0.1, 0.0]

    def animate(self):
        try:
            self.sim.connect()
            self.sim.start_simulation()
            self.sim.initial_setAgentpositions(Params["agent_position"])
            time.sleep(2)
            for i in range(Params["frames"]):
                print(f"現在のfor文を読んだ回数: {i+1}回目")
                self.agent_positions[0][0] += self.direction[0]
                self.agent_positions[1][0] += self.direction[1]
                self.agent_positions[2][0] += self.direction[2]
                self.agent_positions[3][0] += self.direction[3]
                self.agent_positions[4][0] += self.direction[4]
                self.agent_positions[5][0] += self.direction[5]
                self.k += 1
                if self.k % 20 == 0:
                    # k が 20 の倍数ごとに x座標の小さい順にソート
                    # sorted() で インデックス番号 のリストを取得
                    sorted_idx = sorted(
                        range(Params["num_agents"]),
                        key=lambda i: self.agent_positions[i][0],
                    )
                    print(f"ハンドルを切り替える (k={self.k}, sorted_idx={sorted_idx})")
                    self.sim.change_handles(sorted_idx)

                    # 位置データも sorted_idx に従って並び替える
                    old_positions = [pos.copy() for pos in self.agent_positions]
                    for j in range(Params["num_agents"]):
                        self.agent_positions[j] = old_positions[sorted_idx[j]]

                    # 切り替え直後に位置を再設定して瞬間移動を防ぐ
                    self.sim.setAgentposition(self.agent_positions)
                for j in range(Params["num_agents"]):
                    print(f"Agent[{j}]の位置: {self.agent_positions[j]}")
                    self.sim.setAgentposition(self.agent_positions)
                time.sleep(Params["frame_time"])

                self.sim.step_simulation()
                time.sleep(Params["frame_time"])

        except KeyboardInterrupt:
            print("ctrl+Cが押されました。")
        finally:
            self.sim.stop_simulation()


controller = Main(Params["agent_position"])
controller.animate()
