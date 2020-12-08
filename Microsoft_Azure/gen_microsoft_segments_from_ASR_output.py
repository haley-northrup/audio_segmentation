import os
import argparse
import pandas as pd
import numpy as np
from pydub import AudioSegment

from IPython import embed 

"""
Script for generating segments from Microsoft Azure ASR output 
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
            segment_dict[idx] = sorted_entries.drop(['word_timing', 'confidence'], axis=1)  
        return segment_dict

    def generate_segments(self, output_dir, wav_dir):
        """
        Generate and save segment .wav files and metadata based on segment timing (segment_dict)
        :return: none
        """
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
                                
                #TODO is the segment_id name "ms_" confusing with milliseconds ("_ms") 
                # save segment to .wav file ("ms_<call_id>_<segment_number>")
                seg_id = 'ms_' + str(call_id) + '_' + str(s) 
                #orig_audio.export(os.path.join(output_dir, str(call_id) + '.wav'))
                segment_audio.export(os.path.join(output_dir, seg_id + '.wav'), format="wav")

                #Save segment metadata 
                seg_meta_df.loc[ct, 'segment_id'] =  seg_id
                seg_meta_df.loc[ct, 'call_id'] = int(call_id)
                seg_meta_df.loc[ct, 'segment_number'] = int(s) #John/Soheil called "segment_order" 
                seg_meta_df.loc[ct, 'subject_id'] = self.call_meta_df.loc[cidx, 'subject_id'].astype(int).values[0]
                seg_meta_df.loc[ct, 'call_datetime'] = self.call_meta_df.loc[cidx, 'date_time'].values[0]
                seg_meta_df.loc[ct, 'is_assessment'] = self.call_meta_df.loc[cidx, 'is_assessment'].values[0]
                seg_meta_df.loc[ct, 'duration_ms'] = int(duration_ms) #John/Soheil call "segment_length"
                seg_meta_df.loc[ct, 'start_ms'] = int(start_ms) 
                seg_meta_df.loc[ct, 'end_ms'] = int(end_ms) 
                seg_meta_df.loc[ct, 'ms_transcription'] = seg_df.loc[sidx, 'text'].values[0] 
                ct = ct + 1 
        #Save transcript version 
        seg_meta_df.to_csv(os.path.join(output_dur, 'seg_meta_test_with_ASR_trans.csv'), index=False) 
        #Save no transcript version 
        seg_meta_df = seg_meta_df.drop(['ms_transcription'], axis=1)
        seg_meta_df.to_csv(os.path.join(output_dir, 'seg_meta_test.csv'), index=False) 


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


if __name__ == '__main__':
    main()
