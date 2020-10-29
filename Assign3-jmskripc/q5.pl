:- [map].

% When looking up basic tutorials for prolog, it was hard to not stumble across
% introductory material that explains how to traverse graphs.
% The following code has some basis from the source:
% https://www.cpp.edu/~jrfisher/www/prolog_tutorial/2_15.html

% This generates all possible paths that exist. I commented extensevly to show what each
% clause is achiveving. And then implemented a custom function that will find the minimum path
% in the set of all generated paths. 

% A helper function to ensure that 'roadTo' queries are symmetric
% so we do not have to check (X,Y) and (Y,X)
roadTo(X,Y,L) :- road(X,Y,L).
roadTo(X,Y,L) :- road(Y,X,L). 

% Helper function to get a path (we do not need the visited list returned)
path(Start,Dest,Path,Length) :-
       path_exists(Start,Dest,[Start],Path,Length).

% A path exists from start to dest if there is a road between them
path_exists(Start,Dest,Visited,[Dest|Visited],Length) :- 
        roadTo(Start,Dest,Length).

% A path exists from Start to Dest if
% there is a path from Start to an intermediate node Int and
% Int is not the destination
% Int has not been visited
% There exists a path from Int to Dest
path_exists(Start,Dest,Visited,Path,Length) :-
        roadTo(Start,Int,L),           
        Int \== Dest,
        \+member(Int,Visited),
        path_exists(Int,Dest,[Int|Visited],Path,PastLength),
        Length is PastLength+L. 

% Brute force approach: Find all paths and then pick the shortest
% The setof() function generates all possible bindings of paths and lengths
% It then forms a l
ist Result of form [[Path, Length], [Path2, Length2]... etc]
% Which we then find the minimum of using min_path
% And then reverse it to make it from Source->Dest
isShortest(Start,Dest,Path):-
    setof([X,L],path(Start,Dest,X,L),Result),
    min_path(Result, RPath, Length),
    reverse(Path, RPath).

% Some custom code for finding the minimum path length

% Code for this was adapted from (https://stackoverflow.com/a/3965130)
% This code instead finds the minimum from a list L of form [[A1,B1], [A2,B2]... etc]
% Where the result is the tuple [A_N, B_N], such that B_N is the minimum of all Bs in L.

% If our list is one item, that is the minimum
min_path([[P,L]],P,L).                 

% Compare the next two path/length pairs in the list
% If the first one is the minimum, keep it
min_path([[P1,L1],[P2,L2]|T],PMin,LMin) :-
    L1 =< L2,                             
    min_path([[P1,L1]|T],PMin,LMin).               

% Compare the next two path/length pairs in the list
% If the second one is the minimum, keep it
min_path([[P1,L1],[P2,L2]|T],PMin,LMin) :-
    L1 > L2,                             
    min_path([[P2,L2]|T],PMin,LMin).               





