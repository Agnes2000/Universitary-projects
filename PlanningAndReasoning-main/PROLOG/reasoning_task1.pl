% Connessioni tra fermate
connessione(a, b, ora(8, 0), 10, autobus1).
connessione(a, b, ora(8, 30), 10, autobus2).
connessione(b, c, ora(8, 15), 15, metro1).
connessione(b, c, ora(8, 50), 15, autobus3).
connessione(a, c, ora(9, 0), 25, autobus4).

:- op(600, xfy, :).

% Conversione orario in minuti
ora_to_min(ora(H, M), Min) :-
    integer(H), integer(M),
    Min is H * 60 + M.

% Conversione da minuti a orario
min_to_ora(Min, ora(H, M)) :-
    H is Min // 60,
    M is Min mod 60.

% Test di debug 
test_debug :-
    writeln('=== TEST CONNESSIONI ==='),
    forall(connessione(Da, A, Ora, Durata, Mezzo),
           format('~w -> ~w alle ~w, durata ~w min, mezzo ~w~n', [Da, A, Ora, Durata, Mezzo])),
    nl,
    writeln('=== TEST CONVERSIONI ORARI ==='),
    ora_to_min(ora(8,0), Min1), format('ora(8,0) = ~w minuti~n', [Min1]),
    ora_to_min(ora(8,15), Min2), format('ora(8,15) = ~w minuti~n', [Min2]),
    ora_to_min(ora(9,0), Min3), format('ora(9,0) = ~w minuti~n', [Min3]).

% Percorso diretto semplice
percorso_diretto(Da, A, OraPartenza, Percorso, OraArrivo, Durata, Mezzi) :-
    connessione(Da, A, OraConn, DurataConn, Mezzo),
    ora_to_min(OraConn, OraConnMin),
    ora_to_min(OraPartenza, OraPartMin),
    OraConnMin >= OraPartMin,
    OraArrivo is OraConnMin + DurataConn,
    Percorso = [Da, A],
    Durata = DurataConn,
    Mezzi = [Mezzo].

% Percorso con una fermata intermedia
percorso_una_fermata(Da, A, OraPartenza, Percorso, OraArrivo, DurataTotale, Mezzi) :-
    % Prima tratta
    connessione(Da, Intermedio, OraConn1, Durata1, Mezzo1),
    ora_to_min(OraConn1, OraConn1Min),
    ora_to_min(OraPartenza, OraPartMin),
    OraConn1Min >= OraPartMin,
    OraArrivoIntermedio is OraConn1Min + Durata1,
    
    % Seconda tratta
    connessione(Intermedio, A, OraConn2, Durata2, Mezzo2),
    ora_to_min(OraConn2, OraConn2Min),
    OraConn2Min >= OraArrivoIntermedio,
    OraArrivo is OraConn2Min + Durata2,
    
    Percorso = [Da, Intermedio, A],
    DurataTotale is OraArrivo - OraPartMin,
    Mezzi = [Mezzo1, Mezzo2].

% Tutti i percorsi possibili
tutti_percorsi(Da, A, OraPartenza, ListaPercorsi) :-
    findall(
        (OraArrivo, DurataTotale, Percorso, Mezzi),
        (
            (percorso_diretto(Da, A, OraPartenza, Percorso, OraArrivo, Durata, Mezzi),
             ora_to_min(OraPartenza, OraPartMin),
             DurataTotale is OraArrivo - OraPartMin)
            ;
            percorso_una_fermata(Da, A, OraPartenza, Percorso, OraArrivo, DurataTotale, Mezzi)
        ),
        ListaPercorsi
    ).

% Percorso più veloce
percorso_ottimale(Da, A, OraPartenza, PercorsoMigliore, OraArrivoMigliore, MezziMigliori) :-
    tutti_percorsi(Da, A, OraPartenza, ListaPercorsi),
    ListaPercorsi \= [],
    sort(ListaPercorsi, [(OraArrivoMigliore, _Durata, PercorsoMigliore, MezziMigliori)|_]).

% Stampa risultati 
mostra_percorsi(Da, A, OraPartenza) :-
    writeln('=== RICERCA PERCORSI ==='),
    format('Da: ~w, A: ~w, Partenza: ~w~n', [Da, A, OraPartenza]),
    tutti_percorsi(Da, A, OraPartenza, ListaPercorsi),
    (ListaPercorsi = [] ->
        writeln('Nessun percorso trovato!')
    ;
        writeln('Percorsi trovati:'),
        sort(ListaPercorsi, ListaOrdinata), % Rimuove duplicati e ordina
        forall(member((OraArr, Dur, Perc, Mezzi), ListaOrdinata),
               (min_to_ora(OraArr, OraArrFormattata),
                format('  Percorso: ~w, Mezzi: ~w, Arrivo: ~w, Durata: ~w min~n', 
                       [Perc, Mezzi, OraArrFormattata, Dur]))),
        nl,
        ListaOrdinata = [(OraArrOtt, DurOtt, PercorsoOtt, MezziOtt)|_],
        min_to_ora(OraArrOtt, OraArrOttFormattata),
        format('PERCORSO OTTIMALE: ~w, Mezzi: ~w, Arrivo: ~w, Durata: ~w min~n', 
               [PercorsoOtt, MezziOtt, OraArrOttFormattata, DurOtt])
    ).

% Reasoning Task: trova la via più veloce tra due punti
fastest_route(From, To, DepartureTime, OptimalRoute, ArrivalTime, TotalDuration, Vehicles) :-
    tutti_percorsi(From, To, DepartureTime, Routes),
    Routes \= [],
    sort(Routes, [(ArrivalTime, TotalDuration, OptimalRoute, Vehicles)|_]).

% Formattazione per visualizzazione
format_vehicles([Vehicle], Vehicle) :- !.
format_vehicles([V1, V2], FormattedVehicles) :- 
    format(atom(FormattedVehicles), '~w + ~w', [V1, V2]).
format_vehicles(Vehicles, FormattedVehicles) :-
    atomic_list_concat(Vehicles, ' + ', FormattedVehicles).

solve_routing_task(From, To, DepartureTime) :-
    format('~n=== ROUTING REASONING TASK ===~n'),
    format('Question: What is the fastest way to travel from ~w to ~w?~n', [From, To]),
    format('Departure time: ~w~n~n', [DepartureTime]),
    
    (fastest_route(From, To, DepartureTime, Route, Arrival, Duration, Vehicles) ->
        (format('Execution: System analyzed all available routes and schedules~n~n'),
         
         % Mostra tutti i percorsi possibili
         tutti_percorsi(From, To, DepartureTime, AllRoutes),
         sort(AllRoutes, SortedRoutes),
         format('All possible routes:~n'),
         forall(member((Arr, Dur, Path, Vehs), SortedRoutes),
                (min_to_ora(Arr, ArrFormatted),
                 format_vehicles(Vehs, VehicleStr),
                 format('  ~w via ~w, arrival: ~w, duration: ~w min~n', 
                        [Path, VehicleStr, ArrFormatted, Dur]))),
         
         nl,
         min_to_ora(Arrival, ArrivalFormatted),
         format_vehicles(Vehicles, VehicleStr),
         format('Answer: The fastest route is ~w~n', [Route]),
         format('        Transportation: ~w~n', [VehicleStr]),
         format('        Departure: ~w~n', [DepartureTime]),
         format('        Arrival: ~w~n', [ArrivalFormatted]),
         format('        Total travel time: ~w minutes~n', [Duration]))
    ;
        format('Answer: No route found from ~w to ~w at ~w~n', [From, To, DepartureTime])
    ).

% Test per il problema
test_problema :-
    writeln('=== TEST PROBLEMA SPECIFICO ==='),
    mostra_percorsi(a, c, ora(8, 0)).

% Test che include anche i mezzi 
test_con_mezzi :-
    writeln('=== TEST CON MEZZI ==='),
    format('Percorso diretto:~n'),
    percorso_diretto(a, c, ora(8,0), Percorso, OraArrivo, Durata, Mezzi),
    min_to_ora(OraArrivo, OraArrFormattata),
    format('  ~w con ~w, arrivo ~w in ~w min~n', [Percorso, Mezzi, OraArrFormattata, Durata]),
    fail.
test_con_mezzi :-
    nl,
    format('Percorsi con fermata:~n'),
    percorso_una_fermata(a, c, ora(8,0), Percorso, OraArrivo, Durata, Mezzi),
    min_to_ora(OraArrivo, OraArrFormattata),
    format('  ~w con ~w, arrivo ~w in ~w min~n', [Percorso, Mezzi, OraArrFormattata, Durata]),
    fail.
test_con_mezzi.
