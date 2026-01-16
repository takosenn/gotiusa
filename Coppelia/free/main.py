# これを実行するとシミュレーションスタート

from parameter import Params
from animation import Animation
from patroll import Patroll
from lineformation import LineFormation
from connect_Coppelia import Simulation
from various_calculation import Various
from csv_save import plot_csv_data, save_error_csv_data
import time
import numpy as np


# import japanize_matplotlib      # type: ignore


class Main:
    def __init__(self):
        self.sim = Simulation()
        # Simulationのハンドルを取得してからAnimationに同じインスタンスを渡す
        self.ani = Animation()
        self.patroll = Patroll()
        self.line = LineFormation()
        self.various = Various()
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
        self.circle_formation_started = False  # 円形フォーメーションが始まったか
        self.formation_switch_counter = (
            0  # 円形フォーメーション切り替え条件のカウンター
        )

    def run(self):
        try:
            self.sim.connect()
            self.sim.get_handles(Params["num_agents"])
            self.sim.start_simulation()

            # 同期モード（ステップ実行）を有効にする
            self.sim.client.setStepping(True)

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

            # 時間ベースのシミュレーションループ
            target_simulation_time = (
                Params["frames"] * Params["frame_time"]
            )  # 総シミュレーション時間[s]
            print(
                f"同期モードでシミュレーション開始（目標時間: {target_simulation_time:.1f}秒）\n"
            )

            i = 0  # フレームカウンター
            current_sim_time = self.sim.sim.getSimulationTime()

            while current_sim_time < target_simulation_time:
                print(f"シミュレーション時間: {current_sim_time:.2f}秒 (フレーム: {i})")

                # CoppeliaSim から現在の座標を取得
                target_position, agent_positions = self.sim.get_Drone_position()

                # 全エージェントの角度を計算
                theta = []
                for j in range(Params["num_agents"]):
                    relative_pos = np.array(agent_positions[j]) - np.array(
                        target_position
                    )
                    theta.append(self.various.Theta(relative_pos))

                # theta順にソートして角距離を計算
                theta_with_index = [(j, theta[j]) for j in range(Params["num_agents"])]
                theta_with_index.sort(key=lambda x: x[1])  # theta値でソート（小さい順）

                # 角距離alpha_iを計算
                alpha_i = []
                for idx in range(Params["num_agents"]):
                    current_agent = theta_with_index[idx]
                    next_agent = theta_with_index[(idx + 1) % Params["num_agents"]]

                    diff = next_agent[1] - current_agent[1]
                    if diff >= 0:
                        alpha = diff
                    else:
                        alpha = diff + (2 * np.pi)
                    alpha_i.append(alpha)

                # 誤差を計算（毎フレーム）
                target_error, agent_errors = self.sim.get_position_errors()

                # CSV保存が有効な場合、誤差データを保存
                if Params["save_csv"]:
                    current_time = i * Params["frame_time"]
                    from animation import Japan_time

                    save_error_csv_data(
                        Japan_time, current_time, target_error, agent_errors
                    )

                # 10フレームごとに誤差を表示
                if i % 10 == 0:
                    print(f"\n=== 位置誤差 (フレーム {i}) ===")
                    print(
                        f"Target誤差: [{target_error[0]:.4f}, {target_error[1]:.4f}, {target_error[2]:.4f}] m"
                    )
                    print(f"Target誤差ノルム: {np.linalg.norm(target_error):.4f} m")
                    for j, agent_error in enumerate(agent_errors):
                        error_norm = np.linalg.norm(agent_error)
                        print(
                            f"Agent[{j}]誤差: [{agent_error[0]:.4f}, {agent_error[1]:.4f}, {agent_error[2]:.4f}] m (ノルム: {error_norm:.4f} m)"
                        )
                    print("=" * 40 + "\n")

                # ターゲットの位置を更新（毎フレーム実行）
                if Params["target_move"]:
                    self._update_target_position()
                    # 更新したターゲット位置をCoppeliaSimに反映
                    self.sim.settargetposition(self.target_position)
                    # 更新後のターゲット位置を使用
                    target_position = self.target_position

                # 全エージェントの相対距離を計算
                ro_i_list = []
                for j in range(Params["num_agents"]):
                    ro_i = self.ani.various.Distance(
                        np.array(agent_positions[j]) - np.array(target_position)
                    )
                    ro_i_list.append(ro_i)
                min_ro_i = min(ro_i_list)
                max_ro_i = max(ro_i_list)

                # 取得した座標を使って計算
                if min_ro_i > 10:
                    # 距離が閾値より大きい場合は巡回
                    self.patroll.animate(agent_positions)
                    self.circle_formation_started = False  # 巡回に戻ったらリセット
                    self.formation_switch_counter = 0  # カウンターもリセット
                elif min_ro_i <= 10 and not self.circle_formation_started:
                    # 距離が閾値以下で、円形フォーメーションがまだ始まっていない場合は直線
                    Params["R"] = 4
                    Params["d_i"] = [
                        np.pi / 4,
                        np.pi / 4,
                        np.pi / 4,
                        np.pi / 4,
                        np.pi / 4,
                        3 * np.pi / 4,
                    ]  # 6台の場合
                    Params["Omega"] = 0
                    self.ani.animate(i, target_position, agent_positions)
                    # 条件が満たされた場合、カウンターを増やす
                    if max_ro_i <= 4.1 and alpha_i[5] <= 3 * np.pi / 4:
                        self.formation_switch_counter += 1
                        print(
                            f"円形フォーメーション切り替え条件カウント: {self.formation_switch_counter}/20"
                        )
                    else:
                        self.formation_switch_counter = (
                            0  # 条件が満たされなければリセット
                        )

                    # 20ステップ連続で条件が満たされたら切り替え
                    if self.formation_switch_counter >= 20:
                        self.circle_formation_started = True
                        # 円形フォーメーション切り替え時にソートをリセット
                        self.ani.mapping_initialized = False
                        print("円形フォーメーションに切り替えます")
                else:
                    Params["R"] = 3
                    Params["d_i"] = [
                        np.pi / 3,
                        np.pi / 3,
                        np.pi / 3,
                        np.pi / 3,
                        np.pi / 3,
                        np.pi / 3,
                    ]  # 6台の場合
                    Params["Omega"] = 0.2
                    # それ以外は円形フォーメーション
                    self.ani.animate(i, target_position, agent_positions)
                # シミュレーションを1ステップ進める
                self.sim.step_simulation()

                # フレームカウンターとシミュレーション時間を更新
                i += 1
                current_sim_time = self.sim.sim.getSimulationTime()

        except KeyboardInterrupt:
            print("\nctrl+Cでシミュレーションが終了しました")
        except Exception as e:
            print(f"\nエラーが発生しました: {type(e).__name__}: {e}")
            print("シミュレーションを停止します...")
        finally:
            print(f"\n同期モードでのシミュレーションが終了しました。")
            print(f"最終シミュレーション時間: {self.sim.sim.getSimulationTime():.2f}秒")
            print("CoppeliaSim を停止中...")
            self.sim.stop_simulation()
            print("シミュレーション終了")

            # CSV保存が有効な場合、プロット機能を実行
            if Params["save_csv"]:
                print("\nCSVデータをプロット中...")
                from animation import Japan_time

                plot_csv_data(Japan_time)
                print("プロット完了")

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
