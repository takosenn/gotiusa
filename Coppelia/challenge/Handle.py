# Coppeliasimのハンドルを取得する
# Agentの緑の球(target)とtargetの緑の球(target)、カメラのハンドルを取得する
# カメラはvisionSensorのperspectiveセンサーを選択

from parameter import num_agents
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
client = RemoteAPIClient()
sim = client.require("sim")
drone_handles: list = []
Agent_handles: list = []
visionSensor_handles: list = []

host='127.0.0.1'
port=23000

# 中央のtargetのハンドル
target_handle = sim.getObject("/Quadcopter[0]/target")
print("取得: Quadcopter[0]")

# 各Agentの緑の球(target)のハンドル
for i in range(num_agents):
    object_name = f"Quadcopter[{i+1}]"
    drone_handle = sim.getObject(f"/{object_name}")
    drone_handles.append(drone_handle)
    print(f"取得: {object_name} ")
    object_name = f"Quadcopter[{i+1}]"
    Agent_handle = sim.getObject(f"/{object_name}/target")
    Agent_handles.append(Agent_handle)
    print(f"取得: {object_name} のtarget")
    object_name = f"Quadcopter[{i+1}]"
    visionSensor_handle = sim.getObject(f"/{object_name}/visionSensor")
    visionSensor_handles.append(visionSensor_handle)
    print(f"取得: {object_name}のvisionSensor")
