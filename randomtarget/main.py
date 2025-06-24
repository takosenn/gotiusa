"""
main_animation.py
分割した各モジュールを統合し、アニメーションを実行するエントリーポイント。
全体の制御・アニメーションループ・UIボタンを担当。
"""

# 分割した各モジュールを統合してアニメーションを実行するmainスクリプト
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
from config import *
from init_plot import fig, ax, point, agent_colors
from agent_core import angles, agent_radii, agent_positions, agent_ids, agent_neighbors
from target_core import target_pos, target_velocity, update_target
from animation_core import (
    ro_i_history,
    eta_i_history,
    omega_i_history,
    alpha_i_history,
    u_vec_history,
    a_vec_history,
    relative_velocity_history,
    e_i_1_integral,
    e_i_2_integral,
)
from agent_animation import agent_animate_update

# --- 描画用エージェント点 ---
agent_dots = ax.scatter(
    agent_positions[:, 0], agent_positions[:, 1], c=agent_colors, label="Agents"
)
roi_text = ax.text(
    0.05,
    0.10,
    "",
    transform=ax.transAxes,
    ha="left",
    va="center",
    fontsize=8,
    color="black",
)


def init():
    point.set_data([0], [radius])
    agent_dots.set_offsets(agent_positions)
    roi_text.set_text("")
    return point, agent_dots, roi_text


# --- animate関数（元のrandomtarget.pyからほぼそのまま移植） ---
def animate(i):
    global target_pos, target_velocity, agent_positions
    target_pos[:], target_velocity[:], appeared = update_target(
        target_pos, target_velocity, random_walk_sigma, max_speed, frame_time, i
    )
    x, y = target_pos
    if not appeared:
        # ターゲット未出現時は点を非表示
        point.set_data([], [])
        agent_dots.set_offsets(agent_positions)
        agent_dots.set_color(agent_colors)
        roi_text.set_text("")
        return point, agent_dots, roi_text
    point.set_data([x], [y])
    agent_dots.set_offsets(agent_positions)
    agent_dots.set_color(agent_colors)
    # agent_animate_updateで返された最新のagent_positionsを必ず反映
    agent_animate_update(
        i, agent_positions, target_pos, target_velocity, agent_colors, roi_text
    )
    agent_dots.set_offsets(agent_positions)  # ここで再度反映
    return point, agent_dots, roi_text


ani = FuncAnimation(
    fig, animate, frames=frames, init_func=init, blit=True, interval=frame_time * 1000
)


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
