import numpy as np

Params = {
    "num_agents": 6,
    "frames": 10000,
    "frame_time": 0.05,
    "R": 2,
    "d_i": np.pi / 3,
    "Omega": 2,
    "distance_threshold": 10,
    "direction": 0.1,
    "per_agent_R": [2, 2.2, 2.4, 2.6, 2.8, 3.0],  # 各Quadcopterの個別R値
    "omega_seq": [2, 3, 4, 3],  # Omega切り替えシーケンス（三角波）
    "target_position": [20, 20, 2],
    "agent_position": [
        [5, 0, 2],
        [10, 5, 2],
        [5, 10, 2],
        [0, 5, 2],
        [3.3, 6.6, 2],
        [6.6, 3.3, 2],
    ],
}
