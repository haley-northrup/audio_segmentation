import os 
from IPython import embed

''' Get paths to all Microsoft Azure outputs for PRIORI v1 

NOTE: HARD CODED!! - Subject 2062001 has no recognition_results.csv file (no text recognized for calls) 
''' 


def _read_file_by_lines(filename):
    """
    Read a file into a list of lines
    """
    with open(filename, "r") as f:
        return f.read().splitlines()

num_jobs = 10 
trans = '/nfs/turbo/McInnisLab/Katie/PRIORI-v1-Microsoft-transcripts/'
ctfile = os.path.join(trans, 'subject_set_counts.txt') 

subCts = _read_file_by_lines(ctfile)


sub_set_counts = {}
for l in subCts:
    subject_id = l.split(' ')[0]
    sub_set_counts[subject_id] = int(l.split(' ')[1])

all_paths = []
for subject_id, ct in sub_set_counts.items():
    if subject_id == '2062001':
        continue 
        
    for i in range(0, ct):
        set_folder = 'speech_recognition_output_set_' + str(i) 
        set_path = os.path.join(trans, subject_id, set_folder, 'recognition_results.csv')
        set_path = set_path + "\n"

        all_paths.append(set_path) 

outF = open("ma_pv1_set_paths.txt", "w")
outF.writelines(all_paths)
outF.close()

#TEST WITH LISTDIRS 
#all_paths_2 = []
#for subject_id, ct in sub_set_counts.items():
#    a = os.listdir(os.path.join(trans, subject_id)) 
#    set_dirs = [i for i in a if 'speech_recognition_output_set_' in i]
#    all_paths_2 = all_paths_2 + set_dirs 

#CHECK ALL PATHS EXIST 
for p in all_paths:
    if os.path.exists(p[:-1]) == False:
        print('Path does not exist')
        print(p)



#Generate a path file for each job 
sets_per_job = int(len(all_paths)/num_jobs)
#print(len(all_paths)) 

for j in range(0, num_jobs):
    #print(j) 
    if j < (num_jobs - 1):
        #print(j*sets_per_job)
        #print((j+1)*sets_per_job-1)
        paths = all_paths[j*sets_per_job:(j+1)*sets_per_job]
        #print(len(paths))
    else:
        #print(j*sets_per_job)
        paths = all_paths[j*sets_per_job:]
        #print(len(paths))

    outF = open("ma_pv1_set_paths_" + str(j) + '.txt', "w")
    outF.writelines(paths)
    outF.close() 
