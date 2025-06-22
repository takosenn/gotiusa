import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.widgets import Button

# グラフ・UI部品の初期化

def setup_figure(xlim, ylim):
    fig, ax = plt.subplots()
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    return fig, ax

def add_agent_legend(ax, num_agents, agent_colors):
    legend_elements = [
        Line2D([0], [0], marker="o", color="w", label=f"Agent {i+1}",
               markerfacecolor=agent_colors[i], markersize=10)
        for i in range(num_agents)
    ]
    ax.legend(handles=legend_elements, loc="center left", bbox_to_anchor=(1, 0.5))

def add_play_button(fig, anim, callback):
    button_ax = plt.axes((0.85, 0.05, 0.1, 0.075))
    button = Button(button_ax, "再生/停止")
    button.on_clicked(callback)
    return button
