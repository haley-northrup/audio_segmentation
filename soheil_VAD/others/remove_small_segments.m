function vadout=remove_small_segments(vadout, min_len)
[~, ~, st_points, end_points] = find_start_end_points(vadout);
sil_lens = end_points - st_points + 1;
small_inds = find(sil_lens < min_len);
for i=1:length(small_inds)
    ind = small_inds(i);
    vadout(st_points(ind):end_points(ind)) = 0;
end
end
