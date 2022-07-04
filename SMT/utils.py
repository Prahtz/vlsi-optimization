from tracemalloc import stop
from z3 import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import re
import subprocess, threading

def check_inequality_dx(a, m, rot, i, n):
    return And(Or(rot[i], a[i] - n <= -m[i][0]), Or(Not(rot[i]), a[i] - n <= -m[i][1]))

def check_inequality_dy(a, m, rot, i, n):
    return And(Or(rot[i], a[i] - n <= -m[i][1]), Or(Not(rot[i]), a[i] - n <= -m[i][0]))

def display_results(out_file):   
    with open(out_file, 'r') as f:
        w, h = [int(c) for c in f.readline().strip().split(' ')]
        n = int(f.readline().strip())
        m, p = [], []
        for i in range(n):
            line = [int(c) for c in f.readline().strip().split(' ')]
            dim, pos = line[:2], line[2:]
            m.append(dim)
            p.append(pos)
    grid = np.zeros((h, w), dtype=int)
    for i in range(n):
        grid[h - p[i][1] - m[i][1]: h - p[i][1], p[i][0]: p[i][0] + m[i][0]] = i+1
    
    # create discrete colormap
    cmap = plt.cm.get_cmap('hsv', n+2)
    cmap = cmap(range(n+2))
    cmap[0] = np.array([0, 0, 0, 1])
    cmap = ListedColormap(cmap)

    _, ax = plt.subplots()
    ax.imshow(grid, cmap=cmap, vmin=0, vmax=n+1)

    # draw gridlines
    ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=2)
    ax.set_xticks(np.arange(-.5, w, 1), labels=list(range(w+1)));
    ax.set_yticks(np.arange(-.5, h, 1), labels=list(range(h, -1, -1)));

    plt.show()

def parse_model(model):
    model = ' '.join(model.split('\n'))
    model = model[1:-1].strip()
    f = model.find('model')
    if f >= 0:
        model = model[:f] + model[f+5:]
    model = re.sub('\s+',' ', model)
    model = re.sub('(\) \()', ')-(', model).strip()
    model = re.sub('[\(\)]|( \(\))|(define-fun )', '', model).strip()
    
    model = model.split('-')
    result = {}
    for element in model:
        element = element.split(' ')
        key = element[0]
        val = int(element[2]) if element[1] == 'Int' else (True if element[2] == 'true' else False)
        result[key] = val
    return result

def write_model(file, n_blocks, w, m, model, rot, solving_time):
    x, y = [0]*n_blocks, [0]*n_blocks
    h = 0
    if rot:
        r = [False]*n_blocks
    for key in model.keys():
        if '_' in key:
            v, idx = key.split('_')
        else:
            v = key
        idx = int(idx)
        if v == 'x':
            x[idx] = model[key]
        elif v == 'y':
            y[idx] = model[key]
        elif rot and v == 'r':
            r[idx] = model[key]
        elif v == 'h':
            h = model[key]
        else:
            raise RuntimeError('Unexpected key')

    to_write = ''
    to_write += f'{w} {h}\n{n_blocks}\n'
    for n in range(n_blocks):
        m1, m2 = m[n][0], m[n][1]
        if rot:
            m1, m2 = (m2, m1) if r[n] else (m1, m2)
        to_write += f'{m1} {m2} '
        to_write += f'{x[n]} {y[n]}\n'

    to_write += f'% Solving time: {solving_time} s'
    with open(file, 'w') as f:
        f.write(to_write)

class Process:
    def __init__(self, cmd):
        self.process = self.process = subprocess.Popen(cmd,
                            bufsize=1,
                            stdin = subprocess.PIPE,
                            stdout = subprocess.PIPE,
                            universal_newlines=True,)
        self.rd = self.process.stdout
        self.wr = self.process.stdin

    def readline(self, timeout=None):
        if timeout:
            timeout = timeout * 1e-3
        def target():
            self.line = self.rd.readline()
            
        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()
            return -1
        return self.line

    def writeline(self, line):
        self.wr.write(line + '\n')

    def write(self, string):
        self.wr.write(string)

    def close(self):
        self.process.communicate('(exit)')