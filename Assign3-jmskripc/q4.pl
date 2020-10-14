c([H|T],X):-
    c(H,N),
    c(T,M),
    X is N + M.

c(a,1).
c(_,0).

