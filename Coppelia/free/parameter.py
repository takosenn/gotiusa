import numpy as np

Params = {
    # --- システム設定 ---
    "use_mocap": False,  # True: モーションキャプチャ, False: CoppeliaSim
    "save_csv": False,  # True: CSV保存する, False: CSV保存しない
    # --- エージェント設定 ---
    "num_agents": 6,  # Agentの数[台]
    # --- ターゲット設定 ---
    "radius": 5,  # targetの軌道半径[m]
    "radius_limit": 8,  # Agentの配置半径の制限(中心をtargetとして配置する)[m]
    "omega_target": 0.12,  # target円運動の角速度[rad/s]
    # --- シミュレーション設定 ---
    "frames": 10000,  # アニメーションのフレーム数[frame]
    "frame_time": 0.02,  # 1フレームにかかる時間[s]
    # --- 制御パラメータ ---
    "R": 1,  # targetとAgentの理想の距離(フォーメーションの半径)[m]
    "Omega": 2,  # Agentの理想角速度[rad/s]
}

# 計算で求まるパラメータ
Params["d_i"] = (
    2 * np.pi / Params["num_agents"]
)  # Agentiとその隣接Agenti+-の理想角度[rad]
Params["fps"] = 1 / Params["frame_time"]  # 1秒間に更新するフレーム数[frame]

# 初期位置はCoppeliaSimから取得するため、ここでは定義しない
