from parameter import num_agents
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

client = RemoteAPIClient()
sim = client.require("sim")
Agent_handles = []

# 各Agentの緑の球(target)のハンドル
for i in range(num_agents):
    object_name = f"Quadcopter[{i+1}]"
    Agent_handle = sim.getObject(f"/{object_name}/target")
    Agent_handles.append(Agent_handle)
    print(f"取得: {object_name}")

# 中央のtargetのハンドル
target_handle = sim.getObject("/Quadcopter[0]/target")
print("取得: Quadcopter[0]")
