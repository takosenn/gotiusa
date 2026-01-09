# これを実行するとシミュレーションスタート

from parameter import Params
from animation import Animation
from patroll import Patroll
from lineformation import LineFormation
from connect_Coppelia import Simulation
import time
import numpy as np


# import japanize_matplotlib      # type: ignore


class Main:
    def __init__(self):
        self.sim = Simulation()
        # Simulationのハンドルを取得してからAnimationに同じインスタンスを渡す
        self.sim.get_handles(Params["num_agents"])
        self.ani = Animation()
        self.patroll = Patroll()
        self.line = LineFormation()
        self.ani.sim = self.sim
        self.patroll.sim = self.sim
        self.line.sim = self.sim

        # ターゲットの[0,0]への移動パラメータ（Paramsから取得）
        self.target_move_speed = Params["target_move_speed"]  # 移動速度[m/s]
        self.target_goal = np.array(
            [Params["target_goal_x"], Params["target_goal_y"]]
        )  # 目標位置[x, y]
        self.target_reached_goal = False  # 目標位置に到達したか
        self.target_tolerance = Params["target_tolerance"]  # 到達判定の許容誤差[m]
        self.target_position = None  # ターゲットの現在位置
        self.target_initial_z = None  # ターゲットのz座標

        # フォーメーション状態管理
        self.line_formation_complete = False  # 直線フォーメーションが完成したか

    def run(self):
        try:
            self.sim.connect()
            self.sim.start_simulation()

            # CoppeliaSim から初期位置を取得
            print("CoppeliaSim から初期位置を取得中...")
            initial_target_pos, initial_agent_pos = self.sim.get_Drone_position()
            print(f"Target初期位置: {initial_target_pos}")
            print(f"Agent初期位置: {initial_agent_pos}")

            # ターゲットの初期化
            self.target_position = list(initial_target_pos)
            self.target_initial_z = initial_target_pos[2]
            print(
                f"Target: 初期位置 = [{self.target_position[0]:.3f}, {self.target_position[1]:.3f}, {self.target_position[2]:.3f}]"
            )
            print(
                f"Target: 目標位置 = [{self.target_goal[0]:.3f}, {self.target_goal[1]:.3f}]\n"
            )

            for i in range(Params["frames"]):
                print(f"現在のfor文を読んだ回数: {i}回目")
                # CoppeliaSim から現在の座標を取得
                target_position, agent_positions = self.sim.get_Drone_position()

                # ターゲットの位置を更新（毎フレーム実行）
                if Params["target_move"]:
                    self._update_target_position()
                    # 更新したターゲット位置をCoppeliaSimに反映
                    self.sim.settargetposition(self.target_position)
                    # 更新後のターゲット位置を使用
                    target_position = self.target_position

                # 全エージェントの相対距離の最小値を計算
                min_ro_i = min(
                    self.ani.various.Distance(
                        np.array(agent_positions[j]) - np.array(target_position)
                    )
                    for j in range(Params["num_agents"])
                )

                # 取得した座標を使って計算
                if min_ro_i >= 5:
                    # 距離が5m以上の場合は巡回
                    self.patroll.animate(agent_positions)
                    self.line_formation_complete = False  # 巡回に戻ったらリセット
                elif not self.line_formation_complete:
                    # 距離が5m未満で、直線フォーメーションが未完成の場合
                    self.line_formation_complete = self.line.animate(
                        target_position, agent_positions
                    )
                else:
                    # 直線フォーメーションが完成したら円形フォーメーション
                    self.ani.animate(i, target_position, agent_positions)
                time.sleep(Params["frame_time"])
                self.sim.step_simulation()
        except KeyboardInterrupt:
            print("\nctrl+Cでシミュレーションが終了しました")
        except Exception as e:
            print(f"\nエラーが発生しました: {type(e).__name__}: {e}")
            print("シミュレーションを停止します...")
        finally:
            print("CoppeliaSim を停止中...")
            self.sim.stop_simulation()
            print("シミュレーション終了")

    def _update_target_position(self):
        """ターゲットを[0,0]に向けて移動させる"""
        current_pos_2d = np.array([self.target_position[0], self.target_position[1]])
        distance_to_goal = np.linalg.norm(current_pos_2d - self.target_goal)

        # print(
        #    f"Target更新: 現在位置=[{current_pos_2d[0]:.3f}, {current_pos_2d[1]:.3f}], 目標までの距離={distance_to_goal:.3f}m"
        # )

        if distance_to_goal > self.target_tolerance:
            # 目標位置に向かって移動
            direction = (self.target_goal - current_pos_2d) / distance_to_goal
            movement = direction * self.target_move_speed * Params["frame_time"]

            # 移動量が残り距離より大きい場合は、目標位置に直接移動
            if np.linalg.norm(movement) > distance_to_goal:
                self.target_position = [
                    self.target_goal[0],
                    self.target_goal[1],
                    self.target_initial_z,
                ]
                if not self.target_reached_goal:
                    print(f"Target が目標位置 [0, 0] に到達しました")
                    self.target_reached_goal = True
            else:
                new_pos_2d = current_pos_2d + movement
                self.target_position = [
                    new_pos_2d[0],
                    new_pos_2d[1],
                    self.target_initial_z,
                ]
                # print(
                #    f"Target移動後: 新位置=[{self.target_position[0]:.3f}, {self.target_position[1]:.3f}]"
                # )
        else:
            # 目標位置に到達済み（静止）
            self.target_position = [
                self.target_goal[0],
                self.target_goal[1],
                self.target_initial_z,
            ]
            if not self.target_reached_goal:
                print(f"Target が目標位置 [0, 0] に到達しました")
                self.target_reached_goal = True


controller = Main()
controller.run()
