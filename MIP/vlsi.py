from pulp import *
import time

class VLSI:
    def __init__(self, instance_path, dst_path):
        self.instance_path = instance_path
        self.dst_path = dst_path
        self.rot = False
        self.__load_instance()
    
    def __load_instance(self):
        with open(self.instance_path, 'r') as f:
            self.w = int(f.readline().strip())
            self.n_blocks = int(f.readline().strip())
            self.m = []
            for _ in range(self.n_blocks):
                x, y = [int(c) for c in f.readline().strip().split(' ')]
                self.m.append([x, y])

    def solve(self, solver, out_file):
        model = self.define_model()
        problem = LpProblem('VLSI', LpMinimize)
        for constraint in model:
            problem += constraint
        solver = get_solver(solver)
        timeout = 300
        solver.timeLimit = timeout
        start = time.time_ns() * 1e-9
        problem.solve(solver)
        end = time.time_ns() * 1e-9
        elapsed = end - start           
        result = LpStatus[problem.status]
        if elapsed >= timeout:
            return 'Time Limit Exceeded!'
        if result == 'Optimal':
            print(self.rot)
            self.write_solution(problem, self.w, self.n_blocks, self.rot, self.m, out_file, elapsed)
            
        return result
    
    def write_solution(self, model, w, n_blocks, rot, m, file, solving_time):
        x, y = [0]*n_blocks, [0]*n_blocks
        h = 0

        if rot:
            r = [0]*n_blocks
        for var in model.variables():
            key, val = var.name, round(var.value())
            if '_' in key:
                k, idx = key.split('_')[:2]
                idx = int(idx)
            else:
                k = key
            if k == 'x':
                x[idx] = val
            elif k == 'y':
                y[idx] = val
            elif rot and k == 'r':
                r[idx] = val
            elif k == 'h':
                h = val

        to_write = ''
        to_write += f'{w} {h}\n{n_blocks}\n'
        for n in range(n_blocks):
            m1, m2 = m[n][0], m[n][1]
            if rot:
                m1, m2 = (m2, m1) if r[n] else (m1, m2)
            to_write += f'{m1} {m2} '
            to_write += f'{x[n]} {y[n]}\n'

        to_write += f'Solving time: {solving_time} s'
        with open(file, 'w') as f:
            f.write(to_write)

    def define_model(self):
        raise NotImplementedError()    