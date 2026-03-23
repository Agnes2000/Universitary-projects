(define (problem basic-route)
  (:domain transport)

  (:objects
    user - person
    stop-a stop-b stop-c stop-d - stop
    bus1 - vehicle
  )

  (:init
    (at user stop-a)
    (vehicle-at bus1 stop-a)
    (available bus1)
    
    (= (departure-time bus1 stop-a) 0)
    (can-travel bus1 stop-a stop-b) (= (travel-time bus1 stop-a stop-b) 5) 
    (= (departure-time bus1 stop-b) 5)
    (can-travel bus1 stop-b stop-c) (= (travel-time bus1 stop-b stop-c) 4)
    (= (departure-time bus1 stop-c) 9) 
    (can-travel bus1 stop-c stop-d) (= (travel-time bus1 stop-c stop-d) 2)

    ; Inizializzazione dei fluenti 
    (= (total-time) 0)

    (= (delay bus1) 0)

  )

  (:goal
    (at user stop-d)
  )
    (:metric minimize (total-time))
)
