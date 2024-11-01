import os
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

# File directory
folder_name = './trace_data/'

# List all files in the folder that match the pattern
json_list = [f for f in os.listdir(folder_name) if f.startswith('full') and f.endswith('.json')]

# Set parameters
cell_index = 20
plot_window = [800, 2200]

# Load the JSON file
fname = os.path.join(folder_name, json_list[cell_index])
with open(fname, 'r') as f:
    val = json.load(f)

# Process scores and find best scores
scores = []
new_best_score = float('inf')
new_best_score_index = []

for ii, entry in enumerate(val):
    mean_score = entry['mean_score']
    scores.append(mean_score)
    
    if mean_score < new_best_score:
        new_best_score = mean_score
        new_best_score_index.append(ii)

# Get trace names
trace_names = list(val[0]['trace'].keys())
ro = len(trace_names)
co = len(new_best_score_index)

# Plot scores
plt.figure()
plt.subplot(2, co, (2, co-1))
plt.plot(range(len(val)), scores)
plt.scatter(new_best_score_index, [scores[i] for i in new_best_score_index], color='r', marker='+')
plt.xlabel('Index')
plt.ylabel('Mean Score')

# Setup colormap
numTiers = 10
cmap = cm.get_cmap('viridis', numTiers)(np.linspace(0, 1, numTiers)) * 0.75

# Extract cell name
cell_name = fname.split('data_')[-1].split('.')[0]

# Plot traces for best scores
plt.suptitle(cell_name.replace('_', ' '))
for ii, idx in enumerate(new_best_score_index):
    plt.subplot(2, co, ii + co + 1)
    plt.xlim(plot_window)
    plt.ylim([-110, 40])
    plt.axis('off')
    
    for jj in range(ro):
        time_temp = val[idx]['trace'][trace_names[jj]]['time']
        voltage_temp = val[idx]['trace'][trace_names[jj]]['voltage']
        plt.plot(time_temp, voltage_temp, color=cmap[jj])
    
    plt.title(str(idx), y=-0.1)

output_filename = f'{cell_name}_plot.png'
plt.savefig(output_filename, format='png', dpi=300)
plt.close()

print(f'Plot saved as {output_filename}')
