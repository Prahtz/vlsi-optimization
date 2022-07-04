from z3 import sat
import time
import math
import os

class VLSI:
    def __init__(self, instance_path, dst_path):
        self.instance_path = instance_path
        self.dst_path = dst_path
        self.rot = None
        self.__load_instance()

    def __load_instance(self):
        with open(self.instance_path, 'r') as f:
            self.w = int(f.readline().strip())
            self.n_blocks = int(f.readline().strip())
            self.m = []
            for _ in range(self.n_blocks):
                x, y = [int(c) for c in f.readline().strip().split(' ')]
                self.m.append([x, y])

    def __write_to_file(self, model, max_h, solving_time):
        to_write = ''
        h = 0
        for n in range(self.n_blocks):
            r = 0
            if self.rot:
                r = 1 if model.evaluate(self.rot[n]) else 0
            for j in range(max_h):
                if model.evaluate(self.y[n][j]):
                    h = max(h, j + (1-r)*self.m[n][1] + r*self.m[n][0])
        to_write += f'{self.w} {h}\n{self.n_blocks}\n'
        for n in range(self.n_blocks):
            m1, m2 = self.m[n][0], self.m[n][1]
            if self.rot:
                m1, m2 = (m2, m1) if model.evaluate(self.rot[n]) else (m1, m2)
            to_write += f'{m1} {m2} '
            for i in range(self.w):
                if model.evaluate(self.x[n][i]):
                    x = i
                    break
            for i in range(max_h):
                if model.evaluate(self.y[n][i]):
                    y = i
                    break
            to_write += f'{x} {y}\n'
        
        to_write += f'% Solving time: {solving_time} s'
        out_file = os.path.join(self.dst_path, 'out-' + self.instance_path.split('/')[-1].split('-')[-1])
        with open(out_file, 'w') as f:
            f.write(to_write)

    def solve(self):
        area_min = sum([self.m[i][0] * self.m[i][1] for i in range(self.n_blocks)])
        if self.rot:
            min_h = max(max([min(self.m[i][1], self.m[i][0]) for i in range(self.n_blocks)]), math.floor(area_min/self.w))
            max_h = sum([max(self.m[i][1], self.m[i][0]) for i in range(self.n_blocks)])
        else:
            min_h = max(max([self.m[i][1] for i in range(self.n_blocks)]), math.floor(area_min/self.w))
            max_h = sum([self.m[i][1] for i in range(self.n_blocks)])

        T = 300000
        timeout = T
        for objective_h in range(min_h, max_h):
            print(f'Solving for h={objective_h}')
            solver = self.define_model(objective_h)
            solver.set('timeout', timeout)
            start = time.time_ns()*1e-6
            res = solver.check()
            end = time.time_ns()*1e-6
            timeout -= end - start
            if timeout <= 0:
                print('Time limit exceeded!')
                break
            if res == sat:
                model = solver.model()
                solving_time = (T - timeout)*1e-3
                self.__write_to_file(model, objective_h, solving_time)
                print(f'Solving time: {solving_time} s')
                return True
        return False
    
    def define_model(self, max_h):
        raise NotImplementedError()