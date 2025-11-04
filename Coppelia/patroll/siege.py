
import numpy as np
from various_calculation import Various
from caluculation import caluculate

class Siege:
    def __init__(self, num_agents , frame_time , target_position , agent_positions, distance):
        self.various = Various()

        self.num_agents = num_agents
        self.frame_time = frame_time

        self.target_position = target_position
        self.prev_target_position = np.copy(self.target_position)

        self.agent_positions = list(agent_positions)
        self.prev_agent_positions = np.copy(self.agent_positions)

        self.current_world_agent_positions = [0 for _ in range(self.num_agents)]

        self.relative_coordinates = list(np.array(self.target_position) - np.array(self.agent_positions))
        self.prev_relative_coordinates = np.copy(self.relative_coordinates)

        self.agent_velocity = (np.array(self.agent_positions) - np.array(self.prev_agent_positions)) / self.frame_time

        self.theta = [self.various.Theta(coord) for coord in self.relative_coordinates]
        self.prev_theta = np.copy(self.theta)

        self.omega_i = [0 for _ in range(self.num_agents)]
        self.omega_i_plus = [0 for _ in range(self.num_agents)]
        self.omega_i_minus = [0 for _ in range(self.num_agents)]

        self.ro_i = list(distance)
        self.prev_ro_i = np.copy(self.ro_i)
        self.eta = [0 for _ in range(self.num_agents)]

        self.alpha_i = [0 for _ in range(self.num_agents)]
        self.alpha_i_minus = [0 for _ in range(self.num_agents)]

        self.e_i_1 = [0 for _ in range(self.num_agents)]
        self.e_i_2 = [0 for _ in range(self.num_agents)]
        self.fi = [0 for _ in range(self.num_agents)]

    def animate(self , agent_position ,  prev_agent_positions , prev_target_position , target_position):
        self.target_position = target_position
        self.prev_target_position = prev_target_position
        #self.agent_positions = agent_position
        self.prev_agent_positions = prev_agent_positions

        for i in range(self.num_agents):
            i_plus = (i+1)%self.num_agents
            i_minus = (i-1)%self.num_agents
            self.relative_coordinates[i] = np.array(self.target_position) - np.array(self.agent_positions[i])
            self.prev_relative_coordinates[i] = (np.array(self.target_position) + [0.1,0.1,0]) - np.array(self.agent_positions[i])
            self.ro_i[i] = np.linalg.norm(self.relative_coordinates[i])
            self.prev_ro_i[i] = np.linalg.norm(self.prev_relative_coordinates[i])
            self.eta[i] = (self.ro_i[i] - self.prev_ro_i[i]) / self.frame_time
            self.theta[i] = self.various.Theta(self.relative_coordinates[i])
            self.prev_theta[i]  = self.various.Theta(self.prev_relative_coordinates[i])
            # 角速度 omega_i
            delta_theta = np.arctan2(
                np.sin(self.theta[i] - self.prev_theta[i]),
                np.cos(self.theta[i] - self.prev_theta[i]),
            )
            self.omega_i[i] = delta_theta / self.frame_time
            # 隣接の角速度
            self.omega_i_plus[i] = np.copy(self.omega_i[i_plus])
            self.omega_i_minus[i] = np.copy(self.omega_i[i_minus])

                # raw alpha を全エージェント分計算（まだスケーリングはしない）
            for j in range(self.num_agents):
                j_plus = (j + 1) % self.num_agents
                j_minus = (j - 1) % self.num_agents
                alpha_raw, alpha_minus_raw = self.various.Angular_distance(
                    self.theta[j], self.theta[j_plus], self.theta[j_minus]
                )
                self.alpha_i[j] = alpha_raw
                self.alpha_i_minus[j] = alpha_minus_raw

            # --- 正規化: 全体合計が 2π になるよう一度だけスケール ---
            total = sum(self.alpha_i)
            if total == 0:
                # 万が一全てゼロなら均等分配（安全策）
                uniform = 2 * np.pi / self.num_agents
                for j in range(self.num_agents):
                    self.alpha_i[j] = uniform
                    self.alpha_i_minus[j] = uniform
            else:
                scale = 2 * np.pi / total
                for j in range(self.num_agents):
                    self.alpha_i[j] = self.alpha_i[j] * scale
                    self.alpha_i_minus[j] = self.alpha_i_minus[j] * scale

            u_r, u_theta, self.e_i_1[j], self.e_i_2[j], self.fi[j] = caluculate(
                i,
                j,
                self.alpha_i[j],
                self.alpha_i_minus[j],
                self.omega_i_plus[j],
                self.omega_i[j],
                self.omega_i_minus[j],
                self.ro_i[j],
                self.eta[j],
            )

            cos_alpha = np.cos(self.theta[j])
            sin_alpha = np.sin(self.theta[j])
            # ローカル->ワールド変換して速度・位置更新
            A = np.array([[cos_alpha, -sin_alpha], [sin_alpha, cos_alpha]])
            u_local = np.array([u_r, u_theta])
            u_world_2d = A @ u_local
            u_world = np.append(u_world_2d, 0)

            new_velocity = u_world * self.frame_time + np.array(
                self.agent_velocity[j]
            )
            self.agent_velocity[j] = new_velocity.tolist()
            updated_position = (
                np.array(self.current_world_agent_positions[j])
                + new_velocity * self.frame_time
            )
            self.current_world_agent_positions[j] = updated_position.tolist()
            

            


            

            # 前回値の更新
            self.prev_ro_i[j] = np.copy(self.ro_i[j])
            self.prev_theta[j] = np.copy(self.theta[j])
            self.prev_relative_coordinates[j] = np.copy(self.relative_coordinates[j])
            self.prev_agent_positions[j] = np.copy(
                self.current_world_agent_positions[j]
            )


        self.target_position += np.array([-0.1, -0.1, 0], dtype=float)

        return self.current_world_agent_positions , self.target_position

        
            
