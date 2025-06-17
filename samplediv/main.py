import matplotlib
matplotlib.rcParams['font.family'] = 'MS Gothic'

from config import *
from init_plot import fig, ax, point, circle, agent_positions, agent_dots, agent_colors
from controls import angular_distance_rad
from animate import show

# ここでアニメーションを開始する
# animate.py 側でアニメーションやUI制御を実装

if __name__ == "__main__":
    show()