# targetとAgentが合体

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib
from matplotlib.widgets import Button
from parameter import frame_time, frames
from Handle import sim
from animation import animate, init, fig

matplotlib.rcParams["font.family"] = "MS Gothic"  # Windows標準の日本語フォントを指定

global target_velocity
# シミュレーション開始
if sim.getSimulationState() == sim.simulation_stopped:
    sim.startSimulation()
    print("Simulation started")


ani = FuncAnimation(
    fig, animate, frames=frames, init_func=init, blit=True, interval=frame_time * 1000
)


# --- 再生/停止ボタンのみ ---
class AnimationControl:
    def __init__(self, anim):
        self.anim = anim
        self.running = True

    def toggle(self, event):
        if self.running:
            self.anim.event_source.stop()
        else:
            self.anim.event_source.start()
        self.running = not self.running


button_ax = plt.axes((0.85, 0.05, 0.1, 0.075))
button = Button(button_ax, "再生/停止")
control = AnimationControl(ani)
button.on_clicked(control.toggle)

plt.show()

sim.stopSimulation()
