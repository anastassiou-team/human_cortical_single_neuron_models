



cell_name = 'ITL23__689309060_stage_1_seed_1_hof_7_Layer3_Exc L2 LAMP5 LTK'

json_fil_name = './Required_Files/json/' + cell_name + '.json'
swc_file_name = './Required_Files/swc/' + cell_name.split('_stage')[0] +'_transformed.swc'

simulation_location = './Simulation_t/'




# basic
dt = 0.02
dL = 20
simulation_duration = 5000.0

# iclamp unit in ms mv
iclamp_delay = 1000
iclamp_duration = 1000
iclamp_begine_amp = 0.05


model_processing = 'csmc_allactive_noaxon'
# model_processing='aibs_allactive'

mod_file_folder_name = './Required_Files/modfiles'


import os
try:
    os.system("rm -r " + simulation_location)  
except:
    pass


from bmtk.builder.networks import NetworkBuilder
from bmtk.utils.sim_setup import build_env_bionet
import shutil
import cell_functions #Imports csmc_allactive_noaxon

# Create network
net = NetworkBuilder('single_neuron')
net.add_nodes(cell_name='Cell',
              potental='exc',
              model_type='biophysical',
              model_template='ctdb:Biophys1.hoc',
              model_processing=model_processing,
              dynamics_params='CellJ.json',
              morphology='Cell.swc')

net.build()
net.save_nodes(output_dir=simulation_location+'Model')

build_env_bionet(
    base_dir= simulation_location,
    config_file='config.json',
    network_dir=simulation_location+'Model',
    tstop=simulation_duration,
    dt=dt,
    dL=dL,
    include_examples=False,
    compile_mechanisms=False
)

# Copy required files
shutil.copyfile( json_fil_name, simulation_location + 'components/biophysical_neuron_models/CellJ.json')
shutil.copyfile( swc_file_name, simulation_location + 'components/morphologies/Cell.swc')
shutil.copytree('./Required_Files/modfiles', simulation_location + 'components/mechanisms/modfiles')



from subprocess import call
import os

status=call("nrnivmodl modfiles",cwd = simulation_location + "components/mechanisms",shell=True)
if status:
    print ("NEURON ERROR")
else:
    print ("Compilation done!")




from bmtk.simulator import bionet
import json


with open(simulation_location +'simulation_config.json') as f:
    sim_conf = json.load(f)


sim_conf.update( 
    {
    "reports": {
    "v_report_soma": {
      "variable_name": "v",
      "cells": "all",
      "module": "membrane_report",
      "sections": "soma"
    },
    "v_report_all": {
      "variable_name": "v",
      "cells": "all",
      "module": "membrane_report",
      "sections": "all"
            }
        }
    }
)

# constant iclamp
sim_conf.update(
    {
    "inputs": {
    "current_clamp": {
      "input_type": "current_clamp",
      "module": "IClamp",
      "node_set": "all",
      "gids": "all",
      "amp": iclamp_begine_amp,
      "delay": iclamp_delay,
      "duration": iclamp_duration
    }
    }
    }
)


with open(simulation_location +'simulation_config.json', "w") as outfile:
    outfile.write(json.dumps(sim_conf, indent=4))


conf = bionet.Config.from_json(simulation_location +'config.json')
conf.build_env()

net = bionet.BioNetwork.from_config(conf)
sim = bionet.BioSimulator.from_config(conf, network=net)


# cell = sim.net.get_cell_gid(0)                       # Fetch desired cell


sim.run()



# import h5py


# with h5py.File( simulation_location + 'output/v_report_all.h5', "r") as f:
#     data = f['report']['single_neuron']['data'][()]
#     swc_ids_beg = f['report']['single_neuron']['mapping']['swc_ids_beg'][()] 
#     swc_ids_end = f['report']['single_neuron']['mapping']['swc_ids_end'][()]

# f.close()


# import numpy as np
# from scipy.signal import argrelextrema
# peaksss_loca = argrelextrema(data, np.greater)
# peaksss =  data[peaksss_loca]
# lowww_loca = argrelextrema(data, np.less)
# lowww =  data[lowww_loca]


# hf = h5py.File(simulation_location + 'output/amplitude_envelope.h5', 'w')
# hf.create_dataset('peaksss', data=peaksss)
# hf.create_dataset('peaksss_loca', data=peaksss_loca)
# hf.create_dataset('lowww', data=lowww)
# hf.create_dataset('lowww_loca', data=lowww_loca)
# hf.create_dataset('/report/single_neuron/mapping/swc_ids_beg', data=swc_ids_beg)
# hf.create_dataset('/report/single_neuron/mapping/swc_ids_end', data=swc_ids_end)


# hf.close()
