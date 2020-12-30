function vadout=remove_small_silences(vadout, min_silence_len)
[sil_st_points, sil_end_points, ~, ~] = find_start_end_points(vadout);
sil_lens = sil_end_points - sil_st_points + 1;
small_sil_inds = find(sil_lens < min_silence_len);
for i=1:length(small_sil_inds)
    ind = small_sil_inds(i);
    vadout(sil_st_points(ind):sil_end_points(ind)) = 1;
end
end
