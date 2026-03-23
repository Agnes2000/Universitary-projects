% Connessioni
connessione(a, b, ora(8,10), 20, autobus1).
connessione(a, b, ora(8,30), 25, metro1).
connessione(b, c, ora(8,40), 15, autobus2).
connessione(b, c, ora(9,0),  12, metro2).
connessione(a, c, ora(9,10), 40, treno_diretto).

% Tipi di mezzo per le preferenze
tipo_mezzo(autobus1, autobus).
tipo_mezzo(autobus2, autobus).
tipo_mezzo(metro1, metro).
tipo_mezzo(metro2, metro).
tipo_mezzo(treno_diretto, treno).

% Conversioni orarie e formattazioni
ora_to_min(ora(H, M), Minuti) :- Minuti is H * 60 + M.
min_to_ora(Minuti, ora(H, M)) :- H is Minuti // 60, M is Minuti mod 60.
format_vehicles([Mezzo], Mezzo).
format_vehicles(Mezzi, Formattato) :- atomic_list_concat(Mezzi, ' -> ', Formattato).

percorso_diretto(Da, A, OraPartenza, Percorso, OraArrivo, Durata, Mezzi) :-
    connessione(Da, A, OraPart, DurataConn, Mezzo),
    ora_to_min(OraPart, OraPartMin),
    ora_to_min(OraPartenza, OraPartenzaMin),
    OraPartMin >= OraPartenzaMin,
    OraArrivo is OraPartMin + DurataConn,
    Percorso = [Da, A],
    Durata = DurataConn,
    Mezzi = [Mezzo].

percorso_una_fermata(Da, A, OraPartenza, Percorso, OraArrivo, DurataTotale, Mezzi) :-
    connessione(Da, Intermedio, OraConn1, Durata1, Mezzo1),
    ora_to_min(OraConn1, OraConn1Min),
    ora_to_min(OraPartenza, OraPartMin),
    OraConn1Min >= OraPartMin,
    OraArrivoIntermedio is OraConn1Min + Durata1,
    connessione(Intermedio, A, OraConn2, Durata2, Mezzo2),
    ora_to_min(OraConn2, OraConn2Min),
    OraConn2Min >= OraArrivoIntermedio,
    OraArrivo is OraConn2Min + Durata2,
    Percorso = [Da, Intermedio, A],
    DurataTotale is OraArrivo - OraPartMin,
    Mezzi = [Mezzo1, Mezzo2].

tutti_percorsi(Da, A, OraPartenza, ListaPercorsi) :-
    findall(
        (OraArrivo, DurataTotale, Percorso, Mezzi),
        (
            (percorso_diretto(Da, A, OraPartenza, Percorso, OraArrivo, _DurataConn, Mezzi),
             ora_to_min(OraPartenza, OraPartenzaMin),
             DurataTotale is OraArrivo - OraPartenzaMin)
            ;
            percorso_una_fermata(Da, A, OraPartenza, Percorso, OraArrivo, DurataTotale, Mezzi)
        ),
        ListaPercorsi
    ).

:- dynamic(ritardo/2).
:- dynamic(mezzo_cancellato/1).

aggiungi_ritardo(Mezzo, MinutiRitardo) :- 
    retractall(ritardo(Mezzo, _)), assertz(ritardo(Mezzo, MinutiRitardo)), format('~n--[LOG: Aggiunto ritardo di ~w minuti per ~w]--~n', [MinutiRitardo, Mezzo]).

rimuovi_ritardo(Mezzo) :- 
    retractall(ritardo(Mezzo, _)), format('--[LOG: Rimosso ritardo per ~w]--~n', [Mezzo]).

connessione_disponibile(Da, A, OraPart, Durata, Mezzo, OraPartEffettiva) :- 
    connessione(Da, A, OraPart, Durata, Mezzo), (ritardo(Mezzo, MinutiRitardo) -> (ora_to_min(OraPart, OraPartMin), OraPartEffettivaMin is OraPartMin + MinutiRitardo, min_to_ora(OraPartEffettivaMin, OraPartEffettiva)) ; OraPartEffettiva = OraPart).

connessione_utilizzabile(Da, A, OraPart, Durata, Mezzo, OraPartEffettiva) :- 
    connessione_disponibile(Da, A, OraPart, Durata, Mezzo, OraPartEffettiva), \+ mezzo_cancellato(Mezzo).

percorso_diretto_con_ritardi(Da, A, OraPartenza, Percorso, OraArrivo, Durata, Mezzi, Ritardi) :- 
    connessione_utilizzabile(Da, A, _, DurataConn, Mezzo, OraPartEffettiva), ora_to_min(OraPartEffettiva, OraPartEffettivaMin), ora_to_min(OraPartenza, OraPartMin), OraPartEffettivaMin >= OraPartMin, OraArrivo is OraPartEffettivaMin + DurataConn, Percorso = [Da, A], Durata = DurataConn, Mezzi = [Mezzo], (ritardo(Mezzo, RitardoMin) -> Ritardi = [Mezzo-RitardoMin] ; Ritardi = []).

percorso_una_fermata_con_ritardi(Da, A, OraPartenza, Percorso, OraArrivo, DurataTotale, Mezzi, Ritardi) :- 
    connessione_utilizzabile(Da, Intermedio, _, Durata1, Mezzo1, OraConn1Effettiva), ora_to_min(OraConn1Effettiva, OraConn1EffettivaMin), ora_to_min(OraPartenza, OraPartMin), OraConn1EffettivaMin >= OraPartMin, OraArrivoIntermedio is OraConn1EffettivaMin + Durata1, connessione_utilizzabile(Intermedio, A, _, Durata2, Mezzo2, OraConn2Effettiva), ora_to_min(OraConn2Effettiva, OraConn2EffettivaMin), OraConn2EffettivaMin >= OraArrivoIntermedio, OraArrivo is OraConn2EffettivaMin + Durata2, Percorso = [Da, Intermedio, A], DurataTotale is OraArrivo - OraPartMin, Mezzi = [Mezzo1, Mezzo2], findall(Mezzo-Ritardo, (member(Mezzo, [Mezzo1, Mezzo2]), ritardo(Mezzo, Ritardo)), Ritardi).    tutti_percorsi_con_ritardi(Da, A, OraPartenza, ListaPercorsi) :- findall((OraArrivo, DurataTotale, Percorso, Mezzi, Ritardi), ((percorso_diretto_con_ritardi(Da, A, OraPartenza, Percorso, OraArrivo, _Durata, Mezzi, Ritardi), ora_to_min(OraPartenza, OraPartMin), DurataTotale is OraArrivo - OraPartMin) ; percorso_una_fermata_con_ritardi(Da, A, OraPartenza, Percorso, OraArrivo, DurataTotale, Mezzi, Ritardi)), ListaPercorsi).

format_delays([], 'no delays') :- !.

format_delays([Mezzo-Ritardo], FormattedDelays) :- 
    format(atom(FormattedDelays), '~w delayed by ~w min', [Mezzo, Ritardo]), !.

format_delays(Delays, FormattedDelays) :- 
    maplist(format_single_delay, Delays, DelayStrings), atomic_list_concat(DelayStrings, ', ', FormattedDelays).

format_single_delay(Mezzo-Ritardo, DelayString) :- 
    format(atom(DelayString), '~w delayed by ~w min', [Mezzo, Ritardo]).

solve_delay_task(From, To, DepartureTime, DelayedVehicle, DelayMinutes) :-
    format('~n=== DELAY HANDLING REASONING TASK ===~n'),
    format('Question: What are the travel options if transport ~w is delayed by ~w minutes?~n',
           [DelayedVehicle, DelayMinutes]),
    format('Route: ~w to ~w, planned departure after ~w~n~n', [From, To, DepartureTime]),
    format('Execution: Analyzing all routes before and after the delay.~n'),
    format('~n--- 1. AVAILABLE ROUTES (NO DELAYS) ---~n'),
    tutti_percorsi(From, To, DepartureTime, OriginalRoutes),
    ( OriginalRoutes = [] ->
        format('No routes found from ~w to ~w. Cannot proceed with delay analysis.~n', [From, To])
    ;
        sort(OriginalRoutes, SortedOriginalRoutes),
        length(SortedOriginalRoutes, NumRoutes),
        format('Found ~w possible original route(s):~n', [NumRoutes]),
        forall(member((Arr, Dur, Path, Vehs), SortedOriginalRoutes),
               (min_to_ora(Arr, ArrFormatted),
                format_vehicles(Vehs, VehicleStr),
                format('  - Route: ~w via ~w~n    Arrival: ~w, Duration: ~w min~n',
                       [Path, VehicleStr, ArrFormatted, Dur]))),
        SortedOriginalRoutes = [(_, OrigDuration, _, _)|_],
        aggiungi_ritardo(DelayedVehicle, DelayMinutes),
        format('--- 2. ALTERNATIVE ROUTES (WITH DELAY) ---~n'),
        tutti_percorsi_con_ritardi(From, To, DepartureTime, DelayedRoutesWithInfo),
        findall((Path, Vehs), member((_,_,Path,Vehs,_), DelayedRoutesWithInfo), DelayedRoutes),
        ( DelayedRoutesWithInfo = [] ->
            format('  No routes available with the current delay!~n')
        ;
            sort(DelayedRoutesWithInfo, SortedDelayedRoutes),
            length(SortedDelayedRoutes, NumDelayedRoutes),
            format('Found ~w possible route(s) considering the delay:~n', [NumDelayedRoutes]),
            forall(member((Arr, Dur, Path, Vehs, Delays), SortedDelayedRoutes),
                   (min_to_ora(Arr, ArrFormatted),
                    format_vehicles(Vehs, VehicleStr),
                    format_delays(Delays, DelayStr),
                    format('  - Route: ~w via ~w~n    Arrival: ~w, Duration: ~w min (Delay info: ~w)~n',
                           [Path, VehicleStr, ArrFormatted, Dur, DelayStr])))
        ),
        nl,
        format('--- ANALYSIS OF UNAVAILABLE ORIGINAL ROUTES ---~n'),
        check_unavailable_routes(SortedOriginalRoutes, DelayedRoutes),
        nl,
        ( DelayedRoutesWithInfo = [] ->
            format('Answer: No alternative route could be found after the delay was applied.~n')
        ;
            SortedDelayedRoutes = [(BestArrMin, BestDur, BestPath, BestVehs, BestDelays)|_],
            min_to_ora(BestArrMin, BestArrFormatted),
            format_vehicles(BestVehs, BestVehicleStr),
            format_delays(BestDelays, BestDelayStr),
            format('--- 3. FINAL ANSWER AND SUMMARY ---~n'),
            format('The new best option is the route ~w via ~w.~n', [BestPath, BestVehicleStr]),
            format('  - New estimated arrival: ~w (Total duration: ~w min).~n', [BestArrFormatted, BestDur]),
            format('  - This route is affected by: ~w.~n', [BestDelayStr]),
            DifferenzaTempo is BestDur - OrigDuration,
            ( DifferenzaTempo > 0 ->
                format('  - Impact: This is ~w minutes slower than the original best option.~n', [DifferenzaTempo])
            ; DifferenzaTempo < 0 ->
                AbsDifferenza is abs(DifferenzaTempo),
                format('  - Impact: This is ~w minutes faster than the original best option.~n', [AbsDifferenza])
            ;
                format('  - Impact: The duration is the same as the original best option.~n')
            )
        ),
        rimuovi_ritardo(DelayedVehicle)
    ).
check_unavailable_routes([], _) :-
    format('All original routes were checked.~n').
    
check_unavailable_routes([OriginalRoute|Rest], DelayedRoutes) :-
    OriginalRoute = (_, _, Path, Vehs),
    ( \+ member((Path, Vehs), DelayedRoutes) ->
        format_vehicles(Vehs, VehicleStr),
        format('  - NOTE: The original route ~w via ~w is NO LONGER FEASIBLE due to a missed connection.~n', [Path, VehicleStr])
    ;
        true
    ),
    check_unavailable_routes(Rest, DelayedRoutes).

% Controlla se un singolo veicolo `Mezzo` deve essere evitato.
is_vehicle_forbidden(Mezzo, ListaEvitati) :-
    % Caso 1: L'istanza stessa è nella lista da evitare.
    member(Mezzo, ListaEvitati).
is_vehicle_forbidden(Mezzo, ListaEvitati) :-
    % Caso 2: Il tipo del mezzo è nella lista da evitare.
    tipo_mezzo(Mezzo, Tipo),
    member(Tipo, ListaEvitati).

% Una rotta è valida se per TUTTI i suoi mezzi, NESSUNO di essi è vietato.
route_respects_preferences(ListaEvitati, (_, _, _, Mezzi)) :-
    forall(member(Mezzo, Mezzi),
           \+ is_vehicle_forbidden(Mezzo, ListaEvitati)).

% Formattazione della lista di preferenze per la stampa.
format_preferences([], 'no specific vehicles').
format_preferences([Pref], Pref).
format_preferences(Prefs, Formattato) :- atomic_list_concat(Prefs, ' or ', Formattato).

solve_preference_task(From, To, DepartureTime, AvoidedItems) :-
    format('~n=== PREFERENCE-BASED REASONING TASK ===~n'),
    format_preferences(AvoidedItems, PrefStr),
    format('Question: Can a user reach the destination while avoiding ~w?~n', [PrefStr]),
    format('Route: ~w to ~w, planned departure after ~w~n~n', [From, To, DepartureTime]),
    format('Execution: Finding all routes and filtering based on user preferences.~n'),

    % 1. Tutte le rotte possibili
    tutti_percorsi(From, To, DepartureTime, AllRoutes),

    ( AllRoutes = [] ->
        format('~n--- ANALYSIS ---~n'),
        format('No routes found from ~w to ~w, regardless of preferences.~n', [From, To])
    ;
        
        include(route_respects_preferences(AvoidedItems), AllRoutes, ValidRoutes),

        format('~n--- 1. ANALYSIS OF AVAILABLE ROUTES ---~n'),
        ( ValidRoutes = [] ->
            length(AllRoutes, NumAllRoutes),
            format('Found ~w total route(s), but none of them satisfy the preference (avoid ~w).~n', [NumAllRoutes, PrefStr])
        ;
            sort(ValidRoutes, SortedValidRoutes),
            length(SortedValidRoutes, NumValidRoutes),
            format('Found ~w route(s) that satisfy the preference:~n', [NumValidRoutes]),
            forall(member((Arr, Dur, Path, Vehs), SortedValidRoutes),
                   (min_to_ora(Arr, ArrFormatted),
                    format_vehicles(Vehs, VehicleStr),
                    format('  - Route: ~w via ~w~n    Arrival: ~w, Duration: ~w min~n',
                           [Path, VehicleStr, ArrFormatted, Dur])))
        ),

        format('~n--- 2. FINAL ANSWER ---~n'),
        ( ValidRoutes = [] ->
            format('Answer: No, it is not possible to reach ~w from ~w avoiding ~w.~n', [To, From, PrefStr]),
            format('All available routes involve at least one of the selected transport types/vehicles.~n')
        ;
            SortedValidRoutes = [(BestArr, BestDur, BestPath, BestVehs)|_],
            min_to_ora(BestArr, BestArrFormatted),
            format_vehicles(BestVehs, BestVehicleStr),
            format('Answer: Yes, there is a route available that avoids ~w.~n', [PrefStr]),
            format('The best option is the route ~w via ~w.~n', [BestPath, BestVehicleStr]),
            format('  - Estimated arrival: ~w (Total duration: ~w min).~n', [BestArrFormatted, BestDur])
        )
    ).
