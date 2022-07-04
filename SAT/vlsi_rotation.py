from z3 import *
from utils import *
from vlsi import VLSI

class VLSIRotation(VLSI):
    def __init__(self, instance_path, dst_path, encoding):
        super().__init__(instance_path, dst_path)
        self.encoding = encoding

    def define_model(self, h):
        x = [[Bool(f'x_{n}_{k}') for k in range(self.w)] for n in range(self.n_blocks)]
        y = [[Bool(f'y_{n}_{k}') for k in range(h)] for n in range(self.n_blocks)]
        rot = [Bool(f'rot_{n}') for n in range(self.n_blocks)]

        if self.encoding == 'pairwise':
            exactly_one = exactly_one_pw
        elif self.encoding == 'sequential':
            exactly_one = exactly_one_seq
        elif self.encoding == 'heule':
            exactly_one = exactly_one_he
        elif self.encoding == 'bitwise':
            exactly_one = exactly_one_bw
        else:
            raise RuntimeError('Unknown sat encoding name')
            
        exactly_one_x = And([exactly_one([x[n][i] for i in range(self.w)], f'x_{n}') for n in range(self.n_blocks)])
        exactly_one_y = And([exactly_one([y[n][i] for i in range(h)], f'y_{n}') for n in range(self.n_blocks)])
               
        no_over_w = And([And(
                            Implies(Not(rot[n]), And([Not(x[n][i]) for i in range(self.w - self.m[n][0]+1, self.w)])), 
                            Implies(rot[n], And([Not(x[n][i]) for i in range(self.w - self.m[n][1]+1, self.w)]))
                            ) for n in range(self.n_blocks)])
        no_over_h = And([And(
                Implies(Not(rot[n]), And([Not(y[n][i]) for i in range(h - self.m[n][1]+1, h)])),
                Implies(rot[n], And([Not(y[n][i]) for i in range(h - self.m[n][0]+1, h)]))
            ) for n in range(self.n_blocks)])
        no_overlap = []
        for i in range(self.n_blocks):
            for j in range(i+1, self.n_blocks):
                overlap = []
                overlap.append(And(
                    [*[Implies(And(x[i][k1], Not(rot[i])), Or([x[j][k2] for k2 in range(k1 + self.m[i][0], self.w)])) for k1 in range(self.w - self.m[i][0] + 1)],
                    *[Implies(And(x[i][k1], rot[i]), Or([x[j][k2] for k2 in range(k1 + self.m[i][1], self.w)])) for k1 in range(self.w - self.m[i][1] + 1)]]
                ))
                overlap.append(And(
                    [*[Implies(And(x[j][k1], Not(rot[j])), Or([x[i][k2] for k2 in range(k1 + self.m[j][0], self.w)])) for k1 in range(self.w - self.m[j][0] + 1)],
                    *[Implies(And(x[j][k1], rot[j]), Or([x[i][k2] for k2 in range(k1 + self.m[j][1], self.w)])) for k1 in range(self.w - self.m[j][1] + 1)]]
                ))
                overlap.append(And(
                    [*[Implies(And(y[i][k1], Not(rot[i])), Or([y[j][k2] for k2 in range(k1 + self.m[i][1], h)])) for k1 in range(h - self.m[i][1] + 1)],
                    *[Implies(And(y[i][k1], rot[i]), Or([y[j][k2] for k2 in range(k1 + self.m[i][0], h)])) for k1 in range(h - self.m[i][0] + 1)]]
                ))
                overlap.append(And(
                    [*[Implies(And(y[j][k1], Not(rot[j])), Or([y[i][k2] for k2 in range(k1 + self.m[j][1], h)])) for k1 in range(h - self.m[j][1] + 1)],
                    *[Implies(And(y[j][k1], rot[j]), Or([y[i][k2] for k2 in range(k1 + self.m[j][0], h)])) for k1 in range(h - self.m[j][0] + 1)]]
                ))
                overlap = Or(overlap)
                no_overlap.append(overlap)  
        no_overlap = And(no_overlap)      
        self.x = x
        self.y = y
        self.rot = rot
        
        solver = Solver()
        solver.add(exactly_one_x)
        solver.add(exactly_one_y)
        solver.add(no_over_w)
        solver.add(no_over_h)
        solver.add(no_overlap)
        return solver