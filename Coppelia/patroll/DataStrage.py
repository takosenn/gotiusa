# 時間積分値を保持するためのリスト

from parameter import Params

# e_i_1, e_i_2の時間積分値（各エージェントごと）
# ensure the retrieved value is converted to a string (or use a default) before int()
num_agents = int(str(Params.get("num_agents", 0)))
e_i_1_integral = [0.0 for _ in range(num_agents)]
e_i_2_integral = [0.0 for _ in range(num_agents)]
