import numpy as np
from parameter import Params
from connect_Coppelia import Simulation


class LineFormation:
    def __init__(self):
        self.sim = Simulation()
        self.agent_positions = []
        self.line_speed = 3  # 移動速度[m/s]
        self.tolerance = 0.1  # 到達判定の許容誤差[m]
        self.distance_from_target = 2.0  # ターゲットからの距離[m]
        self.agent_spacing = 1.0  # エージェント間の距離[m]
        self.prev_target_position = None  # 前フレームのターゲット位置
        self.target_velocity_angle = 0  # ターゲットの進行方向の角度
        self.formation_complete_count = 0  # フォーメーション完成の連続カウント
        self.formation_stable_threshold = 10  # 完成と判定するための連続フレーム数
        self.num_agents = Params["num_agents"]  # エージェント数

        # 円形フォーメーションへの段階的移行用パラメータ
        self.transition_started = False  # 移行が開始されたか
        self.transition_step_count = 0  # 移行開始からのステップ数
        self.transition_interval = 6  # 次のエージェントを移行させる間隔（ステップ）
        self.num_transitioned_agents = (
            0  # 円形フォーメーションに移行済みのエージェント数
        )
        self.transition_order = []  # 移行順序（エージェントインデックスのリスト）
        self.circle_radius = 3.0  # 円形フォーメーションの半径[m]

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

        # 垂直方向の単位ベクトル（ラインに沿った方向）
        perpendicular_vector = np.array(
            [np.cos(perpendicular_angle), np.sin(perpendicular_angle)]
        )

        # 各エージェントを垂直方向に投影した座標を取得してソート
        agent_projections = []
        for j in range(num_agents):
            agent_pos = np.array(agent_positions[j])
            # エージェント位置を垂直方向のベクトルに投影（内積）
            projection = np.dot(agent_pos[:2], perpendicular_vector)
            agent_projections.append(
                (j, projection)
            )  # (エージェントインデックス, 投影座標)

        # 投影座標でソート（小さい順 = ラインの一方の端からもう一方へ）
        agent_projections.sort(key=lambda x: x[1])

        # デバッグ出力：投影座標順の情報を表示
        if self.prev_target_position is None:  # 初回のみ表示
            print("\n--- エージェントのライン方向投影座標順 ---")
            print(f"進行方向角度: {np.degrees(self.target_velocity_angle):.1f}°")
            print(f"垂直方向角度: {np.degrees(perpendicular_angle):.1f}°")
            for i, (agent_idx, projection) in enumerate(agent_projections):
                print(f"  {i+1}番目: Agent[{agent_idx}], 投影座標={projection:.3f}m")

        # 配置位置を決定（投影座標順にラインの端から端へ配置）
        position_assignment = [
            None
        ] * num_agents  # position_assignment[line_position] = agent_index

        # 投影座標が小さい順に、位置0から順番に割り当て
        for i, (agent_idx, projection) in enumerate(agent_projections):
            position_assignment[i] = agent_idx

        # デバッグ出力：配置結果を表示
        if self.prev_target_position is None:  # 初回のみ表示
            print("\n--- 配置結果（ライン方向順） ---")
            for line_pos in range(num_agents):
                agent_idx = position_assignment[line_pos]
                if num_agents == 6:
                    pos_name = ["端1", "位置1", "中央左", "中央右", "位置4", "端2"][
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

        # 移行中のエージェントに円形フォーメーションの目標位置を適用
        new_positions = self._update_positions_with_transition(
            target_position, agent_positions, new_positions
        )

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
                if not self.transition_started:
                    # 移行開始
                    print(
                        "\n直線フォーメーションが完成しました。段階的に円形フォーメーションに移行します。"
                    )
                    self._initialize_transition(target_position, agent_positions)
                    self.transition_started = True
        else:
            self.formation_complete_count = 0

        # 段階的移行の処理
        if self.transition_started:
            self.transition_step_count += 1

            # 15ステップごとに新しいエージェントを移行
            if self.transition_step_count % self.transition_interval == 0:
                if self.num_transitioned_agents < self.num_agents:
                    self.num_transitioned_agents += 1
                    transitioned_agent_idx = self.transition_order[
                        self.num_transitioned_agents - 1
                    ]
                    print(
                        f"Agent[{transitioned_agent_idx}] が円形フォーメーションに移行しました。({self.num_transitioned_agents}/{self.num_agents})"
                    )

            # 全エージェントが移行完了したかチェック
            if self.num_transitioned_agents >= self.num_agents:
                print("すべてのエージェントが円形フォーメーションに移行しました。")
                return True

        return False

    def _initialize_transition(self, target_position, agent_positions):
        """移行の初期化：ターゲットのy座標に基づいて移行順序を決定"""
        # 垂直方向の単位ベクトル（ラインに沿った方向）
        perpendicular_angle = self.target_velocity_angle + np.pi / 2
        perpendicular_vector = np.array(
            [np.cos(perpendicular_angle), np.sin(perpendicular_angle)]
        )

        # 各エージェントを垂直方向に投影
        agent_projections = []
        for j in range(self.num_agents):
            agent_pos = np.array(agent_positions[j])
            projection = np.dot(agent_pos[:2], perpendicular_vector)
            agent_projections.append((j, projection))

        # 投影座標でソート
        agent_projections.sort(key=lambda x: x[1])

        # ターゲットのy座標に基づいて移行順序を決定
        target_y = target_position[1]
        if target_y >= 0:
            # y座標が0以上：右端から移行（投影座標が大きい方から）
            self.transition_order = [
                agent_idx for agent_idx, _ in reversed(agent_projections)
            ]
            print(f"ターゲットy座標 = {target_y:.3f} >= 0 → 右端から移行")
        else:
            # y座標が0未満：左端から移行（投影座標が小さい方から）
            self.transition_order = [agent_idx for agent_idx, _ in agent_projections]
            print(f"ターゲットy座標 = {target_y:.3f} < 0 → 左端から移行")

        print(f"移行順序: {self.transition_order}")

    def _update_positions_with_transition(
        self, target_position, agent_positions, new_positions
    ):
        """移行中のエージェントに円形フォーメーションの目標位置を設定"""
        if not self.transition_started or self.num_transitioned_agents == 0:
            return new_positions

        target_pos_2d = np.array(target_position[:2])

        # 円形フォーメーションに移行済みのエージェントの位置を計算
        for i in range(self.num_transitioned_agents):
            agent_idx = self.transition_order[i]

            # 円周上の目標角度（均等配置）
            angle = 2 * np.pi * i / self.num_agents

            # 円形フォーメーションの目標位置
            circle_target_2d = target_pos_2d + self.circle_radius * np.array(
                [np.cos(angle), np.sin(angle)]
            )

            current_pos = np.array(agent_positions[agent_idx])
            target_pos_3d = np.array(
                [circle_target_2d[0], circle_target_2d[1], current_pos[2]]
            )

            # 目標位置に向かって移動
            direction = target_pos_3d - current_pos
            direction_2d_norm = np.linalg.norm(direction[:2])

            if direction_2d_norm > self.tolerance:
                direction_normalized = direction / direction_2d_norm
                movement = direction_normalized * self.line_speed * Params["frame_time"]

                if np.linalg.norm(movement) > direction_2d_norm:
                    new_positions[agent_idx] = target_pos_3d.tolist()
                else:
                    new_positions[agent_idx] = (current_pos + movement).tolist()
            else:
                new_positions[agent_idx] = target_pos_3d.tolist()

        return new_positions
