# animate.py

import functools
import numpy as np
from matplotlib.animation import FuncAnimation
from config import frames
from animation_data import init
from animation_core import animate
from animation_ui import add_control_button
from init_plot import fig, point, agent_dots, agent_positions, radius, ax

# init関数も引数で渡す形に合わせる
init_func = lambda: init(point, agent_dots, agent_positions, radius)
ani = FuncAnimation(
    fig,
    functools.partial(animate),
    frames=frames,
    init_func=init_func,
    blit=True,
    interval=50,
)
add_control_button(ani)


def show():
    import matplotlib.pyplot as plt

    plt.show()
