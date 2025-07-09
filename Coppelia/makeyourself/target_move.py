# move
# Agentとtargetの動き方

import numpy as np
from init_parameter import frame_time, radius, random_walk_sigma, max_speed
from SecondD_ani_init import point, agent_positions, agent_dots

# --- targetのランダムウォーク用初期化 ---
target_pos = np.array([0.0, 0.0])  # 初期位置（円運動の初期値と同じ）
target_velocity = np.zeros(2)  # 初期速度


def init():
    point.set_data([0], [radius])
    agent_dots.set_offsets(agent_positions)
    # roi_text.set_text("")
    return point, agent_dots  # , roi_text


def target_move():
    global target_velocity, target_pos
    # targetのランダムウォーク
    target_velocity += np.random.normal(0, random_walk_sigma, size=2)
    speed = np.linalg.norm(target_velocity)
    # 最大速度制限
    if speed > max_speed:
        target_velocity = target_velocity / speed * max_speed
    # 位置を更新
    target_pos += target_velocity * frame_time
    x, y = target_pos
    point.set_data([x], [y])
