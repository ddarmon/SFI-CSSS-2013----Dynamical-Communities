matrix_weight = utils.CREATE_MATRIX_FROM_TXT('edge_list_3K_user_weighted-300s.txt');
matrix_bool = utils.CREATE_MATRIX_FROM_TXT('edge_list_3K_user_weighted-300s.txt',0);

louvain_bool = utils.CALCULATE_STATIC_MODULARITY(matrix_bool);
louvain_weight = utils.CALCULATE_STATIC_MODULARITY(matrix_weight);

[vv_w aa_w] = utils.COUNT_VALUES(louvain_weight.S);
[vv_b aa_b] = utils.COUNT_VALUES(louvain_bool.S);

sb_sorted = utils.RESORT_COMMUNITY_INDEX(louvain_bool.S);
sw_sorted = utils.RESORT_COMMUNITY_INDEX(louvain_weight.S);

for i = 1:5
    p(i) = utils.SHARED_MODULE(sb_sorted,sw_sorted,i)
end