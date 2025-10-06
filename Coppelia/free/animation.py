import numpy as np
from connect_Coppelia import Simulation
from parameter import num_agents , frame_time , omega_target
from various_calculation import coordinate_trans

class Animation:
    def __init__(self):
        self.sim = Simulation()
        self.ro_i = [5 , 5 , 5 , 5 , 5 , 5]
        self.prev_ro_i = [5 , 5 , 5 , 5 , 5 , 5]
        self.target_position = [0 , 5 , 2]
        self.current_world_agent_positions = []
        for i in range(num_agents):
            current_world_agent_positions = [5 * np.cos(i * np.pi / 3) , 5 + 5 * np.sin(i * np.pi / 3) , 2]
            self.current_world_agent_positions.append(current_world_agent_positions)
        self.local_agent_positions = []
        for i in range(num_agents):
            local_agent_positions = np.array(self.current_world_agent_positions[i] - np.array(self.target_position))
            self.local_agent_positions.append(local_agent_positions)
        self.prev_local_agent_positions = [pos.copy() for pos in self.local_agent_positions]
        self.prev_prev_local_agent_positions = [pos.copy() for pos in self.prev_local_agent_positions]
        self.theta = []
        for i in range(num_agents):
            theta = i * np.pi / 3
            self.theta.append(theta)
        self.prev_theta = []
        for i in range(num_agents):
            prev_theta = i * np.pi / 3
            self.prev_theta.append(prev_theta)
        self.omega_i = [0 , 0 , 0 , 0 , 0 , 0]
        self.prev_omega_i = [0 , 0 , 0 , 0 , 0 , 0]


    def animate(self , i):
        
        
        #ここから下はtargetの位置更新
        target_theta = (omega_target * i) % (2 * np.pi)
        target_x = 5 * np.sin(target_theta)
        target_y = 5 * np.cos(target_theta)
        self.target_position = [target_x , target_y , 2]

        
        #ここから下はAgentの位置更新
        j = i % num_agents
        j_plus = (i + 1) % num_agents
        j_minus = (i - 1) % num_agents


        print(f"現在のAgent[{j+1}]のWorld座標系の位置座標: {self.current_world_agent_positions[j]}")


        self.local_agent_positions[j] = np.array(self.current_world_agent_positions[j]) - np.array(self.target_position)     #targetから見たAgentの座標(x,y,zの要素3つ)
        print(f"targetから見たAgent[{j + 1}]の座標: {self.local_agent_positions[j]}")
        self.ro_i[j] = np.linalg.norm(self.local_agent_positions[j])                                              #target-Agent間の距離(スカラー)
        print(f"targetとAgent[{j+1}]の距離: {self.ro_i[j]}")


        self.theta[j] = np.arctan2(self.local_agent_positions[j][1] , self.local_agent_positions[j][0])
        print(f"targetとAgent[{j+1}]とのなす角度: {self.theta[j]}")
        self.omega_i[j] = (self.theta[j] - self.prev_theta[j]) / frame_time
        print(f"Agent[{j+1}]がtargetの周りを回る角速度: {self.omega_i[j]}")


        eta = (self.ro_i[j] - self.prev_ro_i[j]) / frame_time
        print(f"targetとAgent[{j+1}]の距離の時間微分: {eta}")
        

        agent_velocity = (np.array(self.prev_local_agent_positions[j]) - np.array(self.prev_prev_local_agent_positions[j])) / frame_time
        print(f"Agent[{j+1}]の速度: {agent_velocity}")                                                         #ワールド座標系のAgentの速度


        local_agent_velocity = coordinate_trans(self.theta[j] , agent_velocity[:2])
        print(f"ローカル速度: {local_agent_velocity}")


        updated_position = np.array(self.current_world_agent_positions[j]) + [1 , 1 , 0]                               #位置更新の式(x=1,y=1,z=0だけ位置更新)
        self.current_world_agent_positions[j] = updated_position.tolist()                                              #要素に追加
        print(f"位置座標更新後のAgent[{j + 1}]のWorld座標系の位置: {np.array(self.current_world_agent_positions[j])}")


        #ここから上のself.prev_ro_iは前回のself.ro_iをコピーできてる
        self.prev_ro_i[j] = np.copy(self.ro_i[j])
        print(f"前回のtargetとAgent[{j+1}]との距離を正しくコピーできているか確認: {self.prev_ro_i[j]}")


        self.prev_theta[j] = np.copy(self.theta[j])
        print(f"前回のtargetとAgent[{j+1}]との角度を正しくコピーできているか確認: {self.prev_theta[j]}")


        self.prev_prev_local_agent_positions[j] = np.copy(self.prev_local_agent_positions[j])
        print(f"前回のtargetから見たAgent[{j+1}]の位置を正しくコピーできているか確認: {self.prev_prev_local_agent_positions[j]}")


        #ここから上はself.prev_agent_positionsは前回のself.aget_positionsをコピーできてる
        self.prev_local_agent_positions[j] = np.copy(self.current_world_agent_positions[j])
        print(f"今回のtargetから見たAgent[{j+1}]の位置を正しくコピーできているか確認: {self.prev_local_agent_positions[j]}")

        """Coppeliasim上のAgentの位置同期"""
        self.sim.setAgentposition(j , self.current_world_agent_positions[j])

        self.sim.settargetposition(self.target_position)


        print("\n")