
from parameter import num_agents
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

class Simulation:
    def __init__(self):
        self.client = RemoteAPIClient()
        self.sim = self.client.getObject("sim")
        self.Agent_handles = []
        self.Target_handle = -1

    def Get_AgentHandle(self):
        for i in range(num_agents):
            object_name = f"Quadcopter[{i+1}]"
            Agent_handle = self.sim.getObject(f"/{object_name}/target")
            self.Agent_handles.append(self.Agent_handle)
            print(f"取得: Quadcopter[{i+1}]のtarget")
        return self.Agent_handles

    def Get_TargetHandle(self):
        self.Target_handle = self.sim.getObject("/Quadcopter[0]/target")
        print(f"取得: Quadcopter[0]のtarget")
        return self.Target_handle

    def Position_Synchronization(self , Agents_pos_3d , Target_pos_3d):
        self.sim.setObjectPosition(self.Agent_handles , -1 , Agents_pos_3d)
        self.sim.setObjectPosition(self.Target_handle , -1 , Target_pos_3d)