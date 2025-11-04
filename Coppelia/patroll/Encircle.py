
import numpy as np
from various_calculation import Various
from caluculation import caluculate
from csv_save import save_csv_data

class Siege:
    def __init__(self, num_agents , frame_time , target_position , agent_positions, distance):
        self.various = Various()
        self.num_agents = num_agents
        self.frame_time = frame_time
        self.target_position = target_position
        self.prev_target_position = np.copy(self.target_position)
        self.agent_positions = agent_positions
        self.prev_agent_positions = np.copy(self.agent_positions)
        self.relative_coordinates = []
        self.prev_relative_coordinates = []
        for j in range(self.num_agents):
            relative_coordinates = np.array(self.agent_positions[j]) - np.array(self.target_position)
            prev_relative_coordinates = np.array(self.prev_agent_positions[j]) - np.array(self.prev_target_position)
            self.relative_coordinates.append(relative_coordinates)
            self.prev_relative_coordinates.append(prev_relative_coordinates)
        self.agent_velocities = [np.zeros(3) for _ in range(self.num_agents)]
        self.ro_i = distance
        self.prev_ro_i = []
        for j in range(self.num_agents):
            prev_ro_i = np.linalg.norm(self.prev_agent_positions[j] - self.target_position)
            self.prev_ro_i.append(prev_ro_i)
        self.eta = []
        for j in range(self.num_agents):
            eta = (self.ro_i[j] - self.prev_ro_i[j]) / self.frame_time
            self.eta.append(eta)

        self.theta = []
        self.prev_theta = []
        for j in range(self.num_agents):
            theta = np.arctan2(self.agent_positions[j][1] , self.agent_positions[j][0])
            prev_theta = np.arctan2(self.prev_agent_positions[j][1] , self.prev_agent_positions[j][0])
            self.theta.append(theta)
            self.prev_theta.append(prev_theta)
        self.alpha_i = []
        self.alpha_i_minus = []
        for j in range(self.num_agents):
            j_plus = (j + 1) % num_agents
            j_minus = (j - 1) % num_agents
            alpha_i , alpha_i_minus = self.various.Angular_distance(self.theta[j] , self.theta[j_plus] , self.theta[j_minus])
            self.alpha_i.append(alpha_i)
            self.alpha_i_minus.append(alpha_i_minus)
        self.omega_i = []
        self.omega_i_plus = []
        self.omega_i_minus = []
        for j in range(self.num_agents):
            j_plus = (j + 1) % self.num_agents
            j_minus = (j - 1) % self.num_agents
            omega_i = (self.theta[j] - self.prev_theta[j]) / self.frame_time
            self.omega_i.append(omega_i)
        for j in range(self.num_agents):
            omega_i_plus = np.copy(self.omega_i[j_plus])
            omega_i_minus = np.copy(self.omega_i[j_minus])
            self.omega_i_plus.append(omega_i_plus)
            self.omega_i_minus.append(omega_i_minus)
        self.e_i_1 = [0,0,0,0,0,0]
        self.e_i_2 = [0,0,0,0,0,0]
        self.fi = [0,0,0,0,0,0]
        


    def animate(self , i , Japan_time , current_time , agent_position ,  prev_agent_positions , prev_target_position , target_position):
        self.agent_positions = agent_position
        self.prev_agent_positions = prev_agent_positions
        self.target_position = target_position
        self.prev_target_position = prev_target_position
        for j in range(self.num_agents):
            agent_velocities = (np.array(self.agent_positions[j]) - np.array(self.prev_agent_positions[j])) / self.frame_time
            self.agent_velocities[j] = agent_velocities
            
        for j in range(self.num_agents):
            j_plus = (j + 1) % self.num_agents
            j_minus = (j - 1) % self.num_agents
            self.relative_coordinates[j] = np.array(self.agent_positions[j]) - np.array(self.target_position)
            self.prev_relative_coordinates[j] = np.array(self.prev_agent_positions[j]) - np.array(self.prev_target_position)
            self.ro_i[j] = np.linalg.norm(self.relative_coordinates[j])
            self.prev_ro_i[j] = np.linalg.norm(self.prev_relative_coordinates[j])
            self.eta[j] = (self.ro_i[j] - self.prev_ro_i[j]) / self.frame_time
            self.theta[j] = np.arctan2(self.relative_coordinates[j][1] , self.relative_coordinates[j][0])
            self.prev_theta[j] = np.arctan2(self.prev_relative_coordinates[j][1] , self.prev_relative_coordinates[j][0])
            self.alpha_i[j] , self.alpha_i_minus[j] = self.various.Angular_distance(self.theta[j], self.theta[j_plus], self.theta[j_minus])
        # --- 正規化: 全体合計が 2π になるよう一度だけスケール ---
        total = sum(self.alpha_i)
        if total == 0:
            # 万が一全てゼロなら均等分配（安全策）
            uniform = 2 * np.pi / self.num_agents
            for k in range(self.num_agents):
                self.alpha_i[k] = uniform
                self.alpha_i_minus[k] = uniform
        else:
            scale = 2 * np.pi / total
            for k in range(self.num_agents):
                self.alpha_i[k] = self.alpha_i[k] * scale
                self.alpha_i_minus[k] = self.alpha_i_minus[k] * scale
        for j in range(self.num_agents):
            self.omega_i[j] = (self.theta[j] - self.prev_theta[j]) / self.frame_time
            self.omega_i_plus[j] = np.copy(self.omega_i[j_plus])
            self.omega_i_minus[j] = np.copy(self.omega_i[j_minus])

            u_r , u_theta , self.e_i_1[j] , self.e_i_2[j] , self.fi[j] = caluculate(
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
                self.agent_velocities[j]
            )
            self.agent_velocities[j] = new_velocity.tolist()
            updated_position = (
                np.array(self.agent_positions[j])
                + new_velocity * self.frame_time
            )
            self.agent_positions[j] = updated_position.tolist()

            # 前回値の更新
            self.prev_ro_i[j] = np.copy(self.ro_i[j])
            self.prev_theta[j] = np.copy(self.theta[j])
            self.prev_relative_coordinates[j] = np.copy(self.relative_coordinates[j])
            self.prev_agent_positions[j] = np.copy(self.agent_positions[j])

        self.prev_target_position = np.copy(self.target_position)
        # CSV 保存
        save_csv_data(Japan_time, current_time, self.ro_i, "ro_i")
        save_csv_data(Japan_time, current_time, self.alpha_i, "alpha_i")
        save_csv_data(Japan_time, current_time, self.alpha_i_minus, "alpha_i_minus")
        save_csv_data(Japan_time, current_time, self.omega_i, "omega_i")
        save_csv_data(Japan_time, current_time, self.eta, "eta")
        save_csv_data(Japan_time, current_time, self.e_i_1, "e_i_1")
        save_csv_data(Japan_time, current_time, self.e_i_2, "e_i_2")
        save_csv_data(Japan_time, current_time, self.theta, "theta")
        save_csv_data(Japan_time, current_time, self.fi, "fi")

        return self.agent_positions , self.ro_i