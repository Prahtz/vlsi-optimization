

import os
import math
from collections import defaultdict
import matplotlib.pyplot as plt

target_id = 13
times = defaultdict(dict)
for dir in sorted(os.listdir('./results/'))[::-1]:
    if 'out_' in dir:
        
        failures = {}
        restarts = {}
        propagations = {}
        good = 0
        solver = dir.split('_')[2]
        for file_name in os.listdir(os.path.join('results', dir)):
            id = int(file_name.split('-')[1].split('.')[0])
            file_path = os.path.join('results', dir, file_name)
            
            with open(file_path, 'r') as f:
                file_lines = f.readlines()
                found = False
                for line in file_lines:
                    to_find = '% Solving time: '
                    i = line.find(to_find)
                    if i != -1:
                        time_sec = float(line[i+len(to_find):].split(' ')[0])
                        if time_sec < 300 and not found:
                            times[dir][id] = time_sec
                            found = True
                            good += 1
        
        avg_time = sum(times[dir].values()) / (good)
        max_time = max(times[dir].values())
        std = math.sqrt(sum([(t - avg_time)**2 for t in times[dir].values()]) / (good))

        print(f'Folder: {dir}, solved: {good}, max solving time: {max_time}, average solving time: {round(avg_time, 4)}')

bins = 39
import seaborn as sns
#fig, ax = plt.subplots()
import pandas as pd

times = pd.DataFrame(data=times)[['out_standard_z3_red', 'out_standard_cvc5_inc', 'out_standard_cvc4_dec']]
times = times.rename(columns={'out_standard_z3_red': 'Z3 Redefine', 'out_standard_cvc5_inc': 'CVC5 Incremental', 'out_standard_cvc4_dec':'CVC4 Decremental'})
times = times.reindex(list(range(times.index.min(), times.index.max()+1)),fill_value=0)
times = times.fillna(0)
times['index'] = times.index
times = pd.melt(times, id_vars='index', var_name="model", value_name="times")
_, ax = plt.subplots()
sns.barplot(data=times, x='index', y='times', hue='model', ax=ax)
ax.set_yscale('log')

plt.show()