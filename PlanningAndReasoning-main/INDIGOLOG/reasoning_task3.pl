% --- Connessioni base: da, a, mezzo, tempo senza ritardi
connessione(a, b, metro1, 10).
connessione(b, c, bus1, 5).
connessione(a, c, metro2, 15).
connessione(c, d, bus2, 20).
connessione(b, d, tram1, 30).
connessione(c, e, metro2, 10).
connessione(e, d, bus2, 5).

% --- Ritardi dinamici sui mezzi (default 0 minuti)
:- dynamic delay/2.
delay(metro1, 0).
delay(bus1, 0).
delay(metro2, 0).
delay(bus2, 0).
delay(tram1, 0).

% --- Stato rappresentato come at(Pos)
initially(at(a)).

% --- Azione primitiva
primitive_action(travel(_, _, _, _)).

% --- Condizione di esecuzione: azione possibile solo se siamo nella posizione di partenza
poss(travel(X, Y, Mezzo, T), at(X)) :-
    connessione(X, Y, Mezzo, BaseTime),
    delay(Mezzo, Delay),
    T is BaseTime + Delay.

% --- Effetto dell azione: aggiornamento stato posizione
result(travel(X, Y, _, _), at(Y)).

% --- Procedura principale per andare da X a Y
proc(go(X, Y, Evita), (
    best_route_con_preferenze(X, Y, Evita, Percorso),
    exec_path(Percorso)
)).

% --- Trova percorso più veloce (min tempo) considerando i ritardi
find_best_path(Start, Goal, BestPath) :-
    setof(Time-Path, path(Start, Goal, Path, Time), [ _-BestPath | _]).

% --- Ricerca percorsi con accumulo tempi e ritardi
% path_con_preferenze(+Start, +End, -Percorso, -Tempo, +Evita)
path(Start, Goal, Path, Time, Evita) :-
    travel_path(Start, Goal, [], RevPath, 0, Time, Evita),
    reverse(RevPath, Path).


% travel_path(+Start, +Goal, +Visited, -Path, +AccTime, -TotalTime, +Evita)
travel_path(X, X, Path, Path, Time, Time, _).

travel_path(X, Y, Visited, Path, AccTime, Time, Evita) :-
    connessione(X, Z, Mezzo, T),
    \+ member(Mezzo, Evita),
    \+ member(travel(X, Z, Mezzo, _), Visited),
    ritardo_corrente(Mezzo, R),
    NewT is T + R,
    NewTime is AccTime + NewT,
    travel_path(Z, Y, [travel(X,Z,Mezzo,NewT)|Visited], Path, NewTime, Time, Evita).



ritardo_corrente(Mezzo, Ritardo) :-
    ritardo(Mezzo, Ritardo), !.
ritardo_corrente(_, 0).

% --- Esecuzione sequenza azioni: stampa il percorso step by step
exec_path([]).
exec_path([travel(X, Y, Mezzo, T) | Rest]) :-
    format("Travel from ~w to ~w by ~w in ~w minutes.~n", [X, Y, Mezzo, T]),
    exec_path(Rest).

% --- Stampa tutti i percorsi per debug
print_all_paths(A, B) :-
    findall(Time-Path, path(A, B, Path, Time), Paths),
    forall(member(T-P, Paths), (
        format("Percorso con tempo ~w: ~w~n", [T, P])
    )).

set_ritardo(Mezzo, Minuti) :-
    retractall(ritardo(Mezzo, _)),
    asserta(ritardo(Mezzo, Minuti)).

% --- IndiGolog esecuzione delle azioni travel/4
indigolog_execute([]).
indigolog_execute([travel(X, Y, Mezzo, T)|Rest]) :-
    format("Travel from ~w to ~w by ~w in ~w minutes.~n", [X, Y, Mezzo, T]),
    indigolog_execute(Rest).

% --- IndiGolog entry point: calcola e esegui percorso da A a B
% --- IndiGolog entry point con preferenze: calcola e esegui percorso evitando certi mezzi
indigolog(go(A, B, MezziDaEvitare)) :-
    best_route(A, B, MezziDaEvitare, Percorso),
    indigolog_execute(Percorso).

% --- Calcola percorso migliore da A a B evitando certi mezzi
best_route(A, B, MezziDaEvitare, BestPath) :-
    setof(Time-Path, path(A, B, Path, Time, MezziDaEvitare), [ _-BestPath | _]).


% --- Interprete IndiGolog minimale
indigolog(go(X, Y)) :-
    initially(State),
    proc(go(X, Y), Prog),
    run(Prog, State).

run((A, B), State) :- !,
    run(A, State),
    run(B, State).

run(Action, State) :-
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
