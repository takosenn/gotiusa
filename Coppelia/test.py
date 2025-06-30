
from coppeliasim_zmqremoteapi_client import RemoteAPIClient  # type: ignore
 
# CoppeliaSimに接続 (デフォルト: localhost, port 23000) 
client = RemoteAPIClient() # [3, 4] 
 
# 'sim'オブジェクトを取得して、シミュレーション関数にアクセス 
sim = client.require('sim') # または sim = client.getObject('sim') [3, 4] 
 
# --- ここからCoppeliaSimのAPI関数を呼び出す --- 
# 例: シミュレーション時間を取得 
simulation_time = sim.getSimulationTime() 
print(f"現在のシミュレーション時間: {simulation_time}秒") 
 
# --- 処理が終了したら、特に明示的な切断処理は不要 --- 
# 'client'オブジェクトがスコープを抜けるか、プログラムが終了する際に自動的にクリーンアップされる 

from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time

client = RemoteAPIClient()
sim = client.require('sim')

# ドローンのオブジェクトハンドルを取得（名前はシーンにより異なる）
drone_handle = sim.getObject('/Quadricopter')

# 現在位置を取得
start_pos = sim.getObjectPosition(drone_handle, -1)

# Y軸方向に1メートル移動
target_pos = [start_pos[0], start_pos[1] + 1.0, start_pos[2]]

# 位置を設定（瞬間移動）
sim.setObjectPosition(drone_handle, -1, target_pos)

