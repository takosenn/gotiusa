
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import numpy as np
import time

class Target_Move:
    def __init__(self):
        self.client = RemoteAPIClient()
        self.sim = self.client.require("sim")
        self.target_Drone_handle = self.sim.getObject("/Quadcopter[0]")
        self.target_handle = self.sim.getObject("/Quadcopter[0]/target")
        self.target_pos = [0 , 5 , 2]
        self.target_theta = 0
        self.target_omega = 0.12
        self.frame_time = 0.02
        self.radius = 5


    def set_target_pos(self , target_position):
        self.sim.setObjectPosition(self.target_handle , -1 , target_position)


    def run(self):
        try :
            #self.client.setStepping(True)  # 必要に応じて同期モードを有効にする
            self.sim.stopSimulation()
            time.sleep(1)  # 確実に停止するのを待つ
            self.sim.startSimulation()
            self.set_target_pos(self.target_pos)
            for i in range(10000):
                self.target_theta = self.target_omega * i * self.frame_time
                current_time = i * self.frame_time
                print(f"現在の経過時間：{current_time}")
                target_x = self.radius * np.sin(self.target_theta)
                target_y = self.radius * np.cos(self.target_theta)
                self.target_pos = [target_x , target_y , 2]
                self.set_target_pos(self.target_pos)
                #self.client.step()

        except KeyboardInterrupt:
            print("ctrl+Cでシミュレーションが終了しました")
        finally:
            self.sim.stopSimulation()

move = Target_Move()
move.run()

