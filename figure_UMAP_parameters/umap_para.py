import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import umap
from sklearn.preprocessing import LabelEncoder, StandardScaler

# # Tunable parameters
# input_csv = 'inh_model_para_table.csv'  # Path to the CSV file
# color_column = 2         # Column index (0-based) for group keys
# data_start_column = 5    # Starting column index (0-based) for data to use in UMAP

# # Parameter ranges for the grid search
# spread_values = [1]  # Adjust the spread from low to high
# ratio_values = [0.8]  # Different ratios between spread and min_dist

# n_neighbors = 1024  # Fixed number of neighbors
# random_state = 1211

# alpha=0.4

# # Custom RGB color table (one row per category, normalized to [0, 1])
# color_table = np.array([
#     [1, 1, 0],  # Yellow
#     [1, 0, 0],  # Red
#     [0, 1, 0],  # Green
#     [0, 0, 1],  # Blue
#     # Add more colors as needed
# ])

# Tunable parameters
input_csv = 'exc_model_para_table.csv'  # Path to the CSV file
color_column = 2         # Column index (0-based) for group keys
data_start_column = 5    # Starting column index (0-based) for data to use in UMAP

# Parameter ranges for the grid search
spread_values = [ 1]  # Adjust the spread from low to high
ratio_values = [  0.1]  # Different ratios between spread and min_dist

n_neighbors = 1024  # Fixed number of neighbors
random_state = 1211

# Load the data
data = pd.read_csv(input_csv)

# Extract group keys and features
group_keys = data.iloc[:, color_column]
features = data.iloc[:, data_start_column:]

# Normalize the features using StandardScaler
scaler = StandardScaler()
features_normalized = scaler.fit_transform(features)

# Encode group keys into numeric labels for coloring
label_encoder = LabelEncoder()
group_labels = label_encoder.fit_transform(group_keys)
unique_labels = label_encoder.classes_


color_table = np.array([
    [0.2, 1, 1],  # Cyan
    [0, 0.8, 0.8],  # Cyan
    [0.1, 0.4, 0.4],  # Cyan
    [1, 0, 1],  # Magenta
    [1, 0.5, 0],  # Orange
    # Add more colors as needed
])

alpha=0.4




# Load the data
data = pd.read_csv(input_csv)

# Extract group keys and features
group_keys = data.iloc[:, color_column]
features = data.iloc[:, data_start_column:]

# Normalize the features using StandardScaler
scaler = StandardScaler()
features_normalized = scaler.fit_transform(features)

# Encode group keys into numeric labels for coloring
label_encoder = LabelEncoder()
group_labels = label_encoder.fit_transform(group_keys)
unique_labels = label_encoder.classes_

# Ensure the color table covers all unique labels
if len(color_table) < len(unique_labels):
    raise ValueError("Insufficient colors in color_table for the number of unique categories.")

# Map group labels to colors
category_colors = np.array([color_table[label] for label in group_labels])

# Prepare subplots
fig, axes = plt.subplots(1, 2, figsize=(10, 5), constrained_layout=True)


axes = axes.flatten()

# Iterate over parameter combinations
plot_idx = 0
for spread in spread_values:
    for ratio in ratio_values:
        # Calculate min_dist as the ratio of spread
        min_dist = spread * ratio
        
        # Perform UMAP
        umap_model = umap.UMAP(n_neighbors=n_neighbors, spread=spread, min_dist=min_dist, random_state=random_state)
        umap_results = umap_model.fit_transform(features_normalized)
        
        # Plot in the corresponding subplot with custom RGB colors
        ax = axes[plot_idx]
        scatter = ax.scatter(
            umap_results[:, 0], 
            umap_results[:, 1], 
            c=category_colors, 
            alpha=alpha  # Set transparency to 0.5
        )
        # ax.set_title(f"S: {spread}, R: {ratio}, MD: {min_dist:.2f}", fontsize=8)
        ax.axis('off')  # Remove axes for clarity
        
        plot_idx += 1
        if plot_idx >= len(axes):
            break
    if plot_idx >= len(axes):
        break

# Add a legend with category labels
handles = [
    plt.Line2D([0], [0], marker='o', color=color_table[i], linestyle='', markersize=10)
    for i in range(len(unique_labels))
]
ax_legend = axes[-1]
ax_legend.legend(handles, unique_labels, title="Group Keys",  loc='lower left')
ax_legend.axis('off')  # Hide the legend axis

ax = axes[0]
ax.set_title("UMAP Model Parameters", fontsize=16)


# Display the grid
# plt.suptitle("UMAP Model Parameters", fontsize=16)
plt.savefig("umap_para.png", dpi=300)
plt.show()
