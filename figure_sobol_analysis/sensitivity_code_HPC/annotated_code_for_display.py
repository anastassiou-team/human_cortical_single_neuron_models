#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Below is the code with in-line comments explaining each step and section in detail.
"""

import pickle   # For serializing/de-serializing Python objects
import os       # For directory and path operations (not heavily used in this script)
import glob     # For finding pathnames and files using patterns
import natsort  # For "natural sorting" of filenames/folders (e.g., "2" < "10", but properly handled as numeric not string)
from copy import deepcopy as dcp  # For creating independent copies to avoid mutable reference side effects
import json     # For reading/writing JSON data (currently commented out in saving portion)
import sys      # For reading command line arguments (sys.argv)

# --------------------------------------------------------------------------------------
# COMMAND-LINE ARGUMENTS:
# 1) A base directory path containing subfolders that match '*Out*'
# 2) An integer index used to select one of the '*Out*' subfolders from a sorted list
#
# Example usage:
#   python script.py base_folder 0
#   -> This will pick the first subfolder matching '*Out*' inside 'base_folder'
# --------------------------------------------------------------------------------------

# The first command-line argument: a base folder name/prefix
folder_name = sys.argv[1]

# Use glob to find all subfolders in 'folder_name' that match '*Out*' 
# and sort them in "natural" order, so numeric parts are sorted properly.
folder_name_list = natsort.natsorted(glob.glob(folder_name + '/*Out*'))

# The second command-line argument is an integer index to pick one folder from the sorted list
folder_name = folder_name_list[int(sys.argv[2])]
data_folder = folder_name  # We will refer to this variable in the rest of the code

# Inside this chosen data folder, find files named 'compiled_data_*.pickle' 
# and again sort them with natural sort ordering
file_list = natsort.natsorted(glob.glob(data_folder + '/compiled_data_*.pickle'))

# We will collect loaded, pruned data into 'new_data'
new_data = []

# --------------------------------------------------------------------------------------
# LOAD AND PRUNE DATA:
# For each compiled pickle file, we load it and remove a 'trace' key (likely large or 
# unneeded debug info) from each model's dictionary, then store a deep copy in 'new_data'.
# --------------------------------------------------------------------------------------
for each_file in file_list :
    # Open the pickle file in binary read mode
    file_handle = open(each_file, 'rb')
    # Load the data structure from the pickle
    each_value = pickle.load(file_handle)
    # Note: file_handle.close is missing parentheses, so strictly speaking it won't close,
    # but Python should handle it eventually. 
    # For proper style, it should be file_handle.close().
    file_handle.close

    # The loaded data (each_value) is assumed to be a list-like structure where 
    # 'each_value[0]' contains multiple model dictionaries
    for each_model in each_value[0] :
        # Delete the 'trace' key from each model, presumably to reduce memory usage 
        # or remove debugging data not needed for analysis
        del each_model['trace']
        # Append a deep copy of the pruned model to 'new_data'
        new_data.append(dcp(each_model))

    # Print the running total of how many models have been loaded so far
    print(str(len(new_data)))

# --------------------------------------------------------------------------------------
# SORT THE MODELS BY THEIR 'mean_score' AND PREPARE FOR FILTERING:
# We will sort all models by their 'mean_score' (ascending) and then look at the top 100
# to derive a bounding parameter range. After that, we filter the entire dataset to keep
# only models whose parameters fit within those derived bounds.
# --------------------------------------------------------------------------------------

# Extract the mean_score for each model and store in tot_score
tot_score = []
for each_model in new_data :
    tot_score.append(dcp(each_model['mean_score']))

# Sort new_data by tot_score (ascending). 
# The first model in sorted_new_data has the lowest mean_score.
sorted_new_data = [x for _, x in sorted(zip(tot_score, new_data))]

# --------------------------------------------------------------------------------------
# DETERMINE PARAMETER RANGES FROM THE TOP 100 MODELS:
# We assume the top 100 are "best" in some sense (lowest scores). We'll collect the min 
# and max for each parameter across these top 100, forming a bounding box.
# --------------------------------------------------------------------------------------

# Initialize max_para_dict and min_para_dict from the first (lowest score) model
max_para_dict = dcp(sorted_new_data[0]['param_dict'])
min_para_dict = dcp(sorted_new_data[0]['param_dict'])

# Among the top 100 models, track parameter-wise maximum and minimum values
for each_model in sorted_new_data[:100] :
    for each_para in max_para_dict :
        # Update max if current model's parameter is higher
        max_para_dict[each_para] = max(max_para_dict[each_para], each_model['param_dict'][each_para])
        # Update min if current model's parameter is lower
        min_para_dict[each_para] = min(min_para_dict[each_para], each_model['param_dict'][each_para])

# --------------------------------------------------------------------------------------
# FILTER MODELS TO THOSE WITHIN THE MIN-MAX BOUNDS:
# Now we apply this bounding box to *all* sorted models (not just the top 100), and 
# only keep those whose parameters are strictly within [min, max].
# --------------------------------------------------------------------------------------

filtered_models = []

# Check each model's parameters against the derived min/max values
for each_model in sorted_new_data :
    still_good = True
    for each_para in max_para_dict :
        # If any parameter is above max or below min, exclude this model
        if each_model['param_dict'][each_para] > max_para_dict[each_para] :
            still_good = False
        if each_model['param_dict'][each_para] < min_para_dict[each_para] :
            still_good = False

    # If after checking all parameters 'still_good' remains True, the model is within bounds
    if still_good :
        filtered_models.append(each_model)

# Print the number of models that passed this filter
print(str(len(filtered_models)))


# --------------------------------------------------------------------------------------
# PREPARE FOR SENSITIVITY ANALYSIS:
# We'll identify the features and parameter names from the first filtered model, then 
# re-derive (or confirm) the parameter bounds from the top 100 filtered models. This 
# bounding info is needed by SALib to define the problem space.
# --------------------------------------------------------------------------------------

# A 'feature' is presumably a key in the 'response' dictionary
feature_list = list(filtered_models[0]['response'])
# A 'parameter' is a key in the 'param_dict'
para_list = list(filtered_models[0]['param_dict'])

# Re-initialize parameter range dictionaries from the first filtered model
max_para_dict = dcp(filtered_models[0]['param_dict'])
min_para_dict = dcp(filtered_models[0]['param_dict'])

# Among the top 100 FILTERED models (rather than top 100 overall), get updated min/max
for each_model in filtered_models[:100] :
    for each_para in para_list :
        max_para_dict[each_para] = max(max_para_dict[each_para], each_model['param_dict'][each_para])
        min_para_dict[each_para] = min(min_para_dict[each_para], each_model['param_dict'][each_para])

# Build lists for SALib's 'problem' dictionary: one for bounds, one for names
boundss = []
namess = []

# For each parameter, gather the min and max in a list and store the parameter name
for each_para in para_list :
    boundss.append(dcp([min_para_dict[each_para], max_para_dict[each_para]]))
    namess.append(dcp(each_para))

# The 'problem' dictionary tells SALib the number of parameters, their names, and bounds
problem = {
    'num_vars': len(list(filtered_models[0]['param_dict'])),  # How many parameters total
    'names': namess,                                          # The names of these parameters
    'bounds': boundss                                         # The corresponding [min, max] range per parameter
}

# --------------------------------------------------------------------------------------
# IMPORT SALib AND PERFORM GLOBAL SENSITIVITY ANALYSIS:
# We will try three methods from SALib: RBD-FAST, Delta, and PAWN. 
# For each feature, we gather parameter values X and corresponding model outputs Y, 
# then run the analyses. 
# --------------------------------------------------------------------------------------

import SALib
import numpy as np

# SALib analyzers for different methods
import SALib.analyze.rbd_fast
import SALib.analyze.delta
import SALib.analyze.pawn

# This dictionary will store the results for each feature:
#   analyzed_results[feature] = [RBD-FAST result, Delta result, PAWN result]
analyzed_results = {}

# Loop through each feature (output variable) we want to analyze
for each_feature in feature_list :
    param_values = []  # 2D structure: each row is a vector of parameter values from one model
    Y = []             # 1D structure: each element is the response for that model at 'each_feature'

    # Build up param_values (X) and Y from the filtered models
    for each_model in filtered_models :
        para_temp = []
        for each_para in para_list :
            # Collect the parameter values for this model in a list
            para_temp.append(dcp(each_model['param_dict'][each_para]))
        # Add the parameter vector to param_values
        param_values.append(dcp(para_temp))

        # If the response for this feature is None, we treat it as 0.0
        # Otherwise, store the actual numeric value
        if each_model['response'][each_feature] is not None :
            Y.append(dcp(each_model['response'][each_feature]))
        else :
            Y.append(0.0)

    # Convert Python lists to NumPy arrays as required by SALib
    param_values = np.array(param_values)
    Y = np.array(Y)

    # ----------------------
    # 1) RBD-FAST Analysis
    # ----------------------
    outt = SALib.analyze.rbd_fast.analyze(
        problem,        # The SALib problem definition: parameters, names, bounds
        param_values,   # The matrix of input parameter values 
        Y,              # The output array for the chosen feature
        M=30,           # The number of harmonics (FAST uses Fourier series expansions)
        num_resamples=200,  # For bootstrap-based confidence intervals
        conf_level=0.95,    # Confidence interval
        print_to_console=False,  # Avoid printing to console
        seed=None            # Random seed if reproducibility is needed
    )

    # ----------------------
    # 2) Delta Analysis
    # ----------------------
    outt2 = SALib.analyze.delta.analyze(
        problem,
        param_values,
        Y,
        num_resamples=200,
        conf_level=0.95,
        print_to_console=False,
        seed=None
    )

    # ----------------------
    # 3) PAWN Analysis
    # ----------------------
    outt3 = SALib.analyze.pawn.analyze(
        problem,
        param_values,
        Y,
        S=10,                 # Typically the number of (C)subsets or partitions for PAWN 
        print_to_console=False,
        seed=None
    )

    # Store the three analysis outputs (RBD-FAST, Delta, PAWN) in a list, keyed by the feature
    analyzed_results.update({each_feature: dcp([outt, outt2, outt3])})

    # Print a confirmation for each completed feature
    print(each_feature + ' sensitivity done')

# --------------------------------------------------------------------------------------
# SAVE THE RESULTS:
# The code below shows two approaches: saving to JSON (currently commented) and 
# saving to a pickle file (active code).
# --------------------------------------------------------------------------------------

# Uncomment this block if you wish to save as JSON instead of (or in addition to) pickle:
# out_file = open(data_folder + "/all_sensitivity_v2.json", "w")
# json.dump(analyzed_results, out_file, indent=2)
# out_file.close()

# Here we save all results in a pickle file, which preserves Python objects:
out_file = open(data_folder + "/all_sensitivity_v2.pickle", "wb")
pickle.dump(analyzed_results, out_file)
out_file.close()
