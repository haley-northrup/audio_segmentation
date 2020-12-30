function doSegmentationAll(part_id, part_num)
inpath = '/nfs/turbo/McInnisLab/priori_v1_data/call_audio/speech';
outpath = '/nfs/turbo/McInnisLab/soheil-segmentation-script/priori_v1_segments';
callid_subid_file = '/nfs/turbo/McInnisLab/soheil-segmentation-script/priori_v1_callid_subjectid.txt';
callid_subid_list = textread(callid_subid_file);
% callid_subid_list = [2 1379001 ; 0 0; 3 1379001];
part_id = part_id - 1;
addpath('support');
addpath('voicebox');
addpath('others');
for i = 1:size(callid_subid_list,1)
    if rem(i, part_num) ~= part_id
        % disp('invalid part num')
        continue;
    end
    call = callid_subid_list(i,1);
    sub = callid_subid_list(i,2);
    infile = [inpath '/' num2str(call) '.wav'];
    outdir = [outpath '/' num2str(sub) '/' num2str(call)];
    if exist(infile, 'file') ~= 2
        disp(['Invalid infile. call: ' num2str(call)]);
        continue;
    end
    if exist(outdir, 'dir') == 7
        disp(['Invalid outdir. call: ' num2str(call)]);
        continue;
    end
    mkdir(outdir);
    finfo = dir(infile);
    if finfo.bytes > (100 * 1024 * 1024)
        disp(['File is too big. call: ' num2str(call)]);
        continue;
    end
    copyfile(infile, outdir);
    disp(['Extracting segments for call ' num2str(call)]);
    try
        apply_combosad(infile, outdir);
    catch
        disp(['Can not extract segments from call: ' num2str(call)]);
    end
end
end
