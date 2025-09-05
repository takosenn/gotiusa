
from Handle import sim , visionSensor_handles , Agent_handles
from parameter import measurable_distance
import numpy as np
import math

class visionSensor:
    def __init__(self , j):
        self.j = j
    
    def visionSensor_read(self):
        result = sim.handleVisionSensor(visionSensor_handles[self.j])
        result = sim.getVisionSensorDepth(visionSensor_handles[self.j], 1, [0, 0], [0, 0])
        if isinstance(result, tuple) and len(result) ==2:
            depth_bytes , resolution = result
        floatingNumbers = sim.unpackFloatTable(depth_bytes , 0 , 0 , 0)
        floatingNumbers = np.array(floatingNumbers)
        return floatingNumbers
    
    def visionSensor_min_distance(self):
        floatingNumbers = self.visionSensor_read()
        filtered = floatingNumbers[(floatingNumbers > 0.1) & (floatingNumbers < measurable_distance)]
        #print(filtered)
        ro_i = min(floatingNumbers)
        #ro_i = min(visionSenosr_distance)  # 画面内の最短距離[m] カメラから見た物体までの距離
        return ro_i

    def visionSensor_ViewAngle(self):
        ro_i = self.visionSensor_min_distance()
        if ro_i > 4:  # 広い視野角（84.6度）
            sim.setObjectFloatParam(
                visionSensor_handles[self.j],
                sim.visionfloatparam_perspective_angle,
                math.radians(30),
            )
        else:  # 狭い視野角（30度）
            sim.setObjectFloatParam(
                visionSensor_handles[self.j],
                sim.visionfloatparam_perspective_angle,
                math.radians(15),
            )
        print(f"Agent{self.j+1} visionSensor 測定成功: 距離 = {ro_i:.3f} [m]")

