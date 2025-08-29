
from Handle import sim, Agent_handles, target_handle , Lidar_handles
import numpy as np

def Lidar_distance(j):
    distances = 6
    packed = [sim.getStringSignal("ranges11"),sim.getStringSignal("ranges12"),sim.getStringSignal("ranges13"),sim.getStringSignal("ranges14")]
    if packed:
        arr = sim.unpackFloatTable(packed[j])
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
        distances = np.array([])
    return distances


def Lidar_coodinate_target(j):
    packed = [sim.getStringSignal("ranges11"),sim.getStringSignal("ranges12"),sim.getStringSignal("ranges13"),sim.getStringSignal("ranges14")]
    if packed:
        arr = sim.unpackFloatTable(packed[j])
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
