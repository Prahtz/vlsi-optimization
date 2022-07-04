from pulp import *
import math
from utils import cumulative_rot

from vlsi import VLSI
class VLSIRotationComplete(VLSI):
    def __init__(self, instance_path, dst_path):
        super().__init__(instance_path, dst_path)
        self.rot = True
    
    def define_model(self):
        m = self.m
        n_blocks = self.n_blocks
        w = self.w
        area_min = sum([m[i][0] * m[i][1] for i in range(n_blocks)])
        min_h = max(max([min(self.m[i][1], self.m[i][0]) for i in range(self.n_blocks)]), math.floor(area_min/self.w))
        max_h = sum([max(self.m[i][1], self.m[i][0]) for i in range(self.n_blocks)])
        
        r = [LpVariable(f'r_{n}', lowBound=0, upBound=1, cat=LpBinary) for n in range(n_blocks)]
        x = [LpVariable(f'x_{n}', lowBound=0, upBound=w - min(m[n][0], m[n][1]), cat=LpInteger) for n in range(n_blocks)]
        y = [LpVariable(f'y_{n}', lowBound=0, upBound=max_h - min(m[n][0], m[n][1]), cat=LpInteger) for n in range(n_blocks)]
        h = LpVariable('h', lowBound=min_h, upBound=max_h, cat=LpInteger)
        h.setInitialValue(min_h)
        obj = [(h, 'minimize h')]
        x_bounds = [x[n] - m[n][0]*r[n] + m[n][1]*r[n] <= -m[n][0] + w for n in range(n_blocks)]
        y_bounds = [y[n] - h - m[n][1]*r[n] + m[n][0]*r[n] <= -m[n][1] for n in range(n_blocks)]

        no_overlap = []
        for i in range(n_blocks):
            for j in range(i+1, n_blocks):
                b = [LpVariable(f'b_{i}_{j}_{k}', lowBound=0, upBound=1, cat=LpBinary) for k in range(4)]
                no_overlap += [-b[0] - b[1] - b[2] - b[3] <= -1]
                
                M1 = max(m[i][0], m[i][1]) + max(x[i].upBound, x[i].lowBound) + max(-x[j].upBound, -x[j].lowBound) + m[i][1]
                M2 = max(m[i][0], m[i][1]) + max(y[i].upBound, y[i].lowBound) + max(-y[j].upBound, -y[j].lowBound) + m[i][0]
                M3 = max(m[j][0], m[j][1]) + max(x[j].upBound, x[j].lowBound) + max(-x[i].upBound, -x[i].lowBound) + m[j][1]
                M4 = max(m[j][0], m[j][1]) + max(y[j].upBound, y[j].lowBound) + max(-y[i].upBound, -y[i].lowBound) + m[j][0]
                no_overlap += [x[i] - x[j] + M1*b[0] - m[i][0]*r[i] + m[i][1]*r[i] <= M1 - m[i][0]]
                no_overlap += [y[i] - y[j] + M2*b[1] - m[i][1]*r[i] + m[i][0]*r[i] <= M2 - m[i][1]]
                no_overlap += [x[j] - x[i] + M3*b[2] - m[j][0]*r[j] + m[j][1]*r[j] <= M3 - m[j][0]]
                no_overlap += [y[j] - y[i] + M4*b[3] - m[j][1]*r[j] + m[j][0]*r[j] <= M4 - m[j][1]]

        cumulative_x = cumulative_rot(x, [m[i][0] for i in range(n_blocks)], [m[i][1] for i in range(n_blocks)], h, r, 'x')
        cumulative_y = cumulative_rot(y, [m[i][1] for i in range(n_blocks)], [m[i][0] for i in range(n_blocks)], w, r, 'y')

        constraints = obj + x_bounds+ y_bounds + no_overlap + cumulative_x + cumulative_y

        return constraints