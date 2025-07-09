
#これを実行するとアニメーションが始まる

import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from Button import ani,AnimationControl

import matplotlib
matplotlib.rcParams["font.family"] = "MS Gothic"  # Windows標準の日本語フォントを指定

# aniとAnimationControlがsample_part4で定義されていることを仮定
button_ax = plt.axes((0.85, 0.05, 0.1, 0.075))
button = Button(button_ax, "再生/停止")
control = AnimationControl(ani)
button.on_clicked(control.toggle)

plt.show()