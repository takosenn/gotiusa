from coppeliasim_zmqremoteapi_client import RemoteAPIClient  # type: ignore[import]
import time


client = RemoteAPIClient()
sim = client.require("sim")
# 同期モード（ステップ実行）を有効にする
sim.setStepping(True) # [4]
sim.startSimulation()
target_simulation_time = 3.0 # 3秒間シミュレーションを実行
current_sim_time = sim.getSimulationTime()
while current_sim_time < target_simulation_time:
    print(f"シミュレーション時間: {current_sim_time:.2f} [s]")
    # (ここでロボットの制御などを行う)
    time.sleep(1)
    sim.step() # シミュレーションを1ステップ進める [4]
    current_sim_time = sim.getSimulationTime()
sim.stopSimulation()
print("同期モードでのシミュレーションが終了しました。")