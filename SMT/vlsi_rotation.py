from z3 import *
from utils import *
from vlsi import VLSI

class VLSIRotation(VLSI):
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

        rot = [Bool(f'r_{n}') for n in range(n_blocks)]
        x = [Int(f'x_{n}') for n in range(n_blocks)]
        y = [Int(f'y_{n}') for n in range(n_blocks)]
        self.x, self.y, self.rot = x, y, rot

        assertions = []
        rot_fix = [rot[n] for n in range(n_blocks) if m[n][0] == m[n][1]]
        assertions.append(rot_fix)

        x_bounds = [And(0 <= x[n], check_inequality_dx(x, m, rot, n, w)) for n in range(n_blocks)]
        assertions.append(x_bounds)
 
        h = Int('h')
        self.h = h
        h_bounds = And(min_h <= h, h <= max_h)
        y_bounds = [And(0 <= y[n], check_inequality_dy(y, m, rot, n, h)) for n in range(n_blocks)]
        assertions.append(y_bounds)
        assertions.append(h_bounds)

        no_overlap = [
                    And([Or(
                        check_inequality_dx(x, m, rot, i, x[j]),
                        check_inequality_dy(y, m, rot, i, y[j]),
                        check_inequality_dx(x, m, rot, j, x[i]),
                        check_inequality_dy(y, m, rot, j, y[i])
                        ) 
                        for j in range(i+1, n_blocks)
                    ]) for i in range(n_blocks)
                ]
        assertions.append(no_overlap)
        return assertions

    def get_height_constraints(self, bound):
        return [self.h <= bound]
