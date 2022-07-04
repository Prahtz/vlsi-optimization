import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np

def display_results(out_file):   
    with open(out_file, 'r') as f:
        line = '%'
        while '%' in line:
            line = f.readline().strip()
        w, h = [int(c) for c in line.strip().split(' ')]
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