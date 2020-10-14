:- [q5].

% Similar to isShortest, except now we choose the longest path
isLongest(Start,Dest,Path):-
    setof([X,L],path(Start,Dest,X,L),Result),
    max_path(Result, RPath, Length),
    reverse(Path, RPath).

% If our list is one item, that is the max
max_path([[P,L]],P,L).                 

% Compare the next two path/length pairs in the list
% If the first one is the max, keep it
max_path([[P1,L1],[P2,L2]|T],PMin,LMin) :-
    L1 > L2,                             
    max_path([[P1,L1]|T],PMin,LMin).               

% Compare the next two path/length pairs in the list
% If the second one is the max, keep it
max_path([[P1,L1],[P2,L2]|T],PMin,LMin) :-
    L1 =< L2,                             
    max_path([[P2,L2]|T],PMin,LMin).     