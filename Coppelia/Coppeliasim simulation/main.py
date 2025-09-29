
#これを実行するとシミュレーションスタート

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
from parameter import frames , frame_time 
from animation import animate,init,fig
from connect_Coppelia import sim
import japanize_matplotlib      # type: ignore

# シミュレーション開始
if sim.getSimulationState() == sim.simulation_stopped:
    sim.startSimulation()
    print("Simulation started")

ani = FuncAnimation(
    fig, animate, frames=frames, init_func=init, blit=True, interval=frame_time * 1000
)

#再生/停止ボタン
class AnimationControl:
    def __init__(self, anim):
        self.anim = anim
        self.running = True

    def toggle(self,event):
        if self.running:
            self.anim.event_source.stop()
        else:
            self.anim.event_source.start()
        self.running = not self.running

#ボタンの配置と設定
button_ax = plt.axes((0.85, 0.05, 0.1, 0.075))
button = Button(button_ax, "再生/停止")
#ボタンが反応するようにする
control = AnimationControl(ani)
button.on_clicked(control.toggle)

plt.show()

# シミュレーション停止
print("Stopping simulation")
sim.stopSimulation()
init()