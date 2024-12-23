
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


new_data = []

for each_file in file_list :
    file_handle = open(each_file,'rb')
    each_value = pickle.load( file_handle )
    file_handle.close
    for each_model in each_value[0] :
        del each_model['trace']
        new_data.append( dcp(each_model) )
    print(str(len(new_data)))



tot_score = []
for each_model in new_data :
    tot_score.append(dcp(each_model['mean_score']))


sorted_new_data = [x for _,x in sorted(zip(tot_score,new_data))]

max_para_dict = dcp(sorted_new_data[0]['param_dict'])
min_para_dict = dcp(sorted_new_data[0]['param_dict'])


for each_model in sorted_new_data[:100] :
    for each_para in max_para_dict :
        max_para_dict[each_para] = max( max_para_dict[each_para], each_model['param_dict'][each_para] )
        min_para_dict[each_para] = min( min_para_dict[each_para], each_model['param_dict'][each_para] )


filtered_models = []

for each_model in sorted_new_data :
    still_good = True
    for each_para in max_para_dict :
        if each_model['param_dict'][each_para] > max_para_dict[each_para] :
            still_good = False
        if each_model['param_dict'][each_para] < min_para_dict[each_para] :
            still_good = False
    if still_good :
        filtered_models.append(each_model)

print(str(len(filtered_models)))




feature_list = list(filtered_models[0]['response'])
para_list = list(filtered_models[0]['param_dict'])

max_para_dict = dcp(filtered_models[0]['param_dict'])
min_para_dict = dcp(filtered_models[0]['param_dict'])


for each_model in filtered_models[:100] :
    for each_para in para_list :
        max_para_dict[each_para] = max( max_para_dict[each_para], each_model['param_dict'][each_para] )
        min_para_dict[each_para] = min( min_para_dict[each_para], each_model['param_dict'][each_para] )

boundss = []
namess = []



for each_para in para_list :
    boundss.append(dcp([min_para_dict[each_para], max_para_dict[each_para]]))
    namess.append(dcp( each_para ))


problem = {
    'num_vars': len(list( filtered_models[0]['param_dict'] )),
    'names': namess,
    'bounds': boundss
}

import SALib
import numpy as np

import SALib.analyze.rbd_fast
import SALib.analyze.delta
import SALib.analyze.pawn

analyzed_results = {}

for each_feature in feature_list :
    param_values = []
    Y = []
    for each_model in filtered_models :
        para_temp = []
        for each_para in para_list :
                para_temp.append( dcp(each_model['param_dict'][each_para]) )
        param_values.append(dcp( para_temp ))
        if (each_model['response'][each_feature] != None) :
            Y.append(dcp( each_model['response'][each_feature] ))
        else :
            Y.append(0.0)
    param_values = np.array( param_values )
    Y = np.array( Y )
    outt = SALib.analyze.rbd_fast.analyze(problem, param_values, Y, M=30, num_resamples=200, conf_level=0.95, print_to_console=False, seed=None)
    outt2 = SALib.analyze.delta.analyze(problem, param_values, Y, num_resamples=200, conf_level=0.95, print_to_console=False, seed=None)

    outt3 = SALib.analyze.pawn.analyze(problem, param_values, Y, S=10,  print_to_console=False, seed=None)

    analyzed_results.update({each_feature: dcp([ outt, outt2, outt3 ])})
    print(each_feature+' sensitivity done')


    
# out_file = open(data_folder + "/all_sensitivity_v2.json", "w")
# json.dump(analyzed_results, out_file, indent = 2)
# out_file.close()


out_file = open(data_folder + "/all_sensitivity_v2.pickle", "wb")
pickle.dump(analyzed_results, out_file)
out_file.close()