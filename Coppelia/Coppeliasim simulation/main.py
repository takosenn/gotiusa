
#これを実行するとシミュレーションスタート

from parameter import frames , frame_time 
from animation import Animation
from connect_Coppelia import Simulation
import time

import japanize_matplotlib      # type: ignore



class Main:
    def __init__(self):
        self.sim = Simulation()
        self.ani = Animation()

    def run(self):
        try:
            self.sim.connect()
            self.sim.start_simulation()
            start_time = time.time()
            for i in range(1000):
                self.ani.animate(i)
                next_time = start_time + (i + 1) * frame_time
                sleep_time = max(0, next_time - time.time())
                time.sleep(sleep_time)
        except KeyboardInterrupt:
            print("ctrl+Cでシミュレーションが終了しました")
        finally:
            self.sim.stop_simulation()

controller = Main()
controller.run()
