import math
import json
import os
import numpy as np
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import pandas as pd
import umap

main_dir = os.path.join(os.getcwd())

#%% Formatting

inh_celltype_list = ['PVALB','SST','VIP','LAMP5PAX6Other']
exc_celltype_list = ['ITL6','ITL23','ITL35','ITL46','L56NP']

inh_colors = ['r','g','b','y']
exc_colors = np.array([
    [0.2, 1, 1],  # Cyan
    [0, 0.8, 0.8],  # Cyan
    [0.1, 0.4, 0.4],  # Cyan
    [1, 0, 1],  # Magenta
    [1, 0.5, 0],  # Orange
    ])

#%% Import Data

#Experimental Ephys Data
ephys_exp = pd.read_csv(os.path.join(main_dir,'ephys_exp_features.csv'), index_col=False)

#Simulated Ephys Data
inh_ephys_sim = pd.read_csv(os.path.join(main_dir,'inh_ephys_sim_features.csv'), index_col=False)
exc_ephys_sim = pd.read_csv(os.path.join(main_dir,'exc_ephys_sim_features.csv'), index_col=False)

#%% Get Top 10 models per cell

def get_topmodels(ephys_sim,n=10):
    
    output = pd.DataFrame()
    
    cell_ids = ephys_sim['cell_id'].unique()   
    for cell_id in cell_ids:
        temp = ephys_sim[ephys_sim['cell_id'] == cell_id]
        temp = temp.sort_values(by='hof',ascending=True) #sort dataframe from lowest hof number to highest
        output = pd.concat([output,temp.iloc[:n,:]]) #keep n top hof models per cell_id
        
    output = output.reset_index(drop=True)
    
    return output

inh_ephys_sim = get_topmodels(inh_ephys_sim,n=10)
exc_ephys_sim = get_topmodels(exc_ephys_sim,n=10)

#%% Preprocessing

#Drop non-firing cells
ephys_exp = ephys_exp[ephys_exp['depol.Spikecount'] > 0].reset_index(drop=True)
inh_ephys_sim = inh_ephys_sim[inh_ephys_sim['Spikecount'] > 0].reset_index(drop=True)
exc_ephys_sim = exc_ephys_sim[exc_ephys_sim['Spikecount'] > 0].reset_index(drop=True)

#Split experimental features into exc and inh
inh_ephys_exp = ephys_exp[ephys_exp['cell_type'].isin(inh_celltype_list)]
exc_ephys_exp = ephys_exp[ephys_exp['cell_type'].isin(exc_celltype_list)]

#Get Feature column onlys
inh_ephys_exp_features = inh_ephys_exp.iloc[:,8:]
exc_ephys_exp_features = exc_ephys_exp.iloc[:,8:]
inh_ephys_sim_features = inh_ephys_sim.iloc[:,5:]
exc_ephys_sim_features = exc_ephys_sim.iloc[:,5:]
inh_ephys_sim_features.columns = inh_ephys_exp_features.columns #match column names
exc_ephys_sim_features.columns = inh_ephys_exp_features.columns #match column names

#Drop depolarization block feature
inh_ephys_exp_features = inh_ephys_exp_features.drop('depol.depol_block',axis=1)
exc_ephys_exp_features = exc_ephys_exp_features.drop('depol.depol_block',axis=1)
inh_ephys_sim_features = inh_ephys_sim_features.drop('depol.depol_block',axis=1)
exc_ephys_sim_features = exc_ephys_sim_features.drop('depol.depol_block',axis=1)

#Drop nan feature rows
def drop_nan(feature_df,full_df):
    nan_indices = feature_df[feature_df.isna().any(axis=1)].index
    feature_df = feature_df.drop(nan_indices)
    full_df = full_df.drop(nan_indices)
    feature_df = feature_df.reset_index(drop=True)
    full_df = full_df.reset_index(drop=True)
    
    return feature_df,full_df

inh_ephys_exp_features,inh_ephys_exp = drop_nan(inh_ephys_exp_features,inh_ephys_exp)
exc_ephys_exp_features,exc_ephys_exp = drop_nan(exc_ephys_exp_features,exc_ephys_exp)
inh_ephys_sim_features,inh_ephys_sim = drop_nan(inh_ephys_sim_features,inh_ephys_sim)
exc_ephys_sim_features,exc_ephys_sim = drop_nan(exc_ephys_sim_features,exc_ephys_sim)

#%% Get Z-scores

def get_zscore(features):
    
    scaler = StandardScaler()
    scaler.fit(features)
    
    return scaler.transform(features)
    
inh_ephys_exp_features = get_zscore(inh_ephys_exp_features)
exc_ephys_exp_features = get_zscore(exc_ephys_exp_features)
inh_ephys_sim_features = get_zscore(inh_ephys_sim_features)
exc_ephys_sim_features = get_zscore(exc_ephys_sim_features)

#%% Generate Mapping

n_neighbors = 20 
min_dist = 0.2
random_state = 42

inh_df = np.vstack((inh_ephys_exp_features,inh_ephys_sim_features))
inh_labels = pd.concat((inh_ephys_exp,inh_ephys_sim),axis=0, ignore_index=True)
exc_df = np.vstack((exc_ephys_exp_features,exc_ephys_sim_features))
exc_labels = pd.concat((exc_ephys_exp,exc_ephys_sim),axis=0, ignore_index=True)

#Generate Inh UMAP
inh_trans = umap.UMAP(n_neighbors=n_neighbors,min_dist=min_dist, random_state=random_state).fit(inh_df)
inh_exp_embedding = inh_trans.transform(inh_ephys_exp_features)
inh_sim_embedding = inh_trans.transform(inh_ephys_sim_features)

#Generate Exc UMAP
exc_trans = umap.UMAP(n_neighbors=n_neighbors,min_dist=min_dist, random_state=random_state).fit(exc_df)
exc_exp_embedding = exc_trans.transform(exc_ephys_exp_features)
exc_sim_embedding = exc_trans.transform(exc_ephys_sim_features)

#%% Plot UMAP

def plot_umap(embedding_df,labels_df, title='', s = 100, save_name = None, ax = None, fontsize = 24,
              alpha_val = 1, colors = inh_colors, classes = inh_celltype_list):
    
    #Assign cell-type keys
    dict_key = {}
    for i in range(len(classes)): 
        dict_key[classes[i]] = i
    key = labels_df.cell_type.map(dict_key)
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))
    else:
        plt.sca(ax)
        
    for i, color in enumerate(colors):
        plt.scatter(
        embedding_df[key == i, 0],
        embedding_df[key == i, 1],
        c=color, label=classes[i],
        s=s,
        alpha = alpha_val)
    plt.gca().set_aspect('equal', 'datalim')
    plt.title(title, fontsize=fontsize)
    plt.xticks([])
    plt.yticks([])
    
    if save_name is not None:
        plt.savefig(save_name + '.png', format="png")
        
    return ax

#Plot Inhibitory cells, Simulation
plot_umap(inh_sim_embedding,inh_ephys_sim, title='', s = 100, save_name = 'umap_feature_inh_sim', ax = None, fontsize = 24,
              alpha_val = 0.8, colors = inh_colors, classes = inh_celltype_list)

#Plot Inhibitory cells, Experiment
plot_umap(inh_exp_embedding,inh_ephys_exp, title='', s = 100, save_name = 'umap_feature_inh_exp', ax = None, fontsize = 24,
              alpha_val = 0.8, colors = inh_colors, classes = inh_celltype_list)

#Plot Excitatory cells, Simulation
plot_umap(exc_sim_embedding,exc_ephys_sim, title='', s = 100, save_name = 'umap_feature_exc_sim', ax = None, fontsize = 24,
              alpha_val = 0.8, colors = exc_colors, classes = exc_celltype_list)

#Plot Excitatory cells, Experiment
plot_umap(exc_exp_embedding,exc_ephys_exp, title='', s = 100, save_name = 'umap_feature_exc_exp', ax = None, fontsize = 24,
              alpha_val = 0.8, colors = exc_colors, classes = exc_celltype_list)