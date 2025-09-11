
import numpy as np
from parameter import center, radius , frame_time, omega_target, num_agents
from caluculation import caluculate
from neighbors_info import neighbors_info
from initial_image import initial_image
import csv
from datetime import datetime
from simulation import Simulation

# データ保存時の日時
current_time = datetime.now()

fig, ax, point, agent_dots, agent_positions, agent_colors=initial_image()

# --- アニメーション関数 ---
def init():
    point.set_data([0], [radius])
    agent_dots.set_offsets(agent_positions)
    return point, agent_dots

#with open(f"data_x{current_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv", mode="a", newline="" , encoding="utf-8") as file_x:
#    writer = csv.writer(file_x)
#    writer.writerow(["u_r", "u_theta" , "ro_i", "agent_position_x[1]" , "agent_position_x[2]" , "agent_position_x[3]" , "agent_position_x[4]" , "agent_position_x[5]" , "agent_position_x[6]" ]) #xヘッダー行
#with open(f"data_y{current_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv", mode="a", newline="" , encoding="utf-8") as file_y:
#    writer = csv.writer(file_y)
#    writer.writerow(["u_r", "u_theta" , "ro_i", "agent_position_y[1]" , "agent_position_y[2]" , "agent_position_y[3]" , "agent_position_y[4]" , "agent_position_y[5]" , "agent_position_y[6]" ]) #yヘッダー行



def animate(i):
    theta = omega_target * i
    x = center[0] + radius * np.sin(theta)
    y = center[1] + radius * np.cos(theta)
    point.set_data([x], [y])
    agent_dots.set_offsets(agent_positions)
    # 色分けを毎フレーム反映
    #agent_dots.set_color(agent_colors)

    if not hasattr(animate, "prev_agent_pos"):
        animate.prev_agent_pos = agent_positions.copy()
    if not hasattr(animate, "prev_target_pos"):
        animate.prev_target_pos = np.array([x, y])

    for j in range(num_agents):
        vec = agent_positions[j] - np.array([x, y])
        theta_now = np.arctan2(vec[1], vec[0])
        if not hasattr(animate, "prev_theta"):
            animate.prev_theta = np.zeros(num_agents)
        omega_i = theta_now - animate.prev_theta[j]
        omega_i = (omega_i + np.pi) % (2 * np.pi) - np.pi
        ro_i = np.linalg.norm(vec)  # agentとtargetとの間の距離をベクトルの計算で求めた

        animate.prev_theta[j] = theta_now

        neighbor_info = neighbors_info(j, agent_positions, x, y, animate, theta_now)

        # --- 制御プロトコルu_iの計算と位置更新 ---
        # 放射方向・接線方向の単位ベクトル
        e_r = vec / ro_i
        e_theta = np.array([-e_r[1], e_r[0]])
        # targetの速度ベクトルを計算
        target_velocity = np.array(
            [
                -radius * omega_target * np.cos(theta),  # x方向の速度成分
                -radius * omega_target * np.sin(theta)  # y方向の速度成分
            ]
        )
        # エージェントの速度ベクトルを計算
        agent_velocity = (
            agent_positions[j] - animate.prev_agent_pos[j]
        ) / frame_time
        # 相対速度の計算
        relative_velocity = agent_velocity - target_velocity
        # 相対速度をローカル座標系（極座標）に変換
        relative_velocity_r = np.dot(relative_velocity, e_r)
        relative_velocity_theta = np.dot(relative_velocity, e_theta)
        eta = relative_velocity_r
        eta_norm = abs(eta)
        result = caluculate(i,j,neighbor_info[0],neighbor_info[1],neighbor_info[2],omega_i,neighbor_info[3],ro_i,eta_norm)
        
        # 合成速度ベクトル
        u_vec = result[0] * e_r + result[1] * e_theta
        # 位置更新（タイムステップdt=0.05）
        agent_positions[j] += u_vec * frame_time

        position_synchronization = Simulation()
        position_synchronization.Position_Synchronization()

        #with open(f"data_x{current_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv", mode="a", newline="" , encoding="utf-8") as file_x:
        #    writer = csv.writer(file_x)
        #    writer.writerow([result[0], result[1], ro_i, agent_positions[0][0] , agent_positions[1][0] , agent_positions[2][0] , agent_positions[3][0] , agent_positions[4][0] , agent_positions[5][0]])     # データをCSVに書き込む
        #
        #with open(f"data_y{current_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv", mode="a", newline="" , encoding="utf-8") as file_y:
        #    writer = csv.writer(file_y)
        #    writer.writerow([result[0], result[1], ro_i, agent_positions[0][1] , agent_positions[1][1] , agent_positions[2][1] , agent_positions[3][1] , agent_positions[4][1] , agent_positions[5][1]])     # データをCSVに書き込む
        
    # 前の位置を更新
    animate.prev_agent_pos = agent_positions.copy()
    animate.prev_target_pos = np.array([x, y])
    return point, agent_dots