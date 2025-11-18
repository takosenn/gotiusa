import numpy as np
from parameter import Params


class LineFormation:
    """ターゲットの進行方向に垂直な直線上にエージェントを配置するクラス"""

    def __init__(
        self, num_agents, frame_time, target_position, agent_positions, distance
    ):
        self.num_agents = num_agents
        self.frame_time = frame_time
        self.target_position = np.array(target_position, dtype=float)
        self.prev_target_position = np.copy(self.target_position)
        self.agent_positions = [np.array(pos, dtype=float) for pos in agent_positions]
        self.prev_agent_positions = [np.copy(pos) for pos in self.agent_positions]
        self.distance = distance

    def reorder(self, sorted_idx):
        """sorted_idx の順に内部状態を並び替える"""
        self.agent_positions = [self.agent_positions[i] for i in sorted_idx]
        self.prev_agent_positions = [self.prev_agent_positions[i] for i in sorted_idx]
        self.distance = [self.distance[i] for i in sorted_idx]

    def animate(
        self,
        target_position,
        prev_target_position,
        agent_positions,
        prev_agent_positions,
    ):
        """
        ターゲットの進行方向に垂直な直線上にエージェントを配置し、
        巡回時の移動距離と同じ速度でターゲットに近づく

        Args:
            target_position: 現在のターゲット位置
            prev_target_position: 前回のターゲット位置
            agent_positions: 現在のエージェント位置
            prev_agent_positions: 前回のエージェント位置

        Returns:
            更新後のagent_positions, prev_agent_positions, distance
        """
        self.target_position = np.array(target_position, dtype=float)
        self.prev_target_position = np.array(prev_target_position, dtype=float)
        self.agent_positions = [np.array(pos, dtype=float) for pos in agent_positions]
        self.prev_agent_positions = [
            np.array(pos, dtype=float) for pos in prev_agent_positions
        ]

        # ターゲットの進行方向ベクトルを計算
        target_velocity = self.target_position[:2] - self.prev_target_position[:2]
        target_velocity_norm = np.linalg.norm(target_velocity)

        if target_velocity_norm > 1e-6:
            target_direction = target_velocity / target_velocity_norm
        else:
            # ターゲットが動いていない場合はデフォルト方向
            target_direction = np.array([1, 0])

        # ターゲットの進行方向に垂直なベクトル（2D平面上）
        perpendicular_direction = np.array([-target_direction[1], target_direction[0]])

        # エージェント間の間隔
        spacing = 1.5  # メートル

        # 直線の中心点（ターゲットの現在位置から進行方向前方）
        offset_distance = 3  # ターゲットからの距離
        line_center = self.target_position[:2] + target_direction * offset_distance

        # 各エージェントを直線上に配置し、ターゲットに向かって移動
        for j in range(self.num_agents):
            # 直線上の目標位置を計算
            offset = (j - (self.num_agents - 1) / 2) * spacing
            line_target_pos_2d = line_center + perpendicular_direction * offset
            line_target_pos_3d = np.array(
                [
                    line_target_pos_2d[0],
                    line_target_pos_2d[1],
                    self.agent_positions[j][2],
                ]
            )

            # 現在位置から直線上の位置への方向ベクトル
            to_line = line_target_pos_2d - self.agent_positions[j][:2]
            to_line_norm = np.linalg.norm(to_line)

            # ターゲットへの方向ベクトル
            to_target = self.target_position[:2] - self.agent_positions[j][:2]
            to_target_norm = np.linalg.norm(to_target)

            # 移動ベクトルを計算
            move_direction = np.zeros(2)

            # 直線位置への移動成分
            if to_line_norm > 0.1:  # まだ直線上にない場合
                move_direction += (to_line / to_line_norm) * 0.5

            # ターゲットへの接近成分（巡回時と同じ移動距離）
            if to_target_norm > 1e-6:
                move_direction += (to_target / to_target_norm) * Params["LineFormation_direction"]

            # 移動方向を正規化して、巡回時と同じ移動距離にする
            move_norm = np.linalg.norm(move_direction)
            if move_norm > Params["LineFormation_direction"]:
                move_direction = (move_direction / move_norm) * Params["LineFormation_direction"]

            # 位置を更新（3D座標として）
            self.prev_agent_positions[j] = np.copy(self.agent_positions[j])
            self.agent_positions[j][:2] += move_direction

        # エージェント間の衝突回避
        min_distance = 0.5
        for j in range(self.num_agents):
            repulsion_force = np.zeros(3)
            for k in range(self.num_agents):
                if j != k:
                    diff = self.agent_positions[j] - self.agent_positions[k]
                    dist = np.linalg.norm(diff)
                    if dist < min_distance and dist > 1e-6:
                        direction = diff / dist
                        force_magnitude = (min_distance - dist) / min_distance
                        repulsion_force += direction * force_magnitude * 0.5

            if np.linalg.norm(repulsion_force) > 1e-6:
                self.agent_positions[j] = self.agent_positions[j] + repulsion_force

        # 距離を更新
        self.distance = []
        for j in range(self.num_agents):
            dist = np.linalg.norm(self.agent_positions[j] - self.target_position)
            self.distance.append(dist)

        # リストに変換して返す
        agent_positions_list = [pos.tolist() for pos in self.agent_positions]
        prev_agent_positions_list = [pos.tolist() for pos in self.prev_agent_positions]

        return agent_positions_list, prev_agent_positions_list, self.distance
