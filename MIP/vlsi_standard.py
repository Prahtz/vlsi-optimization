from pulp import *
import math
from vlsi import VLSI
class VLSIStandard(VLSI):
    def __init__(self, instance_path, dst_path):
        super().__init__(instance_path, dst_path)
    
    def define_model(self):
        m = self.m
        n_blocks = self.n_blocks
        w = self.w
        
        area_min = sum([m[i][0] * m[i][1] for i in range(n_blocks)])
        min_h = max(max([m[i][1] for i in range(n_blocks)]), math.floor(area_min/self.w))
        max_h = sum([m[i][1] for i in range(n_blocks)])
        
        x = [LpVariable(f'x_{n}', lowBound=0, upBound=w - m[n][0], cat=LpInteger) for n in range(n_blocks)]
        y = [LpVariable(f'y_{n}', lowBound=0, upBound=max_h - m[n][1], cat=LpInteger) for n in range(n_blocks)]
        h = LpVariable('h', lowBound=min_h, upBound=max_h, cat=LpInteger)
        h.setInitialValue(min_h)
        obj = [(h, 'minimize h')]
        y_bounds = [y[n] - h <= -m[n][1] for n in range(n_blocks)]
        no_overlap = []
        for i in range(n_blocks):
            for j in range(i+1, n_blocks):
                b = [LpVariable(f'b_{i}_{j}_{k}', lowBound=0, upBound=1, cat=LpBinary) for k in range(4)]
                M1 = m[i][0] + max(x[i].upBound, x[i].lowBound) + max(-x[j].upBound, -x[j].lowBound)
                M2 = m[i][1] + max(y[i].upBound, y[i].lowBound) + max(-y[j].upBound, -y[j].lowBound)
                M3 = m[j][0] + max(x[j].upBound, x[j].lowBound) + max(-x[i].upBound, -x[i].lowBound)
                M4 = m[j][1] + max(y[j].upBound, y[j].lowBound) + max(-y[i].upBound, -y[i].lowBound)
                no_overlap += [-b[0] - b[1] - b[2] - b[3] <= -1]
                no_overlap += [x[i] - x[j] + M1*b[0] <= M1 - m[i][0]] 
                no_overlap += [y[i] - y[j] + M2*b[1] <= M2 - m[i][1]] 
                no_overlap += [x[j] - x[i] + M3*b[2] <= M3 - m[j][0]]
                no_overlap += [y[j] - y[i] + M4*b[3] <= M4 - m[j][1]]

        constraints = obj + y_bounds + no_overlap 

        return constraints