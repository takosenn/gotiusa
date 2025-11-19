# ローカル座標系の値をグローバル座標系に変換する関数

import numpy as np
from parameter import Params


class Various:
    def __init__(self):
        self.theta = []
        for i in range(Params["num_agents"]):
            theta = i * np.pi / 3
            self.theta.append(theta)
        self.alpha = []
        for i in range(Params["num_agents"]):
            alpha = i * np.pi / 3
            self.alpha.append(alpha)
        self.alpha_minus = np.copy(self.alpha)

    def Theta(self, pos):
        self.theta = np.arctan2(pos[1], pos[0])
        if self.theta >= 0:
            self.theta = self.theta
        else:
            self.theta = self.theta + 2 * np.pi
        return self.theta

    def Angular_distance(
        self, theta, theta_plus, theta_minus
    ):  # theta_minusは(i-1)番目、theta_plusは(i+1)番目の角度(World座標系)
        diff_plus = theta_plus - theta
        if diff_plus >= 0:
            alpha = diff_plus
        else:
            alpha = diff_plus + (2 * np.pi)
        diff_minus = theta - theta_minus
        if diff_minus >= 0:
            alpha_minus = diff_minus
        else:
            alpha_minus = diff_minus + (2 * np.pi)
        return alpha, alpha_minus

    def Angular_velocity(
        self, theta, prev_theta
    ):  # prev_thetaはi番目の角度 theta = 2πの際に問題あり
        delta = theta - prev_theta
        if delta > np.pi:
            delta -= 2 * np.pi
        elif delta < -np.pi:
            delta += 2 * np.pi
        omega = delta / Params["frame_time"]
        return omega

    def Velocity(self, current_pos, prev_pos):
        velocity = (np.array(current_pos) - np.array(prev_pos)) / Params["frame_time"]
        return velocity

    def coordinate_trans(self, theta_global, u):
        A = np.array(
            [
                [np.cos(theta_global), -np.sin(theta_global)],
                [np.sin(theta_global), np.cos(theta_global)],
            ]
        )
        u_vec_local = np.array([u[0], u[1]])
        u_vec = A @ u_vec_local
        return u_vec

    def reorder_agents(
        self, agent_position, prev_agent_positions, distance, theta, sorted_idx
    ):
        """
        ハンドル切り替え時にエージェントの内部状態を並び替える

        Args:
            agent_position: エージェント位置（リストまたはnumpy配列）
            prev_agent_positions: 前回のエージェント位置（numpy配列）
            distance: ターゲットまでの距離（リスト）
            theta: 各エージェントの角度（リストまたはnumpy配列）
            sorted_idx: 並び替えインデックス（リスト）

        Returns:
            並び替え後の (agent_position, prev_agent_positions, distance, theta)
        """
        # agent_position の並び替え
        if isinstance(agent_position, np.ndarray):
            agent_position = agent_position.tolist()
        agent_position = [agent_position[idx] for idx in sorted_idx]

        # prev_agent_positions の並び替え
        try:
            prev_agent_positions = np.array(
                [prev_agent_positions[idx] for idx in sorted_idx]
            )
        except Exception:
            prev_agent_positions = np.array(
                [prev_agent_positions[idx].tolist() for idx in sorted_idx]
            )

        # distance の並び替え
        distance = [distance[idx] for idx in sorted_idx]

        # theta の並び替え
        try:
            theta = [theta[idx] for idx in sorted_idx]
        except Exception:
            theta = list(theta)
            theta = [theta[idx] for idx in sorted_idx]

        return agent_position, prev_agent_positions, distance, theta
