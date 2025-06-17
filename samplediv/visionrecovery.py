import tkinter as tk
import random
import math

# ランドルト環の向き（上、右、下、左）
DIRECTIONS = ['up', 'right', 'down', 'left']
DIRECTION_SYMBOLS = {'up': '↑', 'right': '→', 'down': '↓', 'left': '←'}
DIRECTION_ANGLE = {'up': 90, 'right': 0, 'down': 270, 'left': 180}

class TargetGame:
    def __init__(self, master):
        self.master = master
        self.master.title('視力検査射的ゲーム')
        self.canvas = tk.Canvas(master, width=600, height=400, bg='white')
        self.canvas.pack()
        self.score = 0
        self.targets = []  # 各的のz, dir, x, y
        self.target_zmax = 200  # 一番奥
        self.target_zmin = 40   # 一番手前
        self.target_base_x = [120, 300, 480]
        self.target_base_y = 200
        self.create_targets()
        self.create_ui()
        self.animating = True
        self.animate()

    def create_targets(self):
        self.targets = []
        for i in range(3):
            z = self.target_zmax - i * 50  # 奥行きにばらつき
            direction = random.choice(DIRECTIONS)
            self.targets.append({'z': z, 'dir': direction})

    def draw_targets(self):
        self.canvas.delete('all')
        for i, t in enumerate(self.targets):
            scale = 1 + (self.target_zmax - t['z']) / (self.target_zmax - self.target_zmin)
            r = 30 * scale
            x = self.target_base_x[i]
            y = self.target_base_y
            self.draw_landolt_c(x, y, r, t['dir'])
            self.canvas.create_text(x, y + r + 20, text=f'的{i+1}', font=('Arial', 14))

    def draw_landolt_c(self, x, y, r, direction):
        # 円弧でランドルト環を描画（切れ目は120度）
        angle = DIRECTION_ANGLE[direction]
        start = angle - 60
        extent = 300
        self.canvas.create_oval(x - r, y - r, x + r, y + r, width=4)
        self.canvas.create_arc(x - r, y - r, x + r, y + r, start=start, extent=extent, style=tk.ARC, width=int(r/4))

    def create_ui(self):
        self.info_label = tk.Label(self.master, text='的と向きを選んでください', font=('Arial', 14))
        self.info_label.pack()
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack()
        self.target_var = tk.IntVar(value=0)
        for i in range(3):
            tk.Radiobutton(self.button_frame, text=f'的{i+1}', variable=self.target_var, value=i).pack(side=tk.LEFT)
        self.dir_var = tk.StringVar(value=DIRECTIONS[0])
        for d in DIRECTIONS:
            tk.Radiobutton(self.button_frame, text=DIRECTION_SYMBOLS[d], variable=self.dir_var, value=d).pack(side=tk.LEFT)
        self.answer_btn = tk.Button(self.master, text='答える', command=self.check_answer)
        self.answer_btn.pack()
        self.score_label = tk.Label(self.master, text='スコア: 0', font=('Arial', 14))
        self.score_label.pack()

    def animate(self):
        if not self.animating:
            return
        for t in self.targets:
            t['z'] -= 2  # 手前に近づく
            if t['z'] < self.target_zmin:
                t['z'] = self.target_zmin
        self.draw_targets()
        self.master.after(30, self.animate)

    def check_answer(self):
        idx = self.target_var.get()
        direction = self.dir_var.get()
        t = self.targets[idx]
        if t['dir'] == direction and t['z'] <= self.target_zmin + 10:
            self.score += 1
            self.info_label.config(text='正解！')
            # 的を一番奥に戻し、向きも新しく
            t['z'] = self.target_zmax
            t['dir'] = random.choice(DIRECTIONS)
        else:
            self.info_label.config(text=f'不正解... 正解は{DIRECTION_SYMBOLS[t['dir']]}')
        self.score_label.config(text=f'スコア: {self.score}')

if __name__ == '__main__':
    root = tk.Tk()
    game = TargetGame(root)
    root.mainloop()

