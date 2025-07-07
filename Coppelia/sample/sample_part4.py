# sample_part4.py
from sample.sample_part3 import *

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
