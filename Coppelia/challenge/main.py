# targetとAgentが合体

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
from parameter import frame_time, frames
from Handle import sim , client , RemoteAPIClient
from animation import animate, init, fig
import japanize_matplotlib      # type: ignore
import time

def __init__(self, host='127.0.0.1', port=23000):
        self.client = RemoteAPIClient(host, port)
        self.sim = self.client.getObject('sim')
        self.quad_handles = []
        self.target_handles = []
        self.goal_cylinder_handle = -1
        
client.setStepping(True) # 必要に応じて同期モードを有効にする

# シミュレーション開始
if sim.getSimulationState() == sim.simulation_stopped:
    sim.startSimulation()
    print("Simulation started")

client.step()
ani = FuncAnimation(
    fig, animate, frames=frames, init_func=init, blit=True, interval=frame_time * 1000
)

time.sleep(0.05)
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

# シミュレーション停止
print("Stopping simulation")
sim.stopSimulation()
init()