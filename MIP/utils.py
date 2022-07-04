import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from pulp import *

def cumulative(s, d, r, b, name):
    early = 0
    late = max([s[i].upBound + d[i] for i in range(len(s))]) + 1
    constraints = []
    for t in range(early, late):
        sum_vars = 0
        for i in range(len(s)):
            t1 = LpVariable(f't1_{t}_{i}_{name}', 0, 1, LpBinary)
            t2 = LpVariable(f't2_{t}_{i}_{name}', 0, 1, LpBinary)
            t3 = LpVariable(f't3_{t}_{i}_{name}', 0, 1, LpBinary)
            constraints += leq_encoding(s[i], t, t1)
            constraints += geq_encoding(s[i], t + 1 - d[i], t2)
            constraints += and_encoding(t1, t2, t3)
            sum_vars += r[i]*t3
        constraints += [b >= sum_vars]
    return constraints

def cumulative_rot(s, d, r, b, rot, name):
    early = 0
    late = max([s[i].upBound + d[i] for i in range(len(s))]) + 1
    constraints = []
    for t in range(early, late):
        sum_vars = 0
        for i in range(len(s)):
            t1 = LpVariable(f't1_{t}_{i}_{name}', 0, 1, LpBinary)
            t2 = LpVariable(f't2_{t}_{i}_{name}', 0, 1, LpBinary)
            t3 = LpVariable(f't3_{t}_{i}_{name}', 0, 1, LpBinary)
            t4 = LpVariable(f't4_{t}_{i}_{name}', 0, 1, LpBinary)

            constraints += leq_encoding(s[i], t, t1)
            constraints += geq_encoding_rot(s[i], t, d[i], r[i], rot[i], t2)
            constraints += and_encoding(t1, t2, t3)
            constraints += and_encoding(t3, rot[i], t4)
            sum_vars += r[i]*t3 - r[i]*t4 + d[i]*t4
        constraints += [b >= sum_vars]
    return constraints

def leq_encoding(x, t, b):
    constraints = []
    M1 = -t + max(x.upBound, x.lowBound)
    M2 = t+1 + max(-x.upBound, -x.lowBound)
    constraints += [x <= t + M1*(1-b)] #x + M1*b <= t + M1
    constraints += [-x <= -t-1 + M2*b] #-x -M2*b <= -t-1
    return constraints

def geq_encoding_rot(x, t, d, r, rot, b):
    constraints = []
    M1 = -t +d + max(x.upBound, x.lowBound) + r
    M2 = t+1 + max(-x.upBound, -x.lowBound) 
    constraints += [x <= t - ((1-rot)*d + rot*r) + M1*b] # t - d  + d*rot - r*rot
    constraints += [-x <= -t-1 + (1-rot)*d + rot*r + M2*(1-b)] #-t-1 + d -d*rot + r*rot
    return constraints

def geq_encoding(x, t, b):
    return leq_encoding(x, t-1, 1-b)

def and_encoding(p, q, b):
    constraints = []
    constraints += [2 - (p + q) >= (1 - b)]
    constraints += [b <= p]
    constraints += [b <= q]
    return constraints



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