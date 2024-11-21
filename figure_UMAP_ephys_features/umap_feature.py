import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import umap
import os

# Set file paths
file1 = 'inh_model_feature_table.csv'  # Replace with your actual file path
# file1 = 'exc_model_feature_table.csv'  # Replace with your actual file path
file2 = 'ephys_features_w_meta.csv'    # Replace with your actual file path
# Step 8: Prepare color mapping for UMAP plotting
color_table = np.array([
    [1, 1, 0],  # Yellow
    [1, 0, 0],  # Red
    [0, 1, 0],  # Green
    [0, 0, 1],  # Blue
    # [0.2, 1, 1],  # Cyan
    # [0, 0.8, 0.8],  # Cyan
    # [0.1, 0.4, 0.4],  # Cyan
    # [1, 0, 1],  # Magenta
    # [1, 0.5, 0],  # Orange

    # Extend this array as needed
])
# Features to remove from Table 1 keep the annotated part, so I can un comment later
feature_cols_to_remove = [
        'cell_name',
        # 'spec_id',
        # 'cell_type',
        'seed_no',
        'hof_no',
        # 'AHP1_depth_from_peak',
        'AHP_depth',
        # 'AHP_time_from_peak',
        'AP1_peak',
        # 'AP1_width',
        'Spikecount',
        # 'decay_time_constant_after_stim',
        'depol_block',
        # 'inv_first_ISI',
        # 'mean_AP_amplitude',
        # 'sag_amplitude',
        'steady_state_voltage',
        'steady_state_voltage_stimend',
        'time_to_first_spike',
        'voltage_base'
        ]



# Step 1: Load the CSV files
df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)


# Step 2: Filter rows in df2 to match groups present in df1
valid_groups = df1['cell_type'].unique()
df2 = df2[df2['cell_type'].isin(valid_groups)]

# Step 3: Remove specified feature columns from df1
df1 = df1.drop(columns=feature_cols_to_remove)

# Step 4: Keep only shared features between df1 and df2
shared_features = [col for col in df1.columns if col not in ['spec_id', 'cell_type']]
df2 = df2[['spec_id', 'cell_type'] + shared_features]

df1 = df1.dropna()
df2 = df2.dropna()



# Step 5: Combine datasets for normalization
combined_data = pd.concat([df1, df2], ignore_index=True)

# Step 6: Z-normalize the combined data and replace NaN with -1
normalized_data = (combined_data[shared_features] - combined_data[shared_features].mean()) / combined_data[shared_features].std()
# normalized_data = normalized_data.fillna(0)

# Step 7: Split the normalized data back into df1 and df2
df1_normalized = normalized_data.iloc[:len(df1)]
df2_normalized = normalized_data.iloc[len(df1):]


unique_groups = pd.concat([df1['cell_type'], df2['cell_type']]).unique()
color_mapping = {group: color_table[i % len(color_table)] for i, group in enumerate(unique_groups)}

# Step 9: Assign colors to points in df1 and df2
df1_colors = [color_mapping[group] for group in df1['cell_type']]
df2_colors = [color_mapping[group] for group in df2['cell_type']]

# Step 10: Set UMAP parameters
spread =  8.0
min_dist_ratio = 0.6
alpha1 = 0.1  # High transparency for df1
alpha2 = 0.8  # Low transparency for df2

# Step 11: Ensure output directory exists
# output_dir = "umap_plots"
# os.makedirs(output_dir, exist_ok=True)

# Step 12: Plot UMAP with tunable parameters



size_1 = 25
size_2 = 50
fig, axes = plt.subplots(1,2, figsize=(10,5))
fig.tight_layout(pad=4.0)


min_dist = spread * min_dist_ratio
umap_reducer = umap.UMAP(spread=spread, min_dist=min_dist, random_state=42)

# Combine normalized data for UMAP
combined_normalized_data = pd.concat([df1_normalized, df2_normalized], ignore_index=True).values
embeddings = umap_reducer.fit_transform(combined_normalized_data)

# Plot embeddings
ax = axes[0]
ax.scatter(
    embeddings[:len(df1), 0], embeddings[:len(df1), 1],
    c=df1_colors, alpha=alpha1, s=size_1
)
ax.scatter(
    embeddings[len(df1):, 0], embeddings[len(df1):, 1],
    c=df2_colors, alpha=alpha2, s=size_2, edgecolors = 'black'
)
# ax.set_title(f"Spread: {spread}, Min_Dist: {min_dist:.2f}")
ax.set_title("8 Ephys features (Exp in black circle, Models in transparent)")

ax.axis('off')  # Hide the legend axis

handles = [
    plt.Line2D([0], [0], marker='o', color=color_table[i], linestyle='', markersize=10)
    for i in range(len(unique_groups))
]
ax_legend = ax
ax_legend.legend(handles, unique_groups, title="Group Keys",  loc='lower left')
ax_legend.axis('off')  # Hide the legend axis




min_dist = spread * min_dist_ratio
umap_reducer = umap.UMAP(spread=spread, min_dist=min_dist, random_state=42)

# Combine normalized data for UMAP
combined_normalized_data = pd.concat([df1_normalized, df2_normalized], ignore_index=True).values
embeddings = umap_reducer.fit_transform(combined_normalized_data)

# Plot embeddings
ax = axes[1]

ax.scatter(
    embeddings[len(df1):, 0], embeddings[len(df1):, 1],
    c=df2_colors, alpha=alpha2, s=size_1
)
ax.scatter(
    embeddings[:len(df1), 0], embeddings[:len(df1), 1],
    c=df1_colors, alpha=alpha2, s=size_1
)
# ax.set_title(f"Spread: {spread}, Min_Dist: {min_dist:.2f}")
ax.set_title("8 Ephys features (Exp & Models)")
ax.axis('off')  # Hide the legend axis



handles = [
    plt.Line2D([0], [0], marker='o', color=color_table[i], linestyle='', markersize=10)
    for i in range(len(unique_groups))
]
ax_legend = ax
ax_legend.legend(handles, unique_groups, title="Group Keys",  loc='lower left')
ax_legend.axis('off')  # Hide the legend axis

# Save the figure
output_file = "umap_feature_inh.png"

fig.savefig(output_file, dpi=300, format="png")
print(f"UMAP plot saved as {output_file}")
