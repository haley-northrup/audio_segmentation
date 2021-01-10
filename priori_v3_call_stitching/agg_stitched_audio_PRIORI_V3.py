import os 
import pandas as pd 
import argparse

from IPython import embed 

#Parse Arguments 
#**********************
parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', type=str, help="Path to directory with individual output feature files")
parser.add_argument('--output_dir', type=str, help="Path to directory to output combined feature files to.")
args = parser.parse_args()

#Aggregate individual files in input_dir 
#***********************************
files = os.listdir(args.input_dir) 
df_full = pd.DataFrame()
for f in files: 
    df = pd.read_csv(os.path.join(args.input_dir, f))
    df_full = df_full.append(df, sort=True)   
embed()
exit() 

        #Reorder columns 
        #cols = ['call_id', 'file_id', 'wav_number', 'call_wav_count', 'record_id', 'is_assessment_call', \
        #'length_seconds', 'size_bytes', 'file_path', 'prechter_file_path']
        #if call_part_df.shape[1] == len(cols):
        #    call_part_df = call_part_df[cols]

        #call_part_df.to_csv(os.path.join(output_meta, 'call_audio_metadata_20210108.csv'), index=False) 
        #stitched_call_df.to_csv(os.path.join(output_meta, 'call_audio_stitched_20210108.csv'), index=False)

        
        #Track metadata 
        #call_part_df.loc[cidx, 'call_wav_count'] = int(cidx.sum())

#stitched_call_df = pd.DataFrame(columns=['call_id', 'call_wav_count', 'record_id', 'is_assessment_call', 'length_seconds', 'file_path'])
        #row += 1
#stitched call metadata 
#stitched_call_df.loc[row, 'call_id'] = c
#stitched_call_df.loc[row, 'call_wav_count'] = int(cidx.sum())
        #stitched_call_df.loc[row, 'record_id'] = call_df['record_id'].values[0]
        #stitched_call_df.loc[row, 'is_assessment_call'] = call_df['is_assessment_call'].values[0]
        #stitched_call_df.loc[row, 'length_seconds'] = call_df['length_seconds'].sum() 
        #stitched_call_df.loc[row, 'file_path'] = stitched_path

#Add metadata based on level 
if args.level == 'day': 
        df_full['day_id'] = df_full.index 
        sub_ids = df_full['day_id'].apply(lambda x: x.split('_')[0]).values 
        dates = df_full['day_id'].apply(lambda x: x.split('_')[1]).values
        df_full.insert(loc=0, column='subject_id', value=sub_ids)
        df_full.insert(loc=1, column='date', value=dates) 
        df_full = df_full.drop(['day_id'], axis=1) 
elif args.level == 'call':
        df_full.insert(loc=0, column='call_id', value=df_full.index.values) 

#Save aggregate file 
df_full.to_csv(os.path.join(args.output_dir, args.level + '_' + args.call_type + '_rhythm.csv'), index=False) 

