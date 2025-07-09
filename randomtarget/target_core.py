"""
target_motion.py
ターゲット（目標点）のランダムウォーク運動・初期化を担当。
ターゲットの動く範囲を[-30, 30]に制限。
また、target_appear_timeで指定した時間（秒）以降に出現する。
"""

import numpy as np
from config import num_agents, xlim, ylim, frame_time

# --- targetの出現時間（0～5秒のランダム値） ---
target_appear_time = 0  # 最初から出現
target_appeared = False

# --- targetのランダムウォーク用初期化 ---
target_pos = np.array([0.0, 0.0])  # 初期位置を中心(0,0)に
target_velocity = np.zeros(2)  # 初期速度


# --- targetのランダムウォーク関数 ---
def update_target(
    target_pos, target_velocity, random_walk_sigma, max_speed, frame_time, i=None
):
    global target_appeared
    target_appeared = True  # 常に出現済み
    target_velocity += np.random.normal(0, random_walk_sigma, size=2)
    speed = np.linalg.norm(target_velocity)
    if speed > max_speed:
        target_velocity = target_velocity / speed * max_speed
    target_pos += target_velocity * frame_time
    # 範囲制限 [-30, 30]
    target_pos[0] = np.clip(target_pos[0], xlim[0], xlim[1])
    target_pos[1] = np.clip(target_pos[1], ylim[0], ylim[1])
    return target_pos, target_velocity, True
