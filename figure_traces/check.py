import os
import json
from natsort import natsorted

def check_responses_pre(folder_name, keyword):
    # List all files matching the keyword and sort them naturally
    aa_list = natsorted([f for f in os.listdir(folder_name) if keyword in f and f.endswith('responses.json')])

    # Read the last file from the sorted list
    with open(os.path.join(folder_name, aa_list[-1]), 'r') as fid:
        val = json.load(fid)

    # List all protocol files and sort them naturally
    bb_list = natsorted([f for f in os.listdir(folder_name) if 'prot' in f and keyword in f and f.endswith('.json')])

    # Read the first protocol file from the sorted list
    with open(os.path.join(folder_name, bb_list[0]), 'r') as fid:
        val_2 = json.load(fid)

    return val, val_2

# Example usage:
# val, val_2 = check_responses_pre('your/folder/path', 'your_keyword')


def check_responses_pre_pre(folder_name):
    # Find all files matching the pattern '*responses.json'
    aa_list = natsorted([f for f in os.listdir(folder_name) if f.endswith('responses.json')])
    
    # Read the last response file
    with open(os.path.join(folder_name, aa_list[-1]), 'r') as fid:
        str_data = fid.read()
    
    val = json.loads(str_data)

    # Find all files matching the pattern '*prot*<keyword>*.json'
    bb_list = natsorted([f for f in os.listdir(folder_name) if 'prot' in f and f.endswith('.json')])
    
    # Read the first prot file
    with open(os.path.join(folder_name, bb_list[0]), 'r') as fid:
        str_data = fid.read()
    
    val_2 = json.loads(str_data)

    # Extracting ID number
    id_number = folder_name.split('_')[-4]
    id_number = id_number.split('/')[-1]

    # Find all matching json files in the specified directory
    cc_list = natsorted([f for f in os.listdir('./exp_trace') if id_number in f and f.endswith('.json')])

    # Read the first matching file
    with open(os.path.join('./exp_trace', cc_list[0]), 'r') as fid:
        str_data = fid.read()
    
    teaces_and_features = json.loads(str_data)

    return teaces_and_features