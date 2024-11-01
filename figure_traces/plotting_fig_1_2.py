import os
import json
import numpy as np
import matplotlib.pyplot as plt
from natsort import natsorted
from check import check_responses_pre
from check import check_responses_pre_pre

# Define folder names and color table
folder_names = [
    'ITL23__595572609_seed_1_Outputs/',
    'ITL35__653040833_seed_1_Outputs/',
    'ITL46__650076115_seed_1_Outputs/',
    'PVALB__689331391_seed_1_Outputs/',
    'SST__737553506_seed_1_Outputs/',
    'VIP__685806972_seed_1_Outputs/',
    'LAMP5PAX6Other__653810044_seed_1_Outputs/'
]

color_table = np.array([
    [0, 0.5, 0.5],
    [0, 0.8, 0.8],
    [0.1, 1.0, 1.0],
    [0.9, 0.1, 0.1],
    [0.1, 0.9, 0.1],
    [0.1, 0.1, 0.9],
    [0.95, 0.95, 0.2],
    [0.75, 0.75, 0.75],
    [0.75, 0.75, 0.75]
])

cell_type_list = [
    'ITL23',
    'ITL35',
    'ITL46',
    'PVALB',
    'SST',
    'VIP',
    'LAMP5PAX6Other'
]

Shifting_right = 1600
Shifting_down = [-150, 0, 120, 160]
ll = [6, 6, 6, 6, 6, 6, 6]

plt.figure()
plt.axis('off')

spike_trim = [-1.0, 1.5]
zoom = 200

# Iterate through each folder
for kk in range(len(folder_names)):
    ccc = color_table[kk, :]
    ccc2 = 1 - ((1 - ccc) * 0.3)

    # Load responses
    val, val_2 = check_responses_pre(folder_names[kk], 'ge_1')
    teaces_and_features = check_responses_pre_pre(folder_names[kk])

    field_name_1 = list(val[-1]['responses'].keys())
    field_name_1_x = [fn.replace('_AIS', '_som').split('.')[0] for fn in field_name_1]
    field_name_2 = list(teaces_and_features.keys())

    # print(field_name_1)
    # print(field_name_1_x)
    # print(field_name_2)
    ampp = np.array([val_2[field_name_1_x[jj]]['stimuli'][0]['amp'] for jj in range(len(field_name_1))])

    jj1 = np.argmax(ampp)
    jj2 = np.argmin(ampp)

    for jj in [jj1, jj2]:
        data_t = val[ll[kk]]['responses'][field_name_1[jj]]['time']
        data_v = val[ll[kk]]['responses'][field_name_1[jj]]['voltage']

        # print(data_t)
        data_t = np.array(data_t)
        data_v = np.array(data_v)

        asd = (data_t > val_2[field_name_1_x[jj]]['stimuli'][0]['delay'] - 200) & \
              (data_t < val_2[field_name_1_x[jj]]['stimuli'][0]['delay'] + 1300)
        asd = [index for index, value in enumerate(asd) if value]
        data_t = np.array([data_t[i] for i in asd])
        data_v = np.array([data_v[i] for i in asd])

        data_v = data_v - (data_v[0] + Shifting_down[1])
        data_t = data_t - (val_2[field_name_1_x[jj]]['stimuli'][0]['delay'] - 200)
        data_t = data_t + (kk) * Shifting_right

        plt.plot(data_t, data_v, linewidth=1, color=ccc)

        fouund_yet = False
        for ii in range(len(field_name_2)):
            try:
                if (round(teaces_and_features[field_name_2[ii]]['00_custom_extra_current_mean'], 2) ==
                    round(val_2[field_name_1_x[jj]]['stimuli'][0]['amp'], 2) * 1000):
                    data_t = teaces_and_features[field_name_2[ii]]['time']
                    data_v = teaces_and_features[field_name_2[ii]]['voltage']
                    fouund_yet = True
            except KeyError:
                continue

        for ii in range(len(field_name_2)):
            try:
                if (round(teaces_and_features[field_name_2[ii]]['00_custom_extra_current_mean'], 2) ==
                    round(val_2[field_name_1_x[jj]]['stimuli'][0]['amp'], 2)):
                    data_t = teaces_and_features[field_name_2[ii]]['time']
                    data_v = teaces_and_features[field_name_2[ii]]['voltage']
                    fouund_yet = True
            except KeyError:
                continue

        data_t = np.array(data_t)
        data_v = np.array(data_v)
        asd = (data_t > val_2[field_name_1_x[jj]]['stimuli'][0]['delay'] - 200) & \
              (data_t < val_2[field_name_1_x[jj]]['stimuli'][0]['delay'] + 1300)

        asd = [index for index, value in enumerate(asd) if value]
        data_t = np.array([data_t[i] for i in asd])
        data_v = np.array([data_v[i] for i in asd])

        # print(val_2[field_name_1_x[jj]]['stimuli'][0]['delay'] )
        # data_t = data_t[asd]
        # data_v = data_v[asd]
        
        if not len(data_v) == 0:
            data_v -= data_v[0]
        data_t -= (val_2[field_name_1_x[jj]]['stimuli'][0]['delay'] - 200)
        data_v -= Shifting_down[0]
        data_t += (kk) * Shifting_right

        plt.plot(data_t, data_v, linewidth=1, color=ccc)

    jj = jj1
    fouund_yet = False
    for ii in range(len(field_name_2)):
        try:
            if (round(teaces_and_features[field_name_2[ii]]['00_custom_extra_current_mean'], 2) ==
                round(val_2[field_name_1_x[jj]]['stimuli'][0]['amp'], 2) * 1000):
                data_t = teaces_and_features[field_name_2[ii]]['time']
                data_v = teaces_and_features[field_name_2[ii]]['voltage']
                t_offset = (teaces_and_features[field_name_2[ii]]['time_to_first_spike'][0] +
                            teaces_and_features[field_name_2[ii]]['00_custom_extra_stim_start'])
                fouund_yet = True
        except KeyError:
            continue

    for ii in range(len(field_name_2)):
        try:
            if (round(teaces_and_features[field_name_2[ii]]['00_custom_extra_current_mean'], 2) ==
                round(val_2[field_name_1_x[jj]]['stimuli'][0]['amp'], 2)):
                data_t = teaces_and_features[field_name_2[ii]]['time']
                data_v = teaces_and_features[field_name_2[ii]]['voltage']
                t_offset = (teaces_and_features[field_name_2[ii]]['time_to_first_spike'][0] +
                            teaces_and_features[field_name_2[ii]]['00_custom_extra_stim_start'])
                fouund_yet = True
        except KeyError:
            continue
    data_t = np.array(data_t)
    data_v = np.array(data_v)
    
    asd = (data_t > t_offset + spike_trim[0]) & (data_t < t_offset + spike_trim[1])
    # data_t = data_t[asd]
    # data_v = data_v[asd]
    asd = [index for index, value in enumerate(asd) if value]
    data_t = np.array([data_t[i] for i in asd])
    data_v = np.array([data_v[i] for i in asd])

    v_offset = data_v[data_t > t_offset]

    if not len(data_v) == 0:
        data_v -= data_v[0]
    data_t -= data_t[0]
    data_v -= Shifting_down[2]
    data_t = data_t * zoom + (kk) * Shifting_right

    plt.plot(data_t, data_v, linewidth=1, color=ccc2)

    data_t = val[ll[kk]]['responses'][field_name_1[jj]]['time']
    data_v = val[ll[kk]]['responses'][field_name_1[jj]]['voltage']

    # print(list(val[ll[kk]]['values']))
    # print(field_name_1_x[jj] + '_soma_time_to_first_spike')
    t_offset = val[ll[kk]]['values'][field_name_1_x[jj] + '.soma.time_to_first_spike'] + \
               teaces_and_features[field_name_1_x[jj]]['00_custom_extra_stim_start']


    data_t = np.array(data_t)
    data_v = np.array(data_v)

    # print(t_offset)

    asd = (data_t > t_offset + spike_trim[0]) & (data_t < t_offset + spike_trim[1])
    asd = [index for index, value in enumerate(asd) if value]
    # print(asd)


    data_t = np.array([data_t[i] for i in asd])
    data_v = np.array([data_v[i] for i in asd])
    v_offset = data_v[data_t > t_offset]

    # data_t = data_t[asd]
    # data_v = data_v[asd]
    data_v -= data_v[0]
    data_t -= data_t[0]

    data_v -= Shifting_down[2]
    data_t = data_t * zoom + (kk) * Shifting_right

    plt.plot(data_t, data_v, linewidth=1, color=ccc)









    fname = os.path.join(folder_names[kk], '*1_iteration_1_hof_responses_ir_curve.json')
    fname = natsorted([f for f in os.listdir(folder_names[kk]) if f.endswith('1_iteration_1_hof_responses_ir_curve.json')])[0]
    with open(os.path.join(folder_names[kk], fname), 'r') as fid:
        val = json.load(fid)


    spike_count_table_fn = [key for key in val[0]['values'] if 'count' in key]

    # Sort spike count table fields naturally
    spike_count_table_fn = natsorted(spike_count_table_fn)
    spike_count_table = []

    # Populate spike_count_table
    for nn in range(len(val)):
        inner_list = []
        for mm in range(len(spike_count_table_fn)):
            inner_list.append(val[nn]['values'][spike_count_table_fn[mm]])
        spike_count_table.append(np.array(inner_list).T)

    spike_count_table = np.vstack(spike_count_table)

    data_i = np.arange(0, (spike_count_table.shape[1] ) * 0.01, 0.01)
    data_f = spike_count_table[ ll[kk],:]


    spike_count_table_i = []
    spike_count_table_f = []

    # Assuming `field_name_2` is a list of strings
    for nn in range(len(field_name_2)):
        spike_count_table_i.append(teaces_and_features[field_name_2[nn]]['00_custom_extra_current_mean'])
        spike_count_table_f.append(teaces_and_features[field_name_2[nn]]['Spikecount'])
    
    spike_count_table_i = np.array(spike_count_table_i)
    spike_count_table_f = np.array(spike_count_table_f)

    spike_count_table_i = np.squeeze(spike_count_table_i) 
    spike_count_table_f = np.squeeze(spike_count_table_f) 


    # Normalize spike_count_table_i
    if np.max(spike_count_table_i) > 2:
        spike_count_table_i = spike_count_table_i / 1000

    # Sort spike count tables by spike_count_table_i
    inddx = np.argsort(spike_count_table_i)
    spike_count_table_i = spike_count_table_i[inddx]
    spike_count_table_f = spike_count_table_f[inddx]

    # Adjusting data ranges
    min_i = np.min(np.concatenate([data_i, spike_count_table_i]))
    max_i = np.max(spike_count_table_i)

    data_f = np.array(data_f)
    data_i = np.array(data_i)


    data_f = data_f[data_i <= max_i]
    data_i = data_i[data_i <= max_i]

    max_f = np.max(np.concatenate([data_f, spike_count_table_f]))

    # Normalize data
    data_f = (data_f / max_f) * 100
    data_i = data_i - min_i
    spike_count_table_f = (spike_count_table_f / max_f) * 100
    spike_count_table_i = spike_count_table_i - min_i

    # Add starting point (0)
    data_f = np.concatenate([[0], data_f])
    data_i = np.concatenate([[0], data_i])

    data_f -= Shifting_down[3]
    data_i = data_i * 4000 + (kk ) * Shifting_right

    spike_count_table_f -= Shifting_down[3]
    spike_count_table_i = spike_count_table_i * 4000 + (kk ) * Shifting_right

    # Custom adjustments for kk == 1
    if kk == 1:
        data_i -= 200
        spike_count_table_i -= 200

    # Plotting
    plt.plot(spike_count_table_i, spike_count_table_f, linewidth=1, color=ccc2)
    plt.scatter(spike_count_table_i, spike_count_table_f, s=30, color=ccc2, marker='x')
    plt.plot(data_i, data_f, linewidth=1, color=ccc)






output_filename = f'plot.png'

plt.savefig(output_filename, format='png', dpi=300)
plt.close()

print(f'Plot saved as {output_filename}')
