import numpy as np

Params = {
    # --- システム設定 ---
    "use_mocap": False,  # True: モーションキャプチャ, False: CoppeliaSim
    "save_csv": False,  # True: CSV保存する, False: CSV保存しない
    # --- エージェント設定 ---
    "num_agents": 6,  # Agentの数[台]
    # --- ターゲット設定 ---
    "target_move": True,  # True: targetを移動させる, False: targetを静止させる
    "target_move_speed": 0.05,  # targetの目標位置への移動速度[m/s]
    "target_goal_x": 0.0,  # targetの目標位置x座標[m]
    "target_goal_y": 0.0,  # targetの目標位置y座標[m]
    "target_tolerance": 0.1,  # target到達判定の許容誤差[m]
    # --- シミュレーション設定 ---
    "frames": 10000,  # アニメーションのフレーム数[frame]
    "frame_time": 0.05,  # 1フレームにかかる時間[s]
    # --- 制御パラメータ ---
    "R": 4,  # targetとAgentの理想の距離(フォーメーションの半径)[m]
    "Omega": 0.5,  # Agentの理想角速度[rad/s]
    # --- LineFormation設定 ---
    "LineFormation_collision_distance": 0.6,  # 衝突回避を開始する距離[m]
    "LineFormation_repulsion_force": 0.8,  # 反発力の強さ
}

# 計算で求まるパラメータ
# 各エージェントの理想相対角距離[rad]（デフォルトは均等分配）
Params["d_i"] = [np.pi/3 , np.pi/3 , np.pi/3 , np.pi/3 , np.pi/3 , np.pi/3 ]  # 6台の場合
Params["fps"] = 1 / Params["frame_time"]  # 1秒間に更新するフレーム数[frame]