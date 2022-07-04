from z3 import *
from utils import *
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

        x = [Int(f'x_{n}') for n in range(n_blocks)]
        y = [Int(f'y_{n}') for n in range(n_blocks)]
        self.x, self.y = x, y

        assertions = []

        x_bounds = [And(0 <= x[n], x[n] <= w - m[n][0]) for n in range(n_blocks)]
        assertions.append(x_bounds)

        h = Int('h')
        self.h = h
        y_bounds = [And(0 <= y[n], y[n] - h <= -m[n][1]) for n in range(n_blocks)]
        h_bounds = And(min_h <= h, h <= max_h)
        assertions.append(y_bounds)
        assertions.append([h_bounds])

        no_overlap = [
                    And([Or(
                        x[i] - x[j] <= -m[i][0], 
                        y[i] - y[j] <= -m[i][1],
                        x[j] - x[i] <= -m[j][0],
                        y[j] - y[i] <= -m[j][1]) 
                        for j in range(i+1, n_blocks)
                    ]) for i in range(n_blocks)
                ]
        assertions.append(no_overlap)
        
        return assertions

    def get_height_constraints(self, bound):
        return [self.h <= bound]