
% There are two OS-linked manufacturers. Apple and Microsoft.
rel(apple, isA, osManufacturer).
rel(microsoft, isA, osManufacturer).

% Apple makes Macbooks, iPads, and iPhones,
rel(macbook, madeBy, apple).
rel(iPad, madeBy, apple).
rel(iPhone, madeBy, apple).

% the first two which are computers.

rel(macbook, isA, computer).
rel(iPad, isA, computer).

% Microsoft makes the Surface series of computers, 
rel(surface, madeBy, microsoft).
rel(surface, isA, computer).

% as well as the Zune music player.
rel(zune, madeBy, microsoft).
rel(zune, isA, musicPlayer).

% The Macbooks come in 15 and 13 inch models and are not touchscreens
rel(mac15Inch, isA, macbook).
rel(mac13Inch, isA, macbook).

% The iPad is a tablet
rel(iPad, isA, tablet).

% The surfaces come in a go and pro model
rel(surfaceGo, isA, surface).
rel(surfacePro, isA, surface).

% All apple products are compatible with eachother

% Tablets are touch screens (per assign 3 working thread by Dr. Lynch)
rel(tablet, isA, touchscreen).

% Microsoft products are not. Using closed world assumption to represent in prolog

% The Surface Pro is compatible with an iPad, and an iPhone, the Zune is not.
rel(surfacePro, compatible, iPad).
rel(iPad, compatible, surfacePro).

rel(surfacePro, compatible, iPhone).
rel(iPhone, compatible, surfacePro).

% The Zune is not. Using closed world assumption to represent in prolog

isa(X,Y) :-
    rel(X, isA, Y).

isa(X,Y) :-
    rel(X, isA, Z),
    rel(Z, isA, Y).

% Things madeBy stuff is also "isA" stuff
isa(X,Y) :-
    rel(X, madeBy, Y).

isa(X,Y) :-
    rel(X, isA, Z),
    rel(Z, madeBy, Y).

madeBy(X,Y) :-
    rel(X, madeBy, Y).

madeBy(X,Y):-
    rel(X, isA, Z),
    rel(Z, madeBy, Y).

% All apple products are compatable with eachother
compatible(X,Y) :-
    madeBy(X, apple),
    madeBy(Y, apple).

compatible(X,Y) :-
    rel(X, compatible, Y).

