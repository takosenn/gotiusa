import numpy as np

rotation_direction = 1  # 正: 反時計回り, 負: 時計回り
num_agents = 6

Params = {
    "num_agents": 6,
    "frames": 10000,
    "frame_time": 0.05,
    "R": [1, 1, 1, 1, 1, 1],  # 理想相対距離（Agent1~6の各値）
    "d_i": [
        2 * np.pi / num_agents,
        2 * np.pi / num_agents,
        2 * np.pi / num_agents,
        2 * np.pi / num_agents,
        2 * np.pi / num_agents,
        2 * np.pi / num_agents,
    ],  # 理想角距離（Agent1~6の各値）
    "Omega": rotation_direction * 3,  # 理想角速度
    "distance_threshold": 10,  # Agent-target間の距離の閾値（この値を下回ると巡回から円形フォーメーションへ移行）
    "patroll_direction": 0.1,  # Agentの巡回時移動距離
    "LineFormation_direction": 0.2,  # エージェントの直線フォーメーション時の移動距離
    "LineFormation_spacing": 1.5,  # 直線フォーメーション時のエージェント間の間隔（メートル）
    "LineFormation_offset_distance": 3,  # 直線フォーメーションの中心点からターゲットまでの距離（メートル）
    "LineFormation_line_threshold": 0.1,  # 直線位置への移動を開始する距離閾値（メートル）
    "LineFormation_line_weight": 0.5,  # 直線位置への移動成分の重み
    "LineFormation_collision_distance": 0.5,  # エージェント間の衝突回避の最小距離（メートル）
    "LineFormation_repulsion_force": 0.5,  # 衝突回避の反発力の強さ
    "R_reset": [1, 1, 1, 1, 1, 1],  # k>100時の理想相対距離（リセット値）
    "omega_seq": [
        rotation_direction * 3,
        rotation_direction * 3.5,
        rotation_direction * 4,
        rotation_direction * 3.5,
    ],  # Omega切り替えシーケンス（三角波）角速度
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
