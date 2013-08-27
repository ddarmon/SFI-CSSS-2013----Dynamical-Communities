classdef utils
    % A simple static class whin it only objective in life is to
    % facilitates the access to simple functions for the analysis of
    % modularity in a twitter network
    
    
    methods(Static)
       
        function matrix = CREATE_MATRIX_FROM_TXT(text_file,use_weigth)
            %This function creates an adjacency matrix from a text file
            %that has the next format:
            %node_i node_j weight
            
            [n1 n2 weigth] = textread(text_file);
            
            
            if(nargin == 2)
                if(use_weigth == 0)
                    weigth = ones(size(weigth));
                end
            end
            
            nmax = max(max(n1), max(n2)) + 1; %indexing in matlab start at 1, not at 0
            matrix = zeros(nmax, nmax);
            
            for i = 1:length(n1)
                matrix(n1(i)+1, n2(i)+1) = weigth(i);
                matrix(n2(i)+1, n1(i)+1) = weigth(i);
            end
            
            
        end
        
        function [values ammount] = COUNT_VALUES(vec)
            % It count the number of elements for each unique value
            % in a vector vec. It returns two vectors, values that
            % represent the unique elements and ammount that is one-to-one
            % map of the value element to its corresponding amount
            
            values = unique(vec);
            ammount = zeros(size(values));
            for i = 1:length(values); ammount(i) = sum(vec==values(i)); end;
            
        end
        
        function S_new = RESORT_COMMUNITY_INDEX(S)
            % This function resort the community index vector such that the
            % the module index is in decreasing size. In other words, S_new
            % will be a community index vector in which the biggest module
            % will be 1, the second biggest module will be 2, and so on.
            
            [val, ammount] = utils.COUNT_VALUES(S);
            
            [w,idx] = sort(ammount,'descend');
            
            S_new = zeros(size(S));
            for i = 1:length(idx)
                S_new(S==idx(i)) = i; 
            end
            
        end
        
        function n = SHARED_MODULE(s1,s2,module_id_1,module_id_2)
            
            if(nargin == 3); module_id_2 = 3; end;
            
            idx1 = find(s1==module_id_1);
            idx2 = find(s2==module_id_2);
            
            n = length(intersect(idx1,idx2));
            
        end
        
        function [s1_new s2_new] = MINIMIZE_DISTANCE(s1,s2)
            % It relabels the module id's of two partition vectors in order
            % to minimize the JACCARD's distance. Right now a simple
            % heuristic based in the size of intersection of two modules is
            % used. However, in the future a better heuristic can be used.
            
            s1 = utils.RESORT_COMMUNITY_INDEX(s1);
            s2 = utils.RESORT_COMMUNITY_INDEX(s2);
            
            s1_big_than_s2 = max(s1) >= max(s2);
            min_size = min(max(s1),max(s2));
            
            s1_new = s1; %Do not need to relabel s1.
            s2_new = zeros(size(s2)); %S2 will be relabed to minimize distance with S1.
            
            for i = 1:max(s1)
                idx1 = find(s1==i);
                
                idx2_max = min(setdiff(s2,-1));
                intersection_max = 0;
                
                for j = 1:max(s2);
                    idx2 = find(s2==j);
                    shared = intersect(idx1,idx2);
                    if(intersection_max < length(shared))
                        intersection_max = length(shared);
                        idx2_max = idx2;
                    end    
                end
                
                if(intersection_max > 0)
                    s2_new(indx2_max) = i;
                    s2(idx2_max) = -1; %Do not relabel this module again
                end
            end
            
            if(~s1_big_than_s2)
                s1(s2~=-1)
            end
            
        end
        
        function louvain = CALCULATE_STATIC_MODULARITY(A)
            % Calculates the static modularity of adjacency matrix A.
            % It returns an structure with the next values:
            %   * Q: Modularity Value
            %   * S: Community assigment
            
            g = genpath('../GenLouvain1.2');
            addpath(g);
            
            gamma = 1;
            k = full(sum(A));
            twom = sum(k);
            B = @(i) A(:,i) - gamma*k'*k(i)/twom;
            [S,Q] = genlouvain(B);
            Q = Q/twom;
            louvain.S = S;
            louvain.Q = Q;
            
            
            
        end
        
        
    end
    
end