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
row_indices = [0, 2, 4]   # Example subset of row indices
col_indices = [1, 3, 5]   # Example subset of column indices

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
                    sobol_table_per_feature.append(
                        val[list(val.keys())[ll]][1]['S1']
                    )
                    
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
                        (
                            sobol_table_per_cell, 
                            sobol_table_per_feature.reshape(1, -1)
                        ), 
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
    sobol_table_subset = sobol_table_per_pp[np.ix_(row_indices, col_indices)]

    # --- MAIN FIGURE (with data) ---
    fig, ax = plt.subplots()
    im = ax.imshow(
        np.log(sobol_table_subset), 
        vmin=-5.5, vmax=-0.5, 
        aspect='auto'
    )
    ax.set_title(titles[pp], fontsize=14)

    # Define the ticks to match the subset
    if last_val is not None and last_unq_feature is not None:
        # X-axis: parameter names
        param_names = last_val[list(last_val.keys())[0]][1]['names']
        ax.set_xticks(range(len(col_indices)))
        ax.set_xticklabels([param_names[c] for c in col_indices], rotation=90)
        
        # Y-axis: feature names
        ax.set_yticks(range(len(row_indices)))
        ax.set_yticklabels([last_unq_feature[r] for r in row_indices])
    
    # Save main figure
    # plt.savefig(f"{titles[pp]}_summary_plot_zoomed.png", 
                # format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # --- SEPARATE FIGURE (color bar only) ---
    fig_cb, ax_cb = plt.subplots(figsize=(0.4, 3))  # narrower figure for color bar
    cbar = fig_cb.colorbar(im, cax=ax_cb)
    cbar.ax.tick_params(labelsize=10)
    cbar.set_label("log(Sobol Index)", fontsize=12)

    # Save color bar figure
    plt.savefig(f"{titles[pp]}_colorbar_only.png", 
                format="png", dpi=300, bbox_inches="tight")
    plt.close(fig_cb)
