import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import math

import parameter as param
from DataStrage import e_i_1_integral, e_i_2_integral
from Handle import Agent_handles, target_handle, sim
from visionSensor import visionSensor
from coordinate_transform import coordinate_trans, coordinate_target
from calculation import Calculation


class Animation:
    def __init__(self, i):
        self.i = i
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(param.xlim)
        self.ax.set_ylim(param.ylim)
        self.ax.set_aspect("equal")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        self.ax.set_title("Example1")

        # 目標の軌道
        (self.point,) = self.ax.plot([0], [param.radius], "ro", label="Target")

        # --- エージェントの初期角度を第i象限に配置（i=1:第1象限, i=2:第2象限, ...） ---
        self.agent_positions = np.zeros((param.num_agents, 2))
        for i in range(param.num_agents):
            theta = 2 * np.pi * i / param.num_agents
            r = param.radius_limit
            self.agent_positions[i, 0] = param.center[0] + r * np.cos(theta)
            self.agent_positions[i, 1] = param.center[1] + r * np.sin(theta)

        cmap = plt.get_cmap("tab10")
        self.agent_colors = [cmap(i) for i in range(param.num_agents)]
        self.agent_dots = self.ax.scatter(
            self.agent_positions[:, 0],
            self.agent_positions[:, 1],
            c=self.agent_colors,
            label="Agents",
        )
        legend_elements = [
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                label=f"Agent {i+1}",
                markerfacecolor=self.agent_colors[i],
                markersize=10,
            )
            for i in range(param.num_agents)
        ]
        self.ax.legend(
            handles=legend_elements, loc="center left", bbox_to_anchor=(1, 0.5)
        )

        # prev_agent_pos, prev_target_pos などの初期化
        self.prev_agent_pos = self.agent_positions.copy()
        self.prev_target_pos = np.array([param.target_pos[0], param.target_pos[1]])
        self.prev_theta_local = np.zeros(param.num_agents)
        self.prev_theta_plus_local = np.zeros(param.num_agents)
        self.prev_theta_minus_local = np.zeros(param.num_agents)

    def initial_rending(self):
        return self.point, self.agent_dots, self.agent_positions

    def target_position(self):
        # targetのランダムウォーク
        param.target_velocity += np.random.normal(0, param.random_walk_sigma, size=2)
        speed = np.linalg.norm(param.target_velocity)
        if speed > param.max_speed:
            param.target_velocity = param.target_velocity / speed * param.max_speed
        param.target_pos += param.target_velocity * param.frame_time
        x, y = param.target_pos
        self.point.set_data([x], [y])
        return x, y

    def agent_position(self):
        point, agent_dots, agent_positions = self.initial_rending()
        x, y = self.target_position()
        agent_dots.set_offsets(agent_positions)

        if not hasattr(self, "prev_agent_pos"):
            self.prev_agent_pos = agent_positions.copy()
        if not hasattr(self, "prev_target_pos"):
            self.prev_target_pos = np.array([x, y])
        return agent_positions

    def init(self):
        self.point.set_data([param.target_pos[0]], [param.target_pos[1]])
        self.agent_dots.set_offsets(self.agent_positions)
        return self.point, self.agent_dots

    def animate(self, frame):
        x, y = self.target_position()
        for j in range(param.num_agents):
            ro_i = visionSensor(j).visionSensor_min_distance()
            world_pos = np.round(coordinate_target(j, ro_i), 2)
            e_r = (
                world_pos[0] / math.sqrt(world_pos[0] ** 2 + world_pos[1] ** 2),
                world_pos[1] / math.sqrt(world_pos[0] ** 2 + world_pos[1] ** 2),
            )
            e_theta = np.array([-e_r[1], e_r[0]])
            agent_velocity = (
                self.agent_positions[j] - self.prev_agent_pos[j]
            ) / param.frame_time
            relative_velocity = agent_velocity - param.target_velocity
            relative_velocity_local = np.array(
                [np.dot(relative_velocity, e_r), np.dot(relative_velocity, e_theta)]
            )
            idx_plus = (j + 1) % param.num_agents
            idx_minus = (j - 1) % param.num_agents
            vec_plus = self.agent_positions[idx_plus] - self.agent_positions[j]
            vec_minus = self.agent_positions[idx_minus] - self.agent_positions[j]
            theta_plus_local = np.arctan2(
                np.dot(vec_plus, e_theta), np.dot(vec_plus, e_r)
            )
            theta_minus_local = np.arctan2(
                np.dot(vec_minus, e_theta), np.dot(vec_minus, e_r)
            )
            theta_now_local = 0.0
            if not hasattr(self, "prev_theta_local"):
                self.prev_theta_local = np.zeros(param.num_agents)
            omega_i_local = theta_now_local - self.prev_theta_local[j]
            omega_i_local = (omega_i_local + np.pi) % (2 * np.pi) - np.pi
            self.prev_theta_local[j] = theta_now_local
            if not hasattr(self, "prev_theta_plus_local"):
                self.prev_theta_plus_local = np.zeros(param.num_agents)
            if not hasattr(self, "prev_theta_minus_local"):
                self.prev_theta_minus_local = np.zeros(param.num_agents)
            omega_i_plus_local = theta_plus_local - self.prev_theta_plus_local[j]
            omega_i_plus_local = (omega_i_plus_local + np.pi) % (2 * np.pi) - np.pi
            omega_i_minus_local = theta_minus_local - self.prev_theta_minus_local[j]
            omega_i_minus_local = (omega_i_minus_local + np.pi) % (2 * np.pi) - np.pi
            self.prev_theta_plus_local[j] = theta_plus_local
            self.prev_theta_minus_local[j] = theta_minus_local
            alpha_i_local = abs(theta_plus_local - theta_now_local)
            alpha_i_minus_local = abs(theta_minus_local - theta_now_local)
            eta = relative_velocity_local[0]
            eta_norm = abs(eta)
            u = Calculation(
                param.d_i,
                ro_i,
                omega_i_local,
                omega_i_plus_local,
                omega_i_minus_local,
                alpha_i_local,
                alpha_i_minus_local,
                eta_norm,
                e_i_1_integral,
                e_i_2_integral,
                j,
                self.i,
            ).calculate_u()
            theta_global = np.arctan2(e_r[1], e_r[0])
            u_vec = coordinate_trans(theta_global, u)
            visionSensor(j).visionSensor_ViewAngle()
            new_pos = self.agent_positions[j] + u_vec * param.frame_time
            dist_to_target = np.linalg.norm(new_pos - param.target_pos)
            if dist_to_target >= param.R:
                self.agent_positions[j] = new_pos
            else:
                direction = (new_pos - param.target_pos) / np.linalg.norm(
                    new_pos - param.target_pos
                )
                self.agent_positions[j] = param.target_pos + direction * param.R

        self.prev_agent_pos = self.agent_positions.copy()
        self.prev_target_pos = np.array([x, y])

        for j in range(param.num_agents):
            Agents_pos_3d = [
                self.agent_positions[j][0],
                self.agent_positions[j][1],
                2.0,
            ]
            sim.setObjectPosition(Agent_handles[j], -1, Agents_pos_3d)
        target_pos_3d = [param.target_pos[0], param.target_pos[1], 2.0]
        sim.setObjectPosition(target_handle, -1, target_pos_3d)
        self.agent_dots.set_offsets(self.agent_positions)
        self.point.set_data([param.target_pos[0]], [param.target_pos[1]])
        return self.point, self.agent_dots
