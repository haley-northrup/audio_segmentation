function [sil_st_points, sil_end_points, sp_st_points, sp_end_points] = find_start_end_points(vadout)

% find start and end points speech and silences from 
% binary voice activity detector output (vadout) 

vadout = (vadout + 0);
delta_vadout = vadout(2:end) - vadout(1:end-1);
sil_st_points = find(delta_vadout > -1.1 & delta_vadout < -0.9) + 1;
sil_end_points = find(delta_vadout < 1.1 & delta_vadout > 0.9);
sp_st_points = find(delta_vadout < 1.1 & delta_vadout > 0.9) + 1;
sp_end_points = find(delta_vadout > -1.1 & delta_vadout < -0.9);
if vadout(1) == 1
    sp_st_points = [1; sp_st_points];
else
    sil_st_points = [1; sil_st_points];
end
if vadout(end) == 1
    sp_end_points = [sp_end_points; length(vadout)];
else
    sil_end_points = [sil_end_points; length(vadout)];
end
if length(sil_st_points) ~= length(sil_end_points)
    error('find_start_end_points: length(sil_st_points) ~= length(sil_end_points)')
end
if length(sp_st_points) ~= length(sp_end_points)
    error('find_start_end_points: length(sp_st_points) ~= length(sp_end_points)')
end
sp_end_points = round(sp_end_points);
sil_end_points = round(sil_end_points);
end
