function [seg_start_inds, seg_end_inds]=find_segment_boundaries(vadout)
[~, ~, sp_st_points, sp_end_points] = find_start_end_points(vadout);
seg_start_inds = max(sp_st_points - 4000, 1);
seg_end_inds = min(sp_end_points + 4000, length(vadout));
end