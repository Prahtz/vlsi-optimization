
from z3 import *
import time
from utils import parse_model, write_model, Process

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

    def get_smt2_model(self):
        solver = Solver()
        for a in self.define_model():
            solver.add(a)
        smt2 = '(set-logic QF_IDL)\n(set-option :produce-models true)\n' + solver.to_smt2()
        smt2 = '\n'.join(smt2.split('\n')[:-4])
        return smt2
    
    def solve_smt2(self, strategy, solver_cmd, out_file):
        smt2 = self.get_smt2_model()
        cmd = get_solver_cmd(solver_cmd)
        process = Process(cmd)
        process.write(smt2)
        
        T = 300000
        timeout = T
        model = ''
        result = False
        lb, ub = get_height_bounds(self.m, self.rot, self.w)
        h = lb
        if strategy == 'binary_search':
            height_condition = lambda x: lb <= ub
        elif strategy == 'incremental' or strategy == 'redefine':
            height_condition = lambda x: x <= ub
        elif strategy == 'decremental':
            h = ub
            height_condition = lambda x: lb <= x
        prev = unsat
        while height_condition(h):
            smt2 = ''
            if strategy == 'incremental' or (strategy == 'binary_search' and prev == unsat):
                smt2 += '(push 1)\n'
            if strategy == 'binary_search':
                h = (lb + ub) // 2
            if strategy == 'redefine':
                process.close()
                process = Process(cmd)
                smt2 += self.get_smt2_model()

            smt2 += ''.join(['(assert ' + a.sexpr() + ')\n' for a in self.get_height_constraints(h)])
            smt2 += '(check-sat)\n'
            start = time.time_ns() * 1e-6
            process.write(smt2)
            output = process.readline(timeout)
            end = time.time_ns() * 1e-6
            elapsed = end - start
            timeout -= elapsed
            if output == -1:
                print('Time limit exceeded!')
                return False
            res = output.split('\n')[0]
            if res == 'sat':
                prev = sat
                result = True
                process.writeline('(get-model)')
                model = read_model(process)
                if strategy == 'binary_search':
                    ub = h - 1
                if strategy == 'incremental' or strategy == 'redefine':
                    break
                h -= 1
            else:
                prev = unsat
                if strategy == 'incremental' or strategy == 'binary_search':
                    process.writeline('(pop 1)')
                if strategy == 'binary_search':
                    lb = h + 1
                if strategy == 'decremental':
                    break
                h += 1
        if result:
            model = parse_model(model)
            solving_time = (T - timeout)*1e-3
            write_model(out_file, self.n_blocks, self.w, self.m, model, self.rot, solving_time)
            print(f'Solving time: {solving_time} s')
        return result

    def define_model(self, *args):
        raise NotImplementedError()

def read_model(process):
    out = ''
    while True:
        line = process.readline()
        out += line
        p = count_parenthesis(out)
        if p == 0:
            break
    return out

def get_height_bounds(m, rot, w):
    area_min = sum([m[i][0] * m[i][1] for i in range(len(m))])
    if rot:
        min_h = max(max([min(m[i][1], m[i][0]) for i in range(len(m))]), math.floor(area_min/w))
        max_h = sum([max(m[i][1], m[i][0]) for i in range(len(m))])
    else:
        min_h = max(max([m[i][1] for i in range(len(m))]), math.floor(area_min/w))
        max_h = sum([m[i][1] for i in range(len(m))])
    return min_h, max_h


def get_solver_cmd(solver):
    if solver == 'z3':
        return ['z3', '-in']
    if solver == 'cvc5':
        return ['cvc5', '--produce-models', '--incremental']
    if solver == 'cvc4':
        return ['cvc4', '--produce-models', '--incremental', '--lang', 'smt']
    raise NotImplementedError('Unknown solver')

def count_parenthesis(s):
    cnt = 0
    for c in s:
        if c == '(':
            cnt += 1
        elif c == ')':
            cnt -= 1
    return cnt
        