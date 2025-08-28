
from Handle import sim, Agent_handles, target_handle , visionSensor_handles
import numpy as np

def Liar_distance(j):
    distances = 6
    packed = sim.getStringSignal("ranges1{j+1}")
    if packed:
        arr = sim.unpackFloatTable(packed)
        if len(arr) % 3 == 0:
            points = np.array(arr).reshape(-1, 3)
            distances = np.linalg.norm(points, axis=1)
            distances = np.min(distances)
            print("座標サンプル:", points[:5])
            print("距離サンプル:", distances[:5])
        elif len(arr) > 0:
            distances = np.array(arr)
            distances = np.min(distances)
            print("距離サンプル:", distances[:5])
        else:
            distances = np.array([])
    else:
        distances = np.arrau([])
    return distances


def Lidar_coodinate_target(j, ro_i, i):
    points = None
    packed = sim.getStringSignal("hokuyo_data")
    if packed:
        arr = sim.unpackFloatTable(packed)
        if len(arr) % 3 == 0:
            points = np.array(arr).reshape(-1, 3)
            distances = np.linalg.norm(points, axis=1)
            print("座標サンプル:", points[:5])
            print("距離サンプル:", distances[:5])
        elif len(arr) > 0:
            distances = np.array(arr)
            print("距離サンプル:", distances[:5])
        else:
            points = np.array([])
    else:
        points = np.array([])
    return points
