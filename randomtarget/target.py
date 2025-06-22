import numpy as np

class Target:
    def __init__(self, init_pos=None):
        if init_pos is None:
            init_pos = np.array([0.0, 0.0])
        self.pos = np.array(init_pos, dtype=float)
        self.velocity = np.zeros(2)

    def random_walk(self, sigma, max_speed, frame_time):
        self.velocity += np.random.normal(0, sigma, size=2)
        speed = np.linalg.norm(self.velocity)
        if speed > max_speed:
            self.velocity = self.velocity / speed * max_speed
        self.pos += self.velocity * frame_time
        return self.pos, self.velocity
