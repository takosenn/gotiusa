import numpy as np
from parameter import center, radius, frame_time, omega_target, num_agents
from caluculation import caluculate
from connect_Coppelia import Simulation
import time
import csv
from datetime import datetime

# データ保存時の日時

class Animation:
    def __init__(self):
        self.sim = Simulation()
        self.sim.get_handles(num_agents)
        self.agent_positions = []
        for i in range(num_agents):
            theta = 2 * np.pi * i / num_agents
            agent_position = [center[0] + 5 * np.cos(theta) , center[1] + radius + 5 * np.sin(theta) , 2]
            self.agent_positions.append(agent_position)
            self.sim.initial_setAgentpositions(i, agent_position)
        self.prev_agent_positions = self.agent_positions
        self.target_position = [0 , 5 ,2]
        self.sim.initial_settargetposition(self.target_position)
        self.prev_target_position = []
        self.ro_i = []
        self.coordinates = []
        self.prev_theta = np.zeros(num_agents)
        self.prev_theta_plus = np.zeros(num_agents)
        self.prev_theta_minus =np.zeros(num_agents)
        self.omega_i = []
        self.omega_i_plus = []
        self.omega_i_minus = []
        self.alpha_i = []
        self.alpha_i_minus = []
        self.prev_time = time.time()

    def animate(self , i):
        current_time = time.time()
        delta_time = current_time - self.prev_time
        j = i % num_agents
        j_plus = (i+1) % num_agents
        j_minus = (i-1) % num_agents

        theta_target = omega_target * i
        self.target_position = [center[0]  + radius * np.sin(theta_target) , center[1]  + radius * np.cos(theta_target) , 2]

        vec = np.array(self.agent_positions[j]) - np.array(self.target_position)                    
        vec_plus = np.array(self.agent_positions[j_plus]) - np.array(self.target_position)          
        vec_minus = np.array(self.agent_positions[j_minus]) - np.array(self.target_position)        
        theta = np.arctan2(vec[1] , vec[0])                                                         
        theta_plus = np.arctan2(vec_plus[1] , vec_plus[0])
        print(theta_plus)
        theta_minus = np.arctan2(vec_minus[1] , vec_minus[0])

        self.ro_i = np.linalg.norm(vec)
        #角速度の計算
        self.omega_i = theta - self.prev_theta[j]
        self.omega_i_plus = theta_plus - self.prev_theta_plus[j]
        self.omega_i_minus = theta_minus - self.prev_theta_minus[j]
        
        self.omega_i = (self.omega_i + np.pi) % (2 * np.pi) - np.pi
        self.omega_i_plus = (self.omega_i_plus + np.pi) % (2 * np.pi) - np.pi
        self.omega_i_minus = (self.omega_i_minus + np.pi) % (2 * np.pi) - np.pi


        #前回のthetaを保持
        self.prev_theta[j] = theta
        self.prev_theta_plus[j] = theta_plus
        self.prev_theta_minus[j] = theta_minus
        #agent間の角距離計算
        diff = abs(theta - theta_plus)
        self.alpha_i = min(diff, 2 * np.pi - diff)
        diff_minus = abs(theta - theta_minus)
        self.alpha_i_minus = min(diff_minus, 2 * np.pi - diff_minus)

        # 放射方向・接線方向の単位ベクトル
        e_r = vec / self.ro_i
        e_theta = np.array([-e_r[1], e_r[0]])

        # targetの速度ベクトルを計算
        target_velocity = np.array(
            [
                -radius * omega_target * np.cos(theta),  # x方向の速度成分
                -radius * omega_target * np.sin(theta),  # y方向の速度成分
                0
            ]
        )
        self.target_position += target_velocity * delta_time

        # エージェントの速度ベクトルを計算(現在の位置と前の位置から)
        agent_velocity = (np.array(self.agent_positions[j]) - np.array(self.prev_agent_positions[j])) / delta_time
        self.prev_time = current_time

        # 相対速度の計算
        relative_velocity = agent_velocity - target_velocity

        # 相対速度をローカル座標系（極座標）に変換
        relative_velocity_r = np.dot(relative_velocity, e_r)
        eta = relative_velocity_r
        eta_norm = abs(eta)
        result = caluculate(
            i,
            j,
            self.alpha_i,
            self.alpha_i_minus,
            self.omega_i_plus,
            self.omega_i,
            self.omega_i_minus,
            self.ro_i,
            eta_norm,
        )
        # 合成速度ベクトル
        e_r = np.delete(e_r , 2)
        u_vec = result[0] * e_r + result[1] * e_theta
        u_vec = np.append(u_vec , 0)
        #print(u_vec)

        self.agent_positions[j] += u_vec * delta_time

        # with open(f"data_x{current_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv", mode="a", newline="" , encoding="utf-8") as file_x:
        #    writer = csv.writer(file_x)
        #    writer.writerow([result[0], result[1], ro_i, agent_positions[0][0] , agent_positions[1][0] , agent_positions[2][0] , agent_positions[3][0] , agent_positions[4][0] , agent_positions[5][0]])     # データをCSVに書き込む
        #
        # with open(f"data_y{current_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv", mode="a", newline="" , encoding="utf-8") as file_y:
        #    writer = csv.writer(file_y)
        #    writer.writerow([result[0], result[1], ro_i, agent_positions[0][1] , agent_positions[1][1] , agent_positions[2][1] , agent_positions[3][1] , agent_positions[4][1] , agent_positions[5][1]])     # データをCSVに書き込む

        # 前の位置を更新
        self.prev_agent_positions[j] = self.agent_positions[j]
        self.prev_target_position = self.target_position

        # Coppeliasim側でAgentの緑の球(target)の位置同期
        for j in range(num_agents):
            Agents_pos_3d = [
                float(self.agent_positions[j][0]),
                float(self.agent_positions[j][1]),
                2.0,
            ]
            #print(f"これはAgent{j+1}の位置{Agents_pos_3d}")
            self.sim.setAgentposition(j, Agents_pos_3d)
        target_pos_3d = [float(self.target_position[0]), float(self.target_position[1]), 2.0]
        self.sim.settargetposition(target_pos_3d)
