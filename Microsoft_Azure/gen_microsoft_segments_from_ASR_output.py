import os
import argparse
import pandas as pd
import numpy as np
import pickle 
from pydub import AudioSegment

from IPython import embed 

"""
Script for generating segments from Microsoft Azure ASR output 

segment metdata csv file  
/wav 
/word_timing 

"""

class GenMicrosoftSegments:
    def __init__(self, recognition_result_files, args):
        """
        :param recognition_result_files: list of paths to files containing recognition results from Microsoft
                                         speech-to-text model
        """
        self.recognition_result_files = recognition_result_files
        self.segment_dict = self._collect_segment_info()
        self.call_meta_df = pd.read_csv(args.call_metadata) 
        if 'record_id' in set(list(self.call_meta_df.columns)):
            self.call_meta_df['subject_id'] = self.call_meta_df['record_id']
            self.call_meta_df['is_assessment'] = self.call_meta_df['is_assessment_call']

    def _collect_segment_info(self):
        """
        Collect all segment timing information for each audio file 
        :return: segment_dict: dict mapping ids 'audio_file_id' to segment timing info 
        """
        segment_dict = dict()
        df_list = []
        # collect results from all files
        for file_path in self.recognition_result_files:
            df = pd.read_csv(file_path)
            df_list.append(df)
        combined_df = pd.concat(df_list)
        if 'feature_id' in combined_df.columns:
            combined_df.set_index('feature_id', inplace=True)
        else:
            combined_df.set_index('audio_file_id', inplace=True)
        sort_column = "order" if "order" in combined_df.columns else "segment_number"
        for idx in set(combined_df.index.values):
            #sort entries in dataframe            
            if len(combined_df.loc[idx].shape) == 1:
                sorted_entries = pd.DataFrame(columns=combined_df.columns)
                sorted_entries.loc[0] = combined_df.loc[idx, :]
            else:
                sorted_entries = combined_df.loc[idx].sort_values(sort_column)
            segment_dict[idx] = sorted_entries #.drop(['word_timing', 'confidence'], axis=1)  
        return segment_dict

    def generate_segments(self, output_dir, wav_dir):
        """
        Generate and save segment .wav files and metadata based on segment timing (segment_dict)

        :param output_dir: Path to output directory
        :param wav_dir: Path to directory with .wav files used to generate segments  
        """
        #make output directory 
        seg_outdir = os.path.join(output_dir, 'wav') 
        if not os.path.exists(seg_outdir): 
            os.makedirs(seg_outdir) 

        seg_meta_df = pd.DataFrame()
        ct = 0
        #read segment dict #iterate over calls
        for call_id, seg_df in self.segment_dict.items():
            print('Call_id: ' + str(call_id))
            cidx = self.call_meta_df['call_id'] == call_id  

            for s in seg_df.segment_number: #iterate over segments 
                sidx = seg_df['segment_number'] == s
            
                duration_ms = seg_df.loc[sidx, 'duration'].values[0] * 10**-4 #convert from (100 ns units) to ms 
                start_ms = seg_df.loc[sidx, 'offset'].values[0] * 10**-4 #convert from (100 ns units) to ms 
                end_ms = start_ms + duration_ms 

                #load call .wav file #call_id is name of wav file (<call_id>.wav)
                wave_file = os.path.join(wav_dir, str(call_id) + '.wav')
                #print(start_ms)
                #print(end_ms) 
                orig_audio = AudioSegment.from_wav(wave_file)
                segment_audio = orig_audio[int(np.floor(start_ms)):int(np.ceil(end_ms))]
                                
                #Segment_id "ma<int>" (ma = Microsoft Azure) 
                seg_id = 'ma' + str(ct) 
                segment_audio.export(os.path.join(seg_outdir, seg_id + '.wav'), format="wav")

                #Save segment metadata 
                seg_df.loc[sidx, 'segment_id'] = seg_id 
                seg_meta_df.loc[ct, 'segment_id'] =  seg_id
                seg_meta_df.loc[ct, 'call_id'] = call_id
                seg_meta_df.loc[ct, 'segment_number'] = int(s) #John/Soheil called "segment_order" 
                seg_meta_df.loc[ct, 'subject_id'] = int(self.call_meta_df.loc[cidx, 'subject_id'].values[0])
                #TODO not datetime information for priori-v3 (2021-01-19) 
                #seg_meta_df.loc[ct, 'call_datetime'] = self.call_meta_df.loc[cidx, 'date_time'].values[0]
                seg_meta_df.loc[ct, 'is_assessment'] = self.call_meta_df.loc[cidx, 'is_assessment'].values[0]
                #TODO not datetime information for priori-v3 (2021-01-19) 
                #seg_meta_df.loc[ct, 'device'] = self.call_meta_df.loc[cidx, 'device'].values[0]
                seg_meta_df.loc[ct, 'duration_ms'] = int(duration_ms) #John/Soheil call "segment_length"
                seg_meta_df.loc[ct, 'start_ms'] = int(start_ms) 
                seg_meta_df.loc[ct, 'end_ms'] = int(end_ms) 
                seg_meta_df.loc[ct, 'confidence'] = seg_df.loc[sidx, 'confidence'].values[0]
                seg_meta_df.loc[ct, 'ma_transcription'] = seg_df.loc[sidx, 'text'].values[0] 
                ct = ct + 1  

            #update segment_dict with segment_ids 
            self.segment_dict[call_id] = seg_df    
        #Convert columns to integers (NOTE not sure why this isn't working above )
        int_cols = ['segment_number', 'subject_id', 'duration_ms', 'start_ms', 'end_ms']
        seg_meta_df[int_cols] = seg_meta_df[int_cols].astype(int)
        self.seg_meta_df = seg_meta_df 

        #Save transcript version 
        #seg_meta_df.to_csv(os.path.join(output_dir, 'TEMP_ma_segments_with_trans.csv'), index=False) 
        #Save no transcript version 
        #seg_meta_df = seg_meta_df.drop(['ma_transcription'], axis=1)
        #seg_meta_df.to_csv(os.path.join(output_dir, 'ma_segments.csv'), index=False) 

    def gen_segment_word_timing_files(self, output_dir):
        """
        Save segment word timing to pickle files (list(dict(word, duration (ms), offset (ms))))

        :param output_dir: Path to output directory 
        """
        #make output directory 
        wt_outdir = os.path.join(output_dir, 'word_timing') 
        if not os.path.exists(wt_outdir): 
            os.makedirs(wt_outdir)

        #read segment dict #iterate over calls
        for call_id, seg_df in self.segment_dict.items():
            for s in range(0, seg_df.shape[0]):#iterate over segments
                seg = seg_df.iloc[s]
                seg = self._parse_word_timing_str(seg)
                #get word count 
                self.seg_meta_df.loc[self.seg_meta_df['segment_id'] == seg['segment_id'], 'word_count'] = len(seg['word_timing'])
                #update units (100 ns) to milliseconds 
                for w in range(0, len(seg['word_timing'])):
                    seg['word_timing'][w]['Duration_ms'] = seg['word_timing'][w]['Duration']* 10**-4 
                    seg['word_timing'][w]['Offset_ms'] = seg['word_timing'][w]['Offset']* 10**-4                
                #save to pickle file 
                fn = os.path.join(wt_outdir, seg['segment_id'] + '.pkl')
                with open(fn, 'wb') as file:
                    pickle.dump(seg['word_timing'], file, protocol=pickle.HIGHEST_PROTOCOL) 

        #Save segment metadata
        #****************************
        self.seg_meta_df['word_count'] = self.seg_meta_df['word_count'].astype(int) 
        self.seg_meta_df.to_csv(os.path.join(output_dir, 'ma_segments_with_trans.csv'), index=False) 
        #Save no transcript version 
        seg_meta_df_no_trans = self.seg_meta_df.drop(['ma_transcription'], axis=1)
        seg_meta_df_no_trans.to_csv(os.path.join(output_dir, 'ma_segments.csv'), index=False) 


    def _parse_word_timing_str(self, seg_df):
        """
        Parse word_timing string(list(Dict)) and generate List(Dict) with a dictionary for each word (duration, offset, word)
        :param seg_df: single segment dataframe with word-level timing information. Each row (duration, offset, str(list(Dict)). 
        :return: seg_df: single segment dataframe with each row (duration, offset, list(Dict). 
        """
        word_timing_list = []
        #separate each string word dictionary 
        word_timing_str = seg_df['word_timing'].strip('][').split("},")
        
        #get information for each word dictionary 
        for ws in word_timing_str:
            word_dict = {}
            ws = ws.strip(" ")
            dl = ws.strip("}{").split(",")
            for d in dl:
                d2 = d.split(":")
                k = d2[0].strip(" ").strip("''")
                v = d2[1].strip(" ")
                if v.isnumeric(): #Duration, Offset are integers
                    v = int(v) 
                else: #Word is a string
                    v = v.strip("''")
                word_dict[k] = v
            word_timing_list.append(word_dict) 
        seg_df['word_timing'] = word_timing_list   
        return seg_df 


def _read_file_by_lines(filename):
    """
    Read a file into a list of lines
    """
    with open(filename, "r") as f:
        return f.read().splitlines()

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ms_asr_output_files', type=str,
                        help="Path to text file containing paths to the Microsoft speech-to-text recognition results "
                             "that you want to extract features from. Files should be CSV files as produced by the "
                             "asr-models-support/Microsoft/speech_to_text.py script in "
                             "https://github.com/kmatton/ASR-Helper.")
    parser.add_argument('--wav_dir', type=str, help="Path to directory with audio files to produce segments from.")
    parser.add_argument('--output_dir', type=str, help="Path to directory to output feature files to.")
    parser.add_argument('--call_metadata', type=str, help="Path to file with call metadata (call_id, subject_id, is_assessment etc.)")
    return parser.parse_args()

def main():
    args = _parse_args()
    recognition_result_files = _read_file_by_lines(args.ms_asr_output_files)
    seg_extractor = GenMicrosoftSegments(recognition_result_files, args)
    seg_extractor.generate_segments(args.output_dir, args.wav_dir)
    seg_extractor.gen_segment_word_timing_files(args.output_dir) 

if __name__ == '__main__':
    main()
