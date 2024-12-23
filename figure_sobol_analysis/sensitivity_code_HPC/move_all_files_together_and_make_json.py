
import pickle
import os
import glob
import natsort 
from copy import deepcopy as dcp
import json
import sys

import shutil
import numpy
# folder_name = sys.argv[1]


folder_name = '/home/wuy2/2023_1009_exc_mod4/'
folder_name_list = natsort.natsorted(  glob.glob(folder_name+'/*Out*'))

for each_folder in folder_name_list :
    temp_name = each_folder.split('/')[-1]
    if os.path.exists(each_folder+"/all_sensitivity_v2.pickle"):

        shutil.copyfile(each_folder+"/all_sensitivity_v2.pickle", temp_name+"_all_sensitivity_v2.pickle")
        whatever_data=pickle.load( open( temp_name+"_all_sensitivity_v2.pickle", "rb" ) )
        for each_feature in whatever_data: 
            for each_analysis in whatever_data[each_feature]:
                for each_data in each_analysis:
                    # if type(each_analysis[each_data]) is 'numpy.ndarray':
                    if isinstance(each_analysis[each_data], numpy.ndarray):
                        each_analysis[each_data] = each_analysis[each_data].tolist()

            
        out_file = open( temp_name+"_all_sensitivity_v2.json", "w")
        json.dump(whatever_data, out_file, indent = 2)
        out_file.close()



    