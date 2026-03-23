% --- Connessioni: da, a, mezzo, tempo
connessione(a, b, metro1, 10).
connessione(b, c, bus1, 5).
connessione(a, c, metro2, 15).
connessione(c, d, bus2, 20).
connessione(b, d, tram1, 30).
connessione(c, e, metro2, 10).
connessione(e, d, bus2, 5).

% --- Stato rappresentato come at(Pos)
initially(at(a)).

% --- Azione primitiva
primitive_action(travel(_, _, _, _)).

% --- Condizione di esecuzione
poss(travel(X, Y, Mezzo, T), at(X)) :-
    connessione(X, Y, Mezzo, T).

% --- Effetto dell azione
result(travel(X, Y, _, _), at(Y)).

% --- Procedura principale per andare da X a Y
proc(go(X, Y), (
    find_best_path(X, Y, Percorso),
    exec_path(Percorso)
)).

% --- Trova percorso più veloce (min tempo)
find_best_path(Start, Goal, BestPath) :-
    setof(Time-Path, path(Start, Goal, Path, Time), [ _-BestPath | _]).

% --- Ricerca percorsi con accumulo tempi
path(Start, Goal, Path, Time) :-
    travel_path(Start, Goal, [], RevPath, 0, Time),
    reverse(RevPath, Path).

travel_path(X, X, Path, Path, Time, Time).
travel_path(X, Y, Visited, Path, AccTime, Time) :-
    connessione(X, Z, Mezzo, T),
    \+ member(travel(X, Z, Mezzo, T), Visited),
    NewTime is AccTime + T,
    travel_path(Z, Y, [travel(X,Z,Mezzo,T)|Visited], Path, NewTime, Time).

% --- Esecuzione sequenza azioni
exec_path([]).
exec_path([travel(X,Y,Mezzo,T) | Rest]) :-
    format("Travel from ~w to ~w by ~w in ~w minutes.~n", [X,Y,Mezzo,T]),
    exec_path(Rest).


% Calcola percorso migliore da A a B
best_route(A, B, Percorso) :-
    setof(Time-Path, path(A, B, Path, Time), [MinTime-Percorso|_]).

print_all_paths(A,B) :-
    findall(Time-Path, path(A,B,Path,Time), Paths),
    forall(member(T-P, Paths), (
        format("Percorso con tempo ~w: ~w~n", [T,P])
    )).

% Stampa ed esegue la lista di azioni travel/4
indigolog_execute([]).
indigolog_execute([travel(X,Y,Mezzo,T)|Rest]) :-
    format("Travel from ~w to ~w by ~w in ~w minutes.~n", [X,Y,Mezzo,T]),
    indigolog_execute(Rest).

% IndiGolog entry point: calcola e esegui percorso da A a B
indigolog(go(A,B)) :-
    best_route(A,B, Percorso),
    indigolog_execute(Percorso).


% --- Interprete IndiGolog minimale
indigolog(go(X,Y)) :-
    initially(State),
    proc(go(X,Y), Prog),
    run(Prog, State).

run((A,B), State) :- !,
    run(A, State),
    run(B, State).
run(Action, State) :-
    % Se Action è travel(...)
    primitive_action(Action), !,
    ( poss(Action, State) ->
        result(Action, NewState),
        format("Executing: ~w~n", [Action]),
        run(done, NewState)
    ; format("Action not possible: ~w~n", [Action])
    ).
run(done, _) :- !.
run(_, _) :-
    format("No further steps.~n").
