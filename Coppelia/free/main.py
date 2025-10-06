#これを実行するとシミュレーションスタート

from parameter import frames , frame_time 
from animation import Animation
from connect_Coppelia import Simulation
import time

#import japanize_matplotlib      # type: ignore



class Main:
    def __init__(self):
        self.sim = Simulation()
        # Simulationのハンドルを取得してからAnimationに同じインスタンスを渡す
        from parameter import num_agents
        self.sim.get_handles(num_agents)
        self.ani = Animation()
        self.ani.sim = self.sim

    def run(self):
        try:
            self.sim.connect()
            self.sim.start_simulation()
            for i in range(1000):
                self.ani.animate(i)
                time.sleep(frame_time)
        except KeyboardInterrupt:
            print("ctrl+Cでシミュレーションが終了しました")
        finally:
            self.sim.stop_simulation()

controller = Main()
controller.run()