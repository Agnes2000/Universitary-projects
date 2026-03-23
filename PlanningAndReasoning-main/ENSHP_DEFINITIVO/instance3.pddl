(define (problem transport-delay-avoid-complex-v2)
  (:domain transport)

  (:objects
    user - person
    stop-a stop-b stop-c stop-d stop-e stop-f stop-g stop-h stop-i stop-j - stop
    tram1 tram2 metro1 metro2 bus1 bus2 - vehicle
  )

  (:init
    (at user stop-a)

    ;; posizioni iniziali veicoli
    (vehicle-at tram1 stop-a)
    (vehicle-at tram2 stop-a)
    (vehicle-at metro1 stop-c)
    (vehicle-at metro2 stop-e)
    (vehicle-at bus1 stop-b)
    (vehicle-at bus2 stop-f)

    ;; percorsi
    (can-travel tram1 stop-a stop-b)
    (can-travel tram1 stop-b stop-c)
    (can-travel tram1 stop-c stop-d)

    (can-travel tram2 stop-a stop-d)
    (can-travel tram2 stop-d stop-e)
    (can-travel tram2 stop-e stop-f)

    (can-travel metro1 stop-c stop-f)
    (can-travel metro1 stop-f stop-g)
    (can-travel metro1 stop-g stop-h)

    (can-travel metro2 stop-e stop-g)
    (can-travel metro2 stop-g stop-i)

    (can-travel bus1 stop-b stop-f)
    (can-travel bus1 stop-f stop-j)

    (can-travel bus2 stop-f stop-h)
    (can-travel bus2 stop-h stop-i)

    ;; tempi di viaggio (in minuti)
    (= (travel-time tram1 stop-a stop-b) 3)
    (= (travel-time tram1 stop-b stop-c) 3)
    (= (travel-time tram1 stop-c stop-d) 4)

    (= (travel-time tram2 stop-a stop-d) 2)
    (= (travel-time tram2 stop-d stop-e) 2)
    (= (travel-time tram2 stop-e stop-f) 3)

    (= (travel-time metro1 stop-c stop-f) 4)
    (= (travel-time metro1 stop-f stop-g) 3)
    (= (travel-time metro1 stop-g stop-h) 5)

    (= (travel-time metro2 stop-e stop-g) 5)
    (= (travel-time metro2 stop-g stop-i) 4)

    (= (travel-time bus1 stop-b stop-f) 6)
    (= (travel-time bus1 stop-f stop-j) 3)

    (= (travel-time bus2 stop-f stop-h) 4)
    (= (travel-time bus2 stop-h stop-i) 2)

    ;; orari di partenza
    (= (departure-time tram1 stop-a) 2)
    (= (departure-time tram1 stop-b) 5)
    (= (departure-time tram1 stop-c) 8)

    (= (departure-time tram2 stop-a) 2)
    (= (departure-time tram2 stop-d) 4)
    (= (departure-time tram2 stop-e) 6)

    (= (departure-time metro1 stop-c) 9)
    (= (departure-time metro1 stop-f) 13)
    (= (departure-time metro1 stop-g) 16)

    (= (departure-time metro2 stop-e) 10)
    (= (departure-time metro2 stop-g) 15)

    (= (departure-time bus1 stop-b) 7)
    (= (departure-time bus1 stop-f) 13)

    (= (departure-time bus2 stop-f) 14)
    (= (departure-time bus2 stop-h) 18)

    ;; ritardi (delay in minuti)
    (= (delay tram2) 5)   
    (= (delay metro2) 2)  
    (= (delay tram1) 0)
    (= (delay metro1) 0)
    (= (delay bus1) 1)
    (= (delay bus2) 3)

    ;; disponibilità
    (available tram1)
    (available tram2)
    (available metro1)
    (available metro2)
    (available bus1)
    (available bus2)

    ;; preferenze: evita tram2
    (avoid user tram2)  

    ;; inizializzazione fluente
    (= (total-time) 0)
  )

  (:goal (at user stop-j))
  (:metric minimize (total-time))
)
