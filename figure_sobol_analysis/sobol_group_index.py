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

# Choose which rows and columns you want to “zoom in” on.
# Adjust these to whatever indices suit your data.
row_indices = [9,1,4,2,13,5,8,6,10]   # Example subset of row indices
col_indices_list = [
    [5,6,8,7,9,10,11,14,13,12,15,16,17],   # inhibitory
    [5,6,8,7,9,10,13,12,11,14,15,16]
    ]

for pp in range(len(titles)):
    sobol_table_per_pp = []
    last_val = None   # We'll keep track of the last 'val' to retrieve names for ticks
    last_unq_feature = None

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

            # Keep references so we know what to label later
            last_val = val
            last_unq_feature = unq_feature

            sobol_table_per_cell = [[]]
            for kk in range(len(unq_feature)):
                ind_temp = np.where(ia == kk)[0]
                sobol_table_per_feature = []
                
                for ll in ind_temp:
                    # Use S1 index
                    sobol_table_per_feature.append(val[list(val.keys())[ll]][1]['S1'])
                    
                    # Check for name mismatch
                    if val[list(val.keys())[ll]][1]['names'] \
                       != val[list(val.keys())[0]][1]['names']:
                        raise ValueError("Mismatch in 'names' across rows.")
                
                # Average the feature table if more than one row
                if len(sobol_table_per_feature) > 1:
                    sobol_table_per_feature = np.mean(sobol_table_per_feature, axis=0)

                sobol_table_per_feature = np.array(sobol_table_per_feature)
                if sobol_table_per_cell == [[]]:
                    sobol_table_per_cell = sobol_table_per_feature.reshape(1, -1)
                else:
                    sobol_table_per_cell = np.concatenate(
                        (sobol_table_per_cell, 
                         sobol_table_per_feature.reshape(1, -1)), 
                        axis=0
                    )
            
            sobol_table_per_cell = np.array(sobol_table_per_cell)
            sobol_table_per_celltype.append(sobol_table_per_cell)
        
        # Average over all files for this particular cell type
        sobol_table_per_celltype = np.mean(
            np.stack(sobol_table_per_celltype, axis=2), 
            axis=2
        )
        sobol_table_per_pp.append(sobol_table_per_celltype)

    # Average over all cell types (the entire prefix group)
    sobol_table_per_pp = np.mean(
        np.stack(sobol_table_per_pp, axis=2), 
        axis=2
    )

    # “Zoom in” on row_indices and col_indices
    col_indices = col_indices_list[pp]
    sobol_table_subset = sobol_table_per_pp[np.ix_(row_indices, col_indices)]

    # Plot the subset
    plt.figure()
    plt.imshow(np.log(sobol_table_subset), vmin=-5.5, vmax=-0.5, aspect='auto')
    plt.title(titles[pp], fontsize=22)

    # Define the ticks to match the subset
    # Ensure last_val and last_unq_feature were set
    if last_val is not None and last_unq_feature is not None:
        # X-axis: parameter names
        param_names = last_val[list(last_val.keys())[0]][1]['names']
        plt.xticks(
            range(len(col_indices)), 
            [param_names[c].replace('basal', 'dendrite').replace('somatic', 'soma') for c in col_indices],
            rotation=90
        )
        # Y-axis: feature names
        plt.yticks(
            range(len(row_indices)), 
            [last_unq_feature[r] for r in row_indices]
        )
    
    # Adjust tick label sizes
    plt.gca().tick_params(axis='x', labelsize=14)
    plt.gca().tick_params(axis='y', labelsize=14)

    # Save figure
    plt.savefig(f"{titles[pp]}_summary_plot_zoomed.png", 
                format="png", dpi=300, bbox_inches="tight")
    plt.close()
