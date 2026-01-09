import numpy as np
from parameter import Params
from connect_Coppelia import Simulation


class LineFormation:
    def __init__(self):
        self.sim = Simulation()
        self.agent_positions = []
        self.line_speed = 1.5  # 移動速度[m/s]
        self.tolerance = 0.3  # 到達判定の許容誤差[m]
        self.distance_from_target = 2.0  # ターゲットからの距離[m]
        self.agent_spacing = 1.0  # エージェント間の距離[m]
        self.prev_target_position = None  # 前フレームのターゲット位置
        self.target_velocity_angle = 0  # ターゲットの進行方向の角度
        self.formation_complete_count = 0  # フォーメーション完成の連続カウント
        self.formation_stable_threshold = 10  # 完成と判定するための連続フレーム数
        self.num_agents = Params["num_agents"]  # エージェント数

    def animate(self, target_position, agent_positions):
        """ターゲットの進行方向に垂直な直線上にエージェントを配置

        Returns:
            bool: 直線フォーメーションが完成したかどうか
        """
        self.agent_positions = agent_positions

        # ターゲットの進行方向を計算
        if self.prev_target_position is not None:
            # 前回位置から現在位置への方向ベクトル
            target_velocity = np.array(target_position[:2]) - np.array(
                self.prev_target_position[:2]
            )
            velocity_norm = np.linalg.norm(target_velocity)

            if velocity_norm > 0.01:  # 移動している場合
                # 進行方向の角度を計算
                self.target_velocity_angle = np.arctan2(
                    target_velocity[1], target_velocity[0]
                )
            # 静止している場合は前回の角度を維持
        else:
            # 初回はターゲットの現在位置を基準に（デフォルトは上方向）
            self.target_velocity_angle = np.pi / 2

        # 進行方向に垂直な角度（左側に90度回転）
        perpendicular_angle = self.target_velocity_angle + np.pi / 2

        # ラインフォーメーションの目標位置を計算
        target_pos_2d = np.array(target_position[:2])
        num_agents = Params["num_agents"]

        # 各エージェントのx座標を取得してソート
        agent_x_coords = []
        for j in range(num_agents):
            agent_pos = np.array(agent_positions[j])
            x_coord = agent_pos[0]
            agent_x_coords.append((j, x_coord))  # (エージェントインデックス, x座標)

        # x座標でソート（小さい順 = 左から右）
        agent_x_coords.sort(key=lambda x: x[1])

        # デバッグ出力：x座標順の情報を表示
        if self.prev_target_position is None:  # 初回のみ表示
            print("\n--- エージェントのx座標順（左から右） ---")
            for i, (agent_idx, x_coord) in enumerate(agent_x_coords):
                print(f"  {i+1}番目: Agent[{agent_idx}], x座標={x_coord:.3f}m")

        # 配置位置を決定（x座標順に左から右へ配置）
        position_assignment = [
            None
        ] * num_agents  # position_assignment[line_position] = agent_index

        # x座標が小さい順（左から）に、位置0から順番に割り当て
        for i, (agent_idx, x_coord) in enumerate(agent_x_coords):
            position_assignment[i] = agent_idx

        # デバッグ出力：配置結果を表示
        if self.prev_target_position is None:  # 初回のみ表示
            print("\n--- 配置結果（x座標順） ---")
            for line_pos in range(num_agents):
                agent_idx = position_assignment[line_pos]
                if num_agents == 6:
                    pos_name = ["左端", "位置1", "中央左", "中央右", "位置4", "右端"][
                        line_pos
                    ]
                else:
                    pos_name = f"位置{line_pos}"
                print(f"  {pos_name}: Agent[{agent_idx}]")
            print()

        # エージェントをラインの中央を基準に配置
        # ターゲットから進行方向の前方に配置
        line_center = target_pos_2d + np.array(
            [
                np.cos(self.target_velocity_angle) * self.distance_from_target,
                np.sin(self.target_velocity_angle) * self.distance_from_target,
            ]
        )

        new_positions = []
        agents_in_position = 0  # 目標位置に到達したエージェントの数

        # 各エージェントの新しい位置を計算（エージェントのインデックス順）
        agent_target_positions = {}  # agent_index -> target_position_3d

        for line_pos in range(num_agents):
            agent_idx = position_assignment[line_pos]

            # ラインの中心からの相対位置（左右対称に配置）
            offset_from_center = (line_pos - (num_agents - 1) / 2) * self.agent_spacing

            # 垂直方向のオフセットを加算
            target_pos_2d_for_agent = line_center + np.array(
                [
                    np.cos(perpendicular_angle) * offset_from_center,
                    np.sin(perpendicular_angle) * offset_from_center,
                ]
            )

            current_pos = np.array(agent_positions[agent_idx])  # [x, y, z]

            # z座標は現在の値を維持
            target_pos_3d = np.array(
                [target_pos_2d_for_agent[0], target_pos_2d_for_agent[1], current_pos[2]]
            )

            agent_target_positions[agent_idx] = (
                target_pos_3d,
                target_pos_2d_for_agent,
                current_pos,
            )

        # エージェントのインデックス順に新しい位置を作成
        for j in range(num_agents):
            target_pos_3d, target_pos_2d_for_agent, current_pos = (
                agent_target_positions[j]
            )

            # 目標位置までの距離（xy平面のみ）
            distance_2d = np.linalg.norm(current_pos[:2] - target_pos_2d_for_agent)

            if distance_2d < self.tolerance:
                # 到達済み
                new_positions.append(target_pos_3d.tolist())
                agents_in_position += 1
            else:
                # 目標位置に向かって移動
                direction = target_pos_3d - current_pos
                direction_2d_norm = np.linalg.norm(direction[:2])

                if direction_2d_norm > 0:
                    # 正規化した方向ベクトル
                    direction_normalized = direction / direction_2d_norm
                    # 移動量（速度 * 時間）
                    movement = (
                        direction_normalized * self.line_speed * Params["frame_time"]
                    )

                    # 移動量が残り距離より大きい場合は、目標位置に直接移動
                    if np.linalg.norm(movement) > distance_2d:
                        new_positions.append(target_pos_3d.tolist())
                    else:
                        new_positions.append((current_pos + movement).tolist())
                else:
                    new_positions.append(current_pos.tolist())

        # エージェント間の衝突回避（反発力を適用）
        min_distance = Params["LineFormation_collision_distance"]
        final_positions = []
        for agent_idx in range(num_agents):
            repulsion_force = np.zeros(3)
            current_pos = np.array(new_positions[agent_idx])

            for other_idx in range(num_agents):
                if agent_idx != other_idx:
                    other_pos = np.array(new_positions[other_idx])
                    diff = current_pos - other_pos
                    dist = np.linalg.norm(diff)

                    if dist < min_distance and dist > 1e-6:
                        direction = diff / dist
                        force_magnitude = (min_distance - dist) / min_distance
                        repulsion_force += (
                            direction
                            * force_magnitude
                            * Params["LineFormation_repulsion_force"]
                        )

            # 反発力を適用した最終位置
            final_positions.append((current_pos + repulsion_force).tolist())

        # CoppeliaSim に位置を反映
        self.sim.setAgentposition(0, final_positions)

        # 次回のために現在のターゲット位置を保存
        self.prev_target_position = list(target_position)

        # 全エージェントが目標位置に到達しているかチェック
        if agents_in_position == num_agents:
            self.formation_complete_count += 1
            if self.formation_complete_count >= self.formation_stable_threshold:
                print(
                    "直線フォーメーションが完成しました。円形フォーメーションに移行します。"
                )
                return True
        else:
            self.formation_complete_count = 0

        return False
