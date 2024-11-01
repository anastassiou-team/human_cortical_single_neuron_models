import os
import json
import numpy as np
import matplotlib.pyplot as plt

prefix = [
    [
        'ITL23__',
        'ITL35__',
        'ITL46__'
    ],
    [
        'PVALB__',
        'SST__',
        'VIP__',
        'LAMP5PAX6Other__'
    ]
]

titles = [
    'Excititory',
    'Inhibitory'
]


folder_namee = 'sensitivity_json/'


for pp in range(len(titles)):
    sobol_table_per_pp = []
    for ii in range(len(prefix[pp])):
        # Get list of files that match the prefix pattern
        file_list = [f for f in os.listdir(folder_namee) if f.startswith(prefix[pp][ii])]

        sobol_table_per_celltype = []
        for jj, file_name in enumerate(file_list):
            fname = os.path.join(folder_namee, file_name)
            with open(fname, 'r') as f:
                val = json.load(f)
            
            # Extract feature names and clean them
            f_name = list(val.keys())
            f_name = [name.split('.soma.')[1] for name in f_name]
            
            # Find unique features and their indices
            unq_feature, ia = np.unique(f_name, return_inverse=True)

            sobol_table_per_cell = [[]]
            for kk in range(len(unq_feature)):
                ind_temp = np.where(ia == kk)[0]
                sobol_table_per_feature = []
                
                for ll in ind_temp:
                    # Use S1 index
                    sobol_table_per_feature.append(val[list(val.keys())[ll]][1]['S1'])
                    
                    # Check for name mismatch
                    if val[list(val.keys())[ll]][1]['names'] != val[list(val.keys())[0]][1]['names']:
                        raise ValueError("mismatch in names")
                
                # Average the feature table if more than one row
                if len(sobol_table_per_feature) > 1:
                    sobol_table_per_feature = np.mean(sobol_table_per_feature, axis=0)
                sobol_table_per_feature = np.array(sobol_table_per_feature)
                # sobol_table_per_cell.append(sobol_table_per_feature)
                if sobol_table_per_cell == [[]]:
                    sobol_table_per_cell = sobol_table_per_feature.reshape(1, -1)
                else:
                    sobol_table_per_cell = np.concatenate((sobol_table_per_cell,sobol_table_per_feature.reshape(1, -1)),axis=0)
            
            sobol_table_per_cell = np.array(sobol_table_per_cell)
            sobol_table_per_celltype.append(sobol_table_per_cell)
        
        sobol_table_per_celltype = np.mean(np.stack(sobol_table_per_celltype, axis=2), axis=2)
        sobol_table_per_pp.append(sobol_table_per_celltype)

    sobol_table_per_pp = np.mean(np.stack(sobol_table_per_pp, axis=2), axis=2)
        
    plt.figure()
    plt.imshow(np.log(sobol_table_per_celltype), vmin=-5.5, vmax=-0.5, aspect='auto')
    plt.title(titles[pp])
    
    # Set x and y ticks
    xticks = range(len(val[list(val.keys())[0]][1]['names']))
    plt.xticks(xticks, val[list(val.keys())[0]][1]['names'], rotation=90)
    yticks = range(len(unq_feature))
    plt.yticks(yticks, unq_feature)
    plt.gca().tick_params(axis='x', labelsize=10)
    plt.gca().tick_params(axis='y', labelsize=10)
    
    # plt.show()
    plt.savefig(f"{titles[pp]}_summary_plot.png", format="png", dpi=300, bbox_inches="tight")
