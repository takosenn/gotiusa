# これを実行するとシミュレーションスタート

from parameter import Params
from animation import Animation
from connect_Coppelia import Simulation
import time


# import japanize_matplotlib      # type: ignore


class Main:
    def __init__(self):
        self.sim = Simulation()
        # Simulationのハンドルを取得してからAnimationに同じインスタンスを渡す
        self.sim.get_handles(Params["num_agents"])
        self.ani = Animation()
        self.ani.sim = self.sim

    def run(self):
        try:
            self.sim.connect()
            self.sim.start_simulation()

            # CoppeliaSim から初期位置を取得
            print("CoppeliaSim から初期位置を取得中...")
            initial_target_pos, initial_agent_pos = self.sim.get_Drone_position()
            print(f"Target初期位置: {initial_target_pos}")
            print(f"Agent初期位置: {initial_agent_pos}")

            for i in range(Params["frames"]):
                print(f"現在のfor文を読んだ回数: {i}回目")
                # CoppeliaSim から現在の座標を取得
                target_position, agent_positions = self.sim.get_Drone_position()
                # 取得した座標を使って計算
                self.ani.animate(i, target_position, agent_positions)
                time.sleep(Params["frame_time"])
                self.sim.step_simulation()
        except KeyboardInterrupt:
            print("ctrl+Cでシミュレーションが終了しました")
        finally:
            self.sim.stop_simulation()


controller = Main()
controller.run()
