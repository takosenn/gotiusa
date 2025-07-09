# connect Coppeliasim
# Coppeliasimに繋げる

from coppeliasim_zmqremoteapi_client import RemoteAPIClient

# CoppeliaSim 接続
client = RemoteAPIClient()
sim = client.require("sim")

# ドローン Agent数 4台
num_agents = 6
drone_handles = []

# ドローンハンドル取得
for i in range(num_agents):
    object_name = f"Quadcopter[{i+1}]"  # Quadcopter[1] ~ Quadcopter[4]
    drone_handle = sim.getObject(
        f"/{object_name}/target"
    )  # シーン内のオブジェクト名に合わせて修正
    drone_handles.append(drone_handle)
    print("取得: Agent")

# Targetオブジェクト取得（ここをループ外で1回だけ！）
target_handle = sim.getObject(
    "/Quadcopter[0]/target"
)  # シーン内のtarget名に合わせて修正
print("取得: target")

# 各エージェントのtargetハンドルを取得
agent_target_handles = [
    sim.getObject(f"/Quadcopter[{i}]/target") for i in range(1, num_agents + 1)
]

# VisionSensorハンドルを取得
visionSensorHandles = [
    sim.getObject(f"/Quadcopter[{i}]/visionSensor") for i in range(1, num_agents + 1)
]

# シミュレーション開始
if sim.getSimulationState() == sim.simulation_stopped:
    sim.startSimulation()
    print("Simulation started")
