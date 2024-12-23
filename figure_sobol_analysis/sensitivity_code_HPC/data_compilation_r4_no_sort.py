
import pickle
import os
import glob
import natsort 
from copy import deepcopy as dcp
import json
import sys


folder_name = sys.argv[1]


folder_name_list = natsort.natsorted(  glob.glob(folder_name+'/*Out*'))
folder_name = folder_name_list[int(sys.argv[2])]
data_folder = folder_name

# data_folder = 'out_folder'

file_list = natsort.natsorted(  glob.glob(data_folder+'/compiled_data_*.pickle'))
# print(file_list)


full_data = []
# 
current_best_score = 99999

for each_file in file_list :
    new_data = []
    file_handle = open(each_file,'rb')
    each_value = pickle.load( file_handle )
    file_handle.close
    print(str(len(each_value[0])))

    tot_score = []
    for each_model in each_value[0] :
        tot_score.append(dcp(each_model['mean_score']))

    if not tot_score:
        min_value = min(tot_score)
        min_index = tot_score.index(min_value)

        each_model = dcp(each_value[0][min_index])
        print(each_model['mean_score'])

        if each_model['mean_score']<current_best_score:
            current_best_score = dcp(each_model['mean_score'])
            for each_trace in each_model['trace']:
                if each_model['trace'][each_trace] is not None:
                    for each_array in each_model['trace'][each_trace]:
                        each_model['trace'][each_trace][each_array] = each_model['trace'][each_trace][each_array].tolist()
        else:
            del each_model['trace']

        full_data.append(each_model)
    else:
        full_data.append({})
    # only document trace if the score is beter !!!!!!!!!!!!


    
out_file = open( "./full_data_" + folder_name.split("/")[-1].split("_seed")[0] +".json", "w")
json.dump(full_data, out_file, indent = 2)
out_file.close()



