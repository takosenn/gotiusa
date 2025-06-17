# animation_ui.py
from matplotlib.widgets import Button
from init_plot import ax

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

def add_control_button(anim):
    button_ax = ax.figure.add_axes((0.85, 0.05, 0.1, 0.075))
    button = Button(button_ax, '再生/停止')
    control = AnimationControl(anim)
    button.on_clicked(control.toggle)
    return button, control
