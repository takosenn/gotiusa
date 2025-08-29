# Coppeliasimのハンドルを取得する
# Agentの緑の球(target)とtargetの緑の球(target)、カメラのハンドルを取得する
# カメラはvisionSensorのperspectiveセンサーを選択

from parameter import num_agents
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

client = RemoteAPIClient()
sim = client.require("sim")
drone_handles: list = []
Agent_handles: list = []
Lidar_handles: list = []

# 中央のtargetのハンドル
target_handle = sim.getObject("/Quadcopter[0]/target")
sim.writeCustomDataBlock(target_handle, "drone_role", "target")
print("取得: Quadcopter[0]")

# Agentのハンドル
for i in range(num_agents):
    # 各Agentのドローン本体のハンドル
    object_name = f"Quadcopter[{i+1}]"
    drone_handle = sim.getObject(f"/{object_name}")
    drone_handles.append(drone_handle)
    print(f"取得: {object_name} ")
    # 各Agentの緑の球(target)のハンドル
    object_name = f"Quadcopter[{i+1}]"
    Agent_handle = sim.getObject(f"/{object_name}/target")
    sim.writeCustomDataBlock(Agent_handle, "drone_role", "Agent")
    Agent_handles.append(Agent_handle)
    print(f"取得: {object_name} のtarget")
    # 各AgentのLidarのハンドル
    object_name = f"Quadcopter[{i+1}]"
    Lidar_handle = sim.getObject(f"/{object_name}/fastHokuyo")
    Lidar_handles.append(Lidar_handle)
    print(f"取得: {object_name}のLidar")
