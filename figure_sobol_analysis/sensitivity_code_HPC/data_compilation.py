#/home/wuy2/2023_0111_bpo_mod/venv_mod_bpo/bin/activate


import pickle
import os
import glob
import natsort 
from copy import deepcopy as dcp
import json
import sys


# folder_name = '/home/wuy2/2023_0120_bpo_mod_pv/689331391_seed_1_Outputs/'
folder_name = sys.argv[1]


folder_name_list = natsort.natsorted(  glob.glob(folder_name+'/*Out*'))

folder_name = folder_name_list[int(sys.argv[2])]
out_folder_name = folder_name

# os.mkdir(out_folder_name)


file_list_value = natsort.natsorted(  glob.glob(folder_name+'/dump_3_*'))
file_list_score = natsort.natsorted(  glob.glob(folder_name+'/dump_2_*'))
file_list_trace = natsort.natsorted(  glob.glob(folder_name+'/dump_1_*'))

if (len(file_list_value) != len(file_list_score)):
    raise()

if (len(file_list_value) != len(file_list_trace)):
    raise()



for each_file_idx in range(len(file_list_score)):
    # each_file_idx = 9
    keep_data = []

    file_handle = open(file_list_value[each_file_idx],'rb')
    each_value = pickle.load( file_handle )
    file_handle.close

    file_handle = open(file_list_score[each_file_idx],'rb')
    each_score = pickle.load( file_handle )
    file_handle.close

    file_handle = open(file_list_trace[each_file_idx],'rb')
    each_trace = pickle.load( file_handle )
    file_handle.close

    para_list = list(each_value[0]['param_dict'])



    each_value = sorted(each_value, key = lambda x: (list( x['param_dict'].values())))
    each_score = sorted(each_score, key = lambda x: (list( x['param_dict'].values())))
    each_trace = sorted(each_trace, key = lambda x: (list( x['param_dict'].values())))




    for ii in range(len(each_value)):
        looking_good = True
        for jj in range(len(para_list)):
            if each_value[ii]['param_dict'][para_list[jj]] != each_score[ii]['param_dict'][para_list[jj]]:
                looking_good = False
        for jj in range(len(para_list)):
            if each_value[ii]['param_dict'][para_list[jj]] != each_trace[ii]['param_dict'][para_list[jj]]:
                looking_good = False
        if looking_good == False :
            raise()

    each_combine = dcp(each_value)

    for ii in range(len(each_combine)):
        each_combine[ii].update({'score': each_score[ii]['response']})
        trace_temp = {}
        for each_trace_line in each_trace[ii]['response'] :
            trace_temp_temp = {}
            if each_trace[ii]['response'][each_trace_line] != None:
                trace_temp_temp.update({'time': each_trace[ii]['response'][each_trace_line]['time'].to_numpy()})
                trace_temp_temp.update({'voltage': each_trace[ii]['response'][each_trace_line]['voltage'].to_numpy()})
            else :
                trace_temp_temp = None
            trace_temp.update( {each_trace_line: dcp(trace_temp_temp)} )
        each_combine[ii].update( {'trace': dcp( trace_temp )} )

        
        # each_combine[ii].update({'trace': each_trace[ii]['response']})

    keep_data_temp = []
    for each_kid in each_combine:
        summed_up_scores_each_kid = 0.0
        for each_score in each_kid['score']:
            summed_up_scores_each_kid = summed_up_scores_each_kid + each_kid['score'][each_score]
        each_kid.update({'mean_score': dcp(summed_up_scores_each_kid)/ len(each_kid['score'])} )
        if (each_kid['mean_score'] <125 ):
            keep_data_temp.append(dcp( each_kid ))


    print(str(len(keep_data_temp)))
    keep_data.append(dcp( keep_data_temp ))


    # import h5py

    # with h5py.File('test.hdf5', 'w') as f:
    #     dset = f.create_dataset("default", data = keep_data)



    file = open(out_folder_name+'/compiled_data_'+str(each_file_idx)+'.pickle', 'wb')
    pickle.dump(keep_data, file)

    file.close()
