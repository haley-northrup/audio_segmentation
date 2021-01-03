''' Compare segmentation statistics across methods 

''' 

import os 
import pandas as pd 
import numpy as np 
from IPython import embed 
import matplotlib.pyplot as plt 


# SET UP 
#*************

outdir = '.'

method1 = 'soheil_VAD'
method2 = 'microsoft_azure' 

method1_path = './soheil_VAD/call_seg_metadata.csv'
method2_path = './microsoft_azure/call_seg_metadata.csv'

priori_emotion_subjects = [1250001, 1510001, 1517001, 1639001, 1786001, 1815001, 1850001,
       2140001, 2218001, 2368001, 2434001, 2503001, 2636001, 2637001,
       2828001, 2914001, 2923001, 3099001, 3413001]

#Load Data 
call_df1 = pd.read_csv(method1_path) 
call_df2 = pd.read_csv(method2_path) 

#Call, Segment Analysis 
#**************************************
#**************************************

call_df1.loc[:, 'length_no_spk_min'] = call_df1['length_no_spk'].values*10**-3/60 #ms to min
call_df2.loc[:, 'length_no_spk_min'] = call_df2['length_no_spk'].values*10**-3/60 #ms to min

#GET CALLS WITH NON-Zero DURATION 
valid_call_df1 = call_df1.loc[call_df1['length_no_spk'] > 0, :] 
valid_call_df2 = call_df2.loc[call_df2['length_no_spk'] > 0, :] 

#Set of all call_ids
all_call_set = set(valid_call_df1['call_id']) 

#WHAT CALLS ARE MISSING SPEECH??
call_df1_wo_segs = valid_call_df1.loc[valid_call_df1['segment_count'] == 0, :]
call_df2_wo_segs = valid_call_df2.loc[valid_call_df2['segment_count'] == 0, :]
calls_wo_segs1 = set(call_df1_wo_segs['call_id'])
calls_wo_segs2 = set(call_df2_wo_segs['call_id'])

#Number of Calls Missing Segments
print('Number of calls without segments')
print(method1 + ': ' + str(call_df1_wo_segs.shape[0]))
print(method2 + ': ' + str(call_df2_wo_segs.shape[0]))

#Difference 
print('Difference: ' + str(np.abs(call_df1_wo_segs.shape[0] - call_df2_wo_segs.shape[0])))

#Set Difference in Call_IDs
set_diff12 = calls_wo_segs1.difference(calls_wo_segs2)
set_diff21 = calls_wo_segs2.difference(calls_wo_segs1)
set_same = calls_wo_segs1.intersection(calls_wo_segs2)
print('Set 1 difference Set 2: ' + str(len(set_diff12)))
print('Set same: ' + str(len(set_same))) 
print('Set 2 difference Set 1: ' + str(len(set_diff21)))

#Calls that have segments identified by both methods 
calls_with_segs = all_call_set.difference(set_same, set_diff12, set_diff21)
calls_wo_segs = set_same 

#WHAT ARE THE CHARACTERISTICS OF THE CALLS ???
#Are these calls shorter?
calls_with_segs_df = valid_call_df1.loc[valid_call_df1['call_id'].isin(calls_with_segs), :]
calls_wo_segs_df = valid_call_df1.loc[valid_call_df1['call_id'].isin(calls_wo_segs), :]

print(calls_with_segs_df['length_no_spk_min'].describe())
print(calls_wo_segs_df['length_no_spk_min'].describe())

#histogram 
plt.figure()
calls_wo_segs_df['length_no_spk_min'].hist(bins=100)
calls_with_segs_df['length_no_spk_min'].hist(bins=100)
plt.yscale('log')
plt.xlim([0, 90])
plt.ylabel('log(count) (wo seg = blue, with seg = orange)')
plt.xlabel('Call Length (minutes)')
plt.legend()
plt.title('Call Length No Speaker Phone')
plt.savefig(os.path.join(outdir, 'call_len_comp_hist.png')) 

#GET CALLS TO INVESTIGATE 
#************************************
#************************************

#DIFFERENCE DATAFRAMES 
calls_wo_segs_12_df = valid_call_df1.loc[valid_call_df1['call_id'].isin(set_diff12), :]
calls_wo_segs_21_df = valid_call_df1.loc[valid_call_df1['call_id'].isin(set_diff21), :]

#GET ONLY PRIORI EMOTION SUBJECTS 
calls_wo_segs_12_df = calls_wo_segs_12_df.loc[calls_wo_segs_12_df['subject_id'].isin(set(priori_emotion_subjects)), :]
calls_wo_segs_21_df = calls_wo_segs_21_df.loc[calls_wo_segs_21_df['subject_id'].isin(set(priori_emotion_subjects)), :]

#Get longest calls in set12, set21  
calls_wo_segs_12_df = calls_wo_segs_12_df.sort_values(by=['length_no_spk_min'], ascending=False)
calls_wo_segs_21_df = calls_wo_segs_21_df.sort_values(by=['length_no_spk_min'], ascending=False)

longest_calls_12 = calls_wo_segs_12_df.iloc[0:4]['call_id']
longest_calls_21 = calls_wo_segs_21_df.iloc[0:4]['call_id']
print(longest_calls_12)
print(longest_calls_21) 


#Get random calls in set21, set12 
ints = np.random.randint(len(set_diff12), size=4)
set_diff12_list = np.array(list(set_diff12))
print('random calls from set12 (VAD no seg, MA seg)')
for s in ints:
    print(set_diff12_list[s])

ints = np.random.randint(len(set_diff21), size=4)
set_diff21_list = np.array(list(set_diff21))
print('random calls from set21 (VAD seg, MA no seg)')
for s in ints:
    print(set_diff21_list[s])
