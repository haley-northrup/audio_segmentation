function apply_combosad(audiofile,outdir)

min_silence_len = 12000; % 1.5 seconds max silence allowed in segment 
min_segment_len = 8000; % 1 second
fs=8000; % Hz
max_section_length = 5 * 60 * 8000; % each section is 5 min
vadout_pow_threshold = 0.0025;
% -------------

% read in audio
[sam,fs_orig]=audioread(audiofile);
all_sam_8k=downsample(sam(:,1),fs_orig/fs);

part_ind = 1;
section_num = floor((length(all_sam_8k)-1) / max_section_length) + 1;
for section_id = 1:section_num
    st = (section_id-1) * max_section_length + 1;
    en = min(section_id * max_section_length, length(all_sam_8k));
    sam_8k = all_sam_8k(st:en);

    if en - st + 1 <= (1 * 8000)
        continue;
    end

%    NOT USED *** old ComboSAD code 
%    [ vadout, params ] = extractComboSAD( sam_8k, 8000, 256, 80 );
%    vadout = vadout > 1;
%    vadout=repmat(vadout, 1, 80)';
%    vadout=vadout(:);

    %apply hanning window
    vadout_pow = conv(sam_8k.^2, hann(200));  
    %apply power threshold
    vadout_pow = vadout_pow > vadout_pow_threshold;  
    vadout = vadout_pow + 0; % binary array (1=speech, 0=silence)

    %remove small segments (1 --> 0) (remove false alarms)
    vadout=remove_small_segments(vadout, 2000);
    %remove small silences (0 --> 1) (combine speech separated by small silences)
    vadout=remove_small_silences(vadout, min_silence_len);
    %remove small segments 
    vadout=remove_small_segments(vadout, min_segment_len);
    
    %Get final set of segments 
    [seg_start_inds, seg_end_inds]=find_segment_boundaries(vadout);
    seg_start_inds = max(1, seg_start_inds);
    seg_end_inds = min(length(sam_8k), seg_end_inds);
    if exist(outdir,'dir') ~= 7
        mkdir(outdir);
    end
    for i=1:length(seg_start_inds)
        %THIS CODE IS WRONG ***********************************************
        %SHOULD REFERENCE all_sam_8k not sam_8k (5 minute chunks of original audio) 
        len_in_sec = (seg_end_inds(i) - seg_start_inds(i)) / 8000;
        seg_start = seg_start_inds(i) / 8000;
        seg_end = seg_end_inds(i) / 8000;
        filename = [outdir '/part' num2str(part_ind) '_' num2str(len_in_sec) '_' num2str(seg_start) '_' num2str(seg_end) '.wav'];
        part_ind = part_ind + 1;
        % disp([num2str(seg_start_inds(i)) ' ' num2str(seg_end_inds(i)) ' ' num2str(length(sam_8k))]);
        %******************************************************************

        %Save segments to .wav files 
        audiowrite(filename,sam_8k(seg_start_inds(i):seg_end_inds(i)),8000);
    end
end
end

