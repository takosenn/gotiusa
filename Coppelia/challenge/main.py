# targetとAgentが合体

import time
from parameter import frames
from animation import Animation
from simulation import Simulation

class Main:
    def __init__(self):
        self.sim = Simulation()
        self.ani = Animation()

    def run(self):
        self.sim.connect()
        self.sim.start_simulation()
        time.sleep(1)  # シミュレーションが安定するまで待つ

        try:
            for i in range(frames):
                self.ani.animate(i)

        except KeyboardInterrupt:
            print("Ctrl+Cが押されました。終了します。")
        finally:
            self.sim.stop_simulation()
            print("シミュレーションが終了しました。")

if __name__ == "__main__":
    main = Main()
    main.run()