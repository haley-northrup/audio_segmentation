''' Get Segmentation Statistics 

Segments and Calls 
counts, lengths, ratios etc. 

#TODO is_assessment by call??
#TODO word counts by segment??

Segment word counts 
    Less than 5 words?
    How many one word segments? 
Assessment Days
    How many assessment days with personal calls?

''' 

import os 
import pandas as pd 
import numpy as np 
from IPython import embed 
import matplotlib.pyplot as plt 


# SET UP 
#*************

#outdir = './microsoft_azure'
outdir = './soheil_VAD'

call_meta_path = '/nfs/turbo/McInnisLab/priori_v1_data/tables/call_audio.csv'
device_meta_path = '/nfs/turbo/McInnisLab/priori_v1_data/tables/device.csv'
seg_meta_path = '/nfs/turbo/McInnisLab/priori_v1_data/collections/emotion_preds.csv'
#seg_meta_path = '/nfs/turbo/McInnisLab/PRIORI_v1_Microsoft_Azure/PRIORI-v1-Microsoft-segments/priori_v1_ma_segments.csv' 

#Load Data 
seg_df = pd.read_csv(seg_meta_path) 
call_df = pd.read_csv(call_meta_path) 
dev_df = pd.read_csv(device_meta_path) 

#Update Columns Names
if 'segment_length' not in set(seg_df.columns): 
    seg_df['segment_length'] = seg_df['duration_ms'] * 10**-3 #convert ms to sec 

#Format Dates
call_df['datetime'] = pd.to_datetime(call_df['datetime'])
call_df['date'] = call_df['datetime'].dt.date 

#Add device type to call_df 
dev_df['imei'] = dev_df['imei'].apply(str) 
dev_dict = dev_df.set_index('imei').to_dict()
call_df['imei'] = call_df['imei'].apply(str) 
call_df['device'] = call_df['imei'].map(dev_dict['model']) 

# Overall Statistics 
#***************************************

#print(call_df.columns) 
#print(seg_df.columns) 

#total number of calls 
print('Total Number of Calls: ' + str(call_df.shape[0]))
temp = call_df.loc[call_df['length_no_spk'] > 0, :] 
print('Calls with non-zero duration: ' + str(temp.shape[0]))

#total number of segments 
print('Total Number of Segments: ' + str(seg_df.shape[0]))

#histogram of segment durations 
print(seg_df['segment_length'].describe())
plt.figure()
seg_df['segment_length'].hist(bins=50)
plt.yscale('log')
plt.ylabel('log(count)')
plt.xlabel('Duration (seconds)')
plt.title('Segment Duration')
plt.savefig(os.path.join(outdir, 'seg_len_hist.png')) 

#Number of segments by phone type 
print('Total Segments by device:')
for d in seg_df['device'].unique():
    ct = (seg_df['device'] == d).sum()
    print(d + ': ' + str(ct))

'''
# Segment Statistics by Call 
#**************************************
#(call_duration (milliseconds) 'length_no_spk')
call_df['length_no_spk_sec'] = call_df['length_no_spk'] * 10**-3  #covert ms to sec 

for c in call_df['call_id'].unique():

    call_segs = seg_df.loc[seg_df['call_id'] == c, :]
    cidx = call_df['call_id'] == c

    #segment count 
    call_df.loc[cidx, 'segment_count'] = call_segs.shape[0]
     
    if call_segs.shape[0] == 0:
        continue 

    #total segment duration (seconds) 
    call_df.loc[cidx, 'total_seg_dur_sec'] = call_segs['segment_length'].sum() 
    #segment duration stats for call (min, max, mean)
    call_df.loc[cidx, 'seg_dur_sec_min'] = call_segs['segment_length'].min() 
    call_df.loc[cidx, 'seg_dur_sec_max'] = call_segs['segment_length'].max() 
    call_df.loc[cidx, 'seg_dur_sec_mean'] = call_segs['segment_length'].mean() 
    call_df.loc[cidx, 'seg_dur_sec_median'] = call_segs['segment_length'].median() 

    #ratio of segment duration to call duration 
    call_df.loc[cidx, 'seg_call_dur_ratio'] = call_df.loc[cidx, 'total_seg_dur_sec']/call_df.loc[cidx,'length_no_spk_sec']


#SAVE CALL SEGMENT METADATA 
call_df.to_csv(os.path.join(outdir, 'call_df_temp_v2_20210101.csv'), index=False) 
'''

call_df = pd.read_csv(os.path.join(outdir, 'call_df_temp_v2_20210101.csv')) 


#Call, Segment Analysis 
#**************************************
#**************************************

#GET CALLS WITH NON-Zero DURATION 
call_df.loc[:, 'total_seg_dur_min'] = call_df['total_seg_dur_sec'].values/60 
valid_call_df = call_df.loc[call_df['length_no_spk'] > 0, :] 

#Segment Count
#***********************  
#What fraction of valid calls have no segments?
calls_wo_segs = (valid_call_df['segment_count'] == 0).sum()/valid_call_df.shape[0] 
print('Frac calls without segments: ' + str(calls_wo_segs))
print('Frac calls with segments: ' + str(1 - calls_wo_segs))

print(valid_call_df['segment_count'].describe())
print(valid_call_df.loc[valid_call_df['segment_count']>0, 'segment_count'].describe())
#histogram 
plt.figure()
valid_call_df['segment_count'].hist(bins=100)
plt.yscale('log')
plt.ylabel('log(count)')
plt.xlabel('Segment count in each call')
plt.title('Segment Counts')
plt.savefig(os.path.join(outdir, 'call_seg_ct_hist.png')) 

#What fraction of calls by phone type have more than 0 segments?
print('Fraction of calls without segments by device:')
for d in valid_call_df['device'].unique():
    #device indices
    didx  = valid_call_df['device'] == d
    #count of calls without segments for device d 
    ct = (didx & valid_call_df['seg_call_dur_ratio'].isna()).sum() 
    #total calls for device d 
    tot = (call_df['device'] == d).sum()
    #percent 
    print(d + ': ' + str(ct/tot ))

#Total segment duration 
#*******************************
print(valid_call_df['total_seg_dur_min'].describe())
print(valid_call_df['total_seg_dur_sec'].describe())
#histogram 
plt.figure()
valid_call_df['total_seg_dur_min'].hist(bins=100)
plt.yscale('log')
plt.ylabel('log(count)')
plt.xlabel('Total Segment Duration in each call (minutes)')
plt.title('Total Segment Duration')
plt.savefig(os.path.join(outdir, 'call_seg_dur_hist.png'))

