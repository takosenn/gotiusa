import numpy as np
import time
import matplotlib.pyplot as plt
from Handle import sim, Agent_handles, target_handle

# ドローンの初期位置リスト
init_positions = [[6, 0, 2], [0, 6, 2], [-6, 0, 2], [0, -6, 2]]
target_pos = [0, 0, 2]
speed = 1  # m/s

# 各ドローンのvisionSensorハンドルを取得
vision_sensor_handles = [
    sim.getObject(f"/Quadcopter[{i+1}]/visionSensor") for i in range(4)
]

# 各ドローンの初期位置をセット
for i, pos in enumerate(init_positions):
    sim.setObjectPosition(Agent_handles[i], sim.handle_world, pos)
sim.setObjectPosition(target_handle, sim.handle_world, target_pos)

# シミュレーション開始
if sim.getSimulationState() == sim.simulation_stopped:
    sim.startSimulation()
else:
    sim.stopSimulation()
    sim.startSimulation()
print("Simulation started")

# 4つのサブプロットで画像を同時表示
fig, axs = plt.subplots(2, 2, figsize=(8, 8))
plt.ion()

stopped = [False] * 4
try:
    # シミュレーション開始・ループ処理
    while not all(stopped):
        if not plt.fignum_exists(fig.number):
            print("ウィンドウが閉じられたので終了します")
            break
        for i in range(4):
            if stopped[i]:
                continue
            result = sim.handleVisionSensor(vision_sensor_handles[i])
            result = sim.getVisionSensorDepth(vision_sensor_handles[i], 1, [0, 0], [0, 0])
            if isinstance(result, tuple) and len(result) == 2:
                depth_bytes, resolution = result  # resolutionは解像度[256,256]を表す

                # bytes → float32配列に変換
                floatingNumbers = sim.unpackFloatTable(depth_bytes, 0, 0, 0)
                ro_i = min(floatingNumbers)  # 画面内の最短距離[m]
            print(f"visionSensorで測定した距離: {ro_i: .3f}[m]")
            pos = sim.getObjectPosition(Agent_handles[i], sim.handle_world)
            dist = np.linalg.norm(np.array(pos) - np.array(target_pos))
            print(f"Drone{i+1} 距離: {dist:.2f} m  現在位置: {pos}")
            # 画像取得
            img, resX, resY = sim.getVisionSensorCharImage(vision_sensor_handles[i])
            img = np.frombuffer(img, dtype=np.uint8).reshape(resY, resX, 3)
            img = np.flipud(img)
            ax = axs[i // 2, i % 2]
            ax.clear()
            ax.imshow(img)
            ax.set_title(f"Drone{i+1} VisionSensor")
            # 進行方向ベクトル
            direction = np.array(target_pos) - np.array(pos)
            direction[2] = 0
            norm = np.linalg.norm(direction)
            if norm == 0 or dist < 2:
                stopped[i] = True
                continue
            direction = direction / norm
            velocity = direction * speed
            new_pos = np.array(pos) + velocity * 0.1
            sim.setObjectPosition(Agent_handles[i], sim.handle_world, new_pos.tolist())
        plt.pause(0.01)
        time.sleep(0.1)

    time.sleep(1)
finally:
    # シミュレーション停止
    sim.stopSimulation()
    print("CoppeliaSimシミュレーションを停止しました")
