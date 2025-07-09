# 再生/停止ボタン生成

from init_parameter import frames, frame_time
from SecondD_ani_init import fig
from target_move import init
from animation import animate
from matplotlib.animation import FuncAnimation

ani = FuncAnimation(
    fig,
    animate,
    frames=frames,
    init_func=init,
    blit=True,
    interval=frame_time * 1000,
    repeat=True,
)


# --- 再生/停止ボタンのクラス定義 ---
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
