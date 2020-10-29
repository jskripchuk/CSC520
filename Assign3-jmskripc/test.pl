rel(surface, isa, laptop).
rel(surfacePro, isa, surface).

isa(X, Y) :- rel(X, isa, Y).

isa(X, Y) :- 
    rel(X, isa, Z),
    rel(Z, isa, Y).