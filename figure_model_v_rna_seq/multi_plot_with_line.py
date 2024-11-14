import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr, linregress
import seaborn as sns

# File paths for the CSVs
file1_path = 'exc_model_para_table.csv'
# file1_path = 'inh_model_para_table.csv'
file2_path = 'rna_data_table_1000_vgic.csv'

# Define the list of columns for x and y axes
cols_x = ['HCN1', 'HCN2', 'HCN3']  # Replace with actual column names
cols_y = ['gbar_Ih_somatic', 'gbar_Ih_basal']  # Replace with actual column names
# cols_x = ['KCNC1', 'KCNC2']  # Replace with actual column names
# cols_y = ['gbar_Kv3_1_somatic', 'gbar_Kv3_1_basal']  # Replace with actual column names
# cols_x = ['SCN1A', 'SCN2A']  # Replace with actual column names
# cols_y = ['gbar_NaV_somatic', 'gbar_NaV_basal']  # Replace with actual column names

key_column = 'cell_type'  # The third column in the first file

# Step 1: Read in two CSV files
df1 = pd.read_csv(file1_path)
df2 = pd.read_csv(file2_path)

# Step 2: Process cell names for matching
cell_of_string_1 = df1.iloc[:, 1].tolist()
cell_of_string_2 = df2.iloc[:, 0].tolist()

logi = [a in cell_of_string_2 for a in cell_of_string_1]
loca = [cell_of_string_2.index(a) if a in cell_of_string_2 else -1 for a in cell_of_string_1]

valid_loca = [index for index in loca if index != -1]
logi = np.where(logi)[0]

# Step 3: Create a dataframe with the valid data
df = pd.DataFrame({
    key_column: df1.iloc[logi, :][key_column].tolist(),
})

# Add all the columns for `cols_x` and `cols_y` to the dataframe
for col_x in cols_x:
    df[col_x] = df2.iloc[valid_loca, :][col_x].tolist()
for col_y in cols_y:
    df[col_y] = df1.iloc[logi, :][col_y].tolist()

# Step 4: Create subplots for each combination of x and y columns
num_plots = len(cols_x) * len(cols_y)
fig, axes = plt.subplots(len(cols_x), len(cols_y), figsize=(len(cols_y)*5, len(cols_x)*5))

# Flatten the axes array for easy indexing
axes = axes.flatten()

# Create the RGB palette (as in the original code)
# custom_colors = [
#     (0.8, 0.8, 0.0),  # Yellow
#     (0.95, 0.0, 0.0),  # Red
#     (0.0, 0.95, 0.0),  # Green
#     (0.0, 0.0, 0.95),  # Blue
# ]
custom_colors = [
    (0.0, 1.0, 1.0),  
    (0.0, 0.8, 0.8),  
    (0.0, 0.6, 0.6),  
]

custom_palette = sns.color_palette(custom_colors)

# Step 5: Loop through each pair of (x, y) columns and plot on the corresponding axis
for i, (col_x, col_y) in enumerate([(x, y) for x in cols_x for y in cols_y]):
    ax = axes[i]
    
    sns.scatterplot(data=df, x=col_x, y=col_y, hue=key_column, palette=custom_palette, s=50, alpha=0.1, ax=ax)
    
    # Overlay the median and 10-90% range for each group
    group_stats = df.groupby(key_column).agg(
        median_x=(col_x, 'median'),
        median_y=(col_y, 'median'),
        lower_x=(col_x, lambda x: np.percentile(x, 10)),
        upper_x=(col_x, lambda x: np.percentile(x, 90)),
        lower_y=(col_y, lambda y: np.percentile(y, 10)),
        upper_y=(col_y, lambda y: np.percentile(y, 90))
    )

    for group, stats in group_stats.iterrows():
        color = custom_palette[list(group_stats.index).index(group)]
        
        # Plot median with the group's color
        ax.scatter(stats['median_x'], stats['median_y'], color=color, zorder=5)
        
        # Plot 10-90% range as a rectangle with thicker lines
        ax.plot([stats['lower_x'], stats['upper_x']], [stats['median_y'], stats['median_y']], color=color, lw=3)
        ax.plot([stats['median_x'], stats['median_x']], [stats['lower_y'], stats['upper_y']], color=color, lw=3)

    # Calculate Pearson correlation
    corr, p_value = pearsonr(df[col_x], df[col_y])
    
    # Add a regression line (straight line fit)
    slope, intercept, r_value, p_value_regression, std_err = linregress(df[col_x], df[col_y])
    
    # Generate a smoother range of x values for the regression line
    x_values_for_line = np.linspace(df[col_x].min(), df[col_x].max(), 100)
    y_values_for_line = slope * x_values_for_line + intercept
    
    # Plot the smoother regression line (less dense)
    ax.plot(x_values_for_line, y_values_for_line, color='black', lw=2, linestyle='--')  # Black dashed line for regression

    # Set the title with the Pearson correlation and p-value
    ax.set_title(f"{col_x} vs {col_y}\nPearson: {corr:.2f}, p-value: {p_value:.2e}", fontsize=10)

    ax.set_xlabel(col_x)
    ax.set_ylabel(col_y)
    ax.grid(True)

# Hide any extra axes if there are more subplots than combinations
for i in range(num_plots, len(axes)):
    axes[i].axis('off')

# Adjust layout for better spacing between subplots
plt.tight_layout()

# Save the plot with a dynamic file name based on the column names
file_name = f"scatter_w_lines_plots_{'_'.join(cols_x)}_vs_{'_'.join(cols_y)}.png"
plt.savefig(file_name, dpi=300)
plt.show()  # Add this to ensure the figure is displayed
