

import os
import math
from collections import defaultdict
import matplotlib.pyplot as plt

target_id = 13
times = defaultdict(dict)
for dir in sorted(os.listdir('./results/')):
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
                    to_find = '% time elapsed: '
                    i = line.find(to_find)
                    if i != -1:
                        time_sec = float(line[i+len(to_find):].split(' ')[0])
                        if time_sec < 300 and not found:
                            times[dir][id] = time_sec
                            found = True
                            good += 1

                    to_find = '%%%mzn-stat: failures='
                    i = line.find(to_find)
                    if i != -1:
                        failures[id] = int(line[i+len(to_find):])
                    
                    to_find = '%%%mzn-stat: restarts='
                    i = line.find(to_find)
                    if i != -1:
                        restarts[id] = int(line[i+len(to_find):])

                    to_find = '%%%mzn-stat: propagations='
                    i = line.find(to_find)
                    if i != -1:
                        propagations[id] = int(line[i+len(to_find):])
        
        avg_time = sum(times[dir].values()) / (good)
        max_time = max(times[dir].values())
        std = math.sqrt(sum([(t - avg_time)**2 for t in times[dir].values()]) / (good))

        print(f'Folder: {dir}, solved: {good}, max solving time: {max_time}, average solving time: {round(avg_time, 4)}')
        assert target_id in restarts.keys(), 'No target id'
        print(f'Folder: {dir}, failures: {failures[target_id]}, restarts: {restarts[target_id]}, propagations: {propagations[target_id]}\n')
    

bins = 39
import seaborn as sns
#fig, ax = plt.subplots()
import pandas as pd

times = pd.DataFrame(data=times)[['out_final_c_io_F', 'out_complete_c_io_F', 'out_rotation_c_io_F']]
times = times.rename(columns={'out_final_c_io_F': 'Final', 'out_complete_c_io_F': 'Complete', 'out_rotation_c_io_F':'Rotation'})
times = times.reindex(list(range(times.index.min(), times.index.max()+1)),fill_value=0)
times = times.fillna(0)
times['index'] = times.index
times = pd.melt(times, id_vars='index', var_name="model", value_name="times")
_, ax = plt.subplots()
sns.barplot(data=times, x='index', y='times', hue='model', ax=ax)
ax.set_yscale('log')

plt.show()