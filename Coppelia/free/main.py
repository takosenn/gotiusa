# これを実行するとシミュレーションスタート

from parameter import Params
from animation import Animation
from connect_Coppelia import Simulation
import time
import numpy as np


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

                # 全エージェントの相対距離の最小値を計算
                min_ro_i = min(
                    self.ani.various.Distance(
                        np.array(agent_positions[j]) - np.array(target_position)
                    )
                    for j in range(Params["num_agents"])
                )

                # 取得した座標を使って計算
                if min_ro_i < 4:
                    self.ani.animate(i, target_position, agent_positions)
                time.sleep(Params["frame_time"])
                self.sim.step_simulation()
        except KeyboardInterrupt:
            print("\nctrl+Cでシミュレーションが終了しました")
        except Exception as e:
            print(f"\nエラーが発生しました: {type(e).__name__}: {e}")
            print("シミュレーションを停止します...")
        finally:
            print("CoppeliaSim を停止中...")
            self.sim.stop_simulation()
            print("シミュレーション終了")


controller = Main()
controller.run()
