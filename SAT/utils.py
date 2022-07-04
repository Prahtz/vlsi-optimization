from z3 import *
from itertools import combinations
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

def at_least_one(bool_vars):
    return Or(bool_vars)

def at_most_one_pw(bool_vars):
    return [Not(And(pair[0], pair[1])) for pair in combinations(bool_vars, 2)]

def exactly_one_pw(bool_vars, name = ""):
    return And(at_least_one(bool_vars), And(at_most_one_pw(bool_vars)))

def at_most_one_seq(bool_vars, name):
    constraints = []
    n = len(bool_vars)
    s = [Bool(f"s_{name}_{i}") for i in range(n - 1)]
    constraints.append(Or(Not(bool_vars[0]), s[0]))
    constraints.append(Or(Not(bool_vars[n-1]), Not(s[n-2])))
    for i in range(1, n - 1):
        constraints.append(Or(Not(bool_vars[i]), s[i]))
        constraints.append(Or(Not(bool_vars[i]), Not(s[i-1])))
        constraints.append(Or(Not(s[i-1]), s[i]))
    return And(constraints)

def exactly_one_seq(bool_vars, name):
    return And(at_least_one(bool_vars), at_most_one_seq(bool_vars, name))

def at_most_one_he(bool_vars, name):
    if len(bool_vars) <= 4:
        return And(at_most_one_pw(bool_vars))
    y = Bool(f"y_{name}")
    return And(And(at_most_one_pw(bool_vars[:3] + [y])), And(at_most_one_he(bool_vars[3:] + [Not(y)], name+"_")))

def exactly_one_he(bool_vars, name='he'):
    return And(at_most_one_he(bool_vars, name), at_least_one(bool_vars))

def toBinary(num, length = None):
    num_bin = bin(num).split("b")[-1]
    if length:
        return "0"*(length - len(num_bin)) + num_bin
    return num_bin

def at_most_one_bw(bool_vars, name):
    constraints = []
    n = len(bool_vars)
    m = math.ceil(math.log2(n))
    r = [Bool(f"r_{name}_{i}") for i in range(m)]
    binaries = [toBinary(i, m) for i in range(n)]
    for i in range(n):
        for j in range(m):
            phi = Not(r[j])
            if binaries[i][j] == "1":
                phi = r[j]
            constraints.append(Or(Not(bool_vars[i]), phi))        
    return And(constraints)

def exactly_one_bw(bool_vars, name='bw'):
    return And(at_least_one(bool_vars), at_most_one_bw(bool_vars, name)) 


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
