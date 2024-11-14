import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr

# File paths for the CSVs
file1_path = 'inh_model_para_table.csv'
file2_path = 'rna_data_table_1000_vgic.csv'


# Column names for data columns to plot (replace with actual column names)
col_x = 'HCN1'
col_y = 'gbar_Ih_somatic'
key_column = 'cell_type'  # This is the third column in the first file (assuming it's the "key" column)

# Step 1: Read in two CSV files
df1 = pd.read_csv(file1_path)
df2 = pd.read_csv(file2_path)


cell_of_string_1 = df1.iloc[:,1].tolist()
cell_of_string_2 = df2.iloc[:,0].tolist()


logi = [a in cell_of_string_2 for a in cell_of_string_1]
loca = [cell_of_string_2.index(a) if a in cell_of_string_2 else -1 for a in cell_of_string_1]

valid_loca = [index for index in loca if index != -1]
logi = np.where(logi)[0]

len(logi)
len(valid_loca)

df = pd.DataFrame({col_y: df1.iloc[logi,:][col_y].tolist(), key_column: df1.iloc[logi,:][key_column].tolist(), col_x: df2.iloc[valid_loca,:][col_x].tolist()})








import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr

# Define the RGB codes for your custom colors (for example)
custom_colors = [
    (0.8, 0.8, 0.0),  # Yellow
    (0.95, 0.0, 0.0),  # Red
    (0.0, 0.95, 0.0),  # Green
    (0.0, 0.0, 0.95),  # Blue
]


# Create a custom color palette from the RGB values
custom_palette = sns.color_palette(custom_colors)

plt.figure(figsize=(10, 8))

# Scatter plot with smaller dots (alpha set to 0.1)
sns.scatterplot(data=df, x=col_x, y=col_y, hue=key_column, palette=custom_palette, s=50, alpha=0.1)

# Overlay the median and 10-90% range for each group
group_stats = df.groupby(key_column).agg(
    median_x=(col_x, 'median'),
    median_y=(col_y, 'median'),
    lower_x=(col_x, lambda x: np.percentile(x, 10)),
    upper_x=(col_x, lambda x: np.percentile(x, 90)),
    lower_y=(col_y, lambda y: np.percentile(y, 10)),
    upper_y=(col_y, lambda y: np.percentile(y, 90))
)

# Loop through each group and plot the group statistics
for group, stats in group_stats.iterrows():
    # Retrieve the color corresponding to the group from the custom palette
    color = custom_palette[list(group_stats.index).index(group)]
    
    # Plot median with the group's color
    plt.scatter(stats['median_x'], stats['median_y'], color=color, zorder=5)
    
    # Plot 10-90% range as a rectangle with thicker lines
    plt.plot([stats['lower_x'], stats['upper_x']], [stats['median_y'], stats['median_y']], color=color, lw=3)
    plt.plot([stats['median_x'], stats['median_x']], [stats['lower_y'], stats['upper_y']], color=color, lw=3)

# Calculate the Pearson correlation across all data
corr, p_value = pearsonr(df[col_x], df[col_y])

# Set the title with the Pearson correlation and p-value in scientific notation
plt.title(f"Pearson Correlation: {corr:.2f}, p-value: {p_value:.2e}", fontsize=16)

# Adjust plot settings
plt.xlabel(col_x)
plt.ylabel(col_y)
plt.legend(title=key_column)
plt.grid(True)

# Save the plot as a high-definition PNG (300 DPI)
plt.savefig("scatter_plot_with_medians_and_range_pearson.png", dpi=300)
