import numpy as np

rotation_direction = 1  # 正: 反時計回り, 負: 時計回り  

Params = {
    "num_agents": 6,
    "frames": 10000,
    "frame_time": 0.05,
    "R": [1, 1, 1, 1, 1, 1],  # 理想相対距離（Agent1~6の各値）
    "d_i": [
        np.pi / 3,
        np.pi / 3,
        np.pi / 3,
        np.pi / 3,
        np.pi / 3,
        np.pi / 3,
    ],  # 理想角距離（Agent1~6の各値）
    "Omega": rotation_direction * 2,  # 理想角速度
    "distance_threshold": 10,  # Agent-target間の距離の閾値（この値を下回ると巡回から円形フォーメーションへ移行）
    "patroll_direction": 0.1,  # Agentの巡回時移動距離
    "LineFormation_direction": 0.1,  # エージェントの直線フォーメーション時の移動距離
    "per_agent_R": [1, 1.2, 1.4, 1.6, 1.8, 2.0],  # 各Quadcopterの個別R値（k<=100時）
    "R_reset": [1, 1, 1, 1, 1, 1],  # k>100時の理想相対距離（リセット値）
    "omega_seq": [rotation_direction * 2, rotation_direction * 2.5, rotation_direction * 3, rotation_direction * 2.5],  # Omega切り替えシーケンス（三角波）角速度
    "target_position": [20, 20, 2],  # targetの初期位置
    "agent_position": [
        [5, 0, 2],
        [10, 5, 2],
        [5, 10, 2],
        [0, 5, 2],
        [3.3, 6.6, 2],
        [6.6, 3.3, 2],
    ],  # 各Quadcopterの初期位置
    "target_distance_traveled": [-0.05, -0.05, 0],
}
