(define (problem transport-network)
  (:domain transport)
  (:objects user - person 
            stop-a stop-b stop-c stop-d - stop 
            bus1 bus2 metro1 - vehicle)
(:init
  ;; Posizione iniziale utente
  (at user stop-a)

  ;; Posizioni iniziali veicoli
  (vehicle-at bus1 stop-a)
  (vehicle-at bus2 stop-a)
  (vehicle-at metro1 stop-b)
  (available bus1)
  (available bus2)
  (available metro1)

  ;; Connessioni BUS1: A->B->C
  (can-travel bus1 stop-a stop-b)
  (can-travel bus1 stop-b stop-c)
  (= (travel-time bus1 stop-a stop-b) 8)
  (= (travel-time bus1 stop-b stop-c) 10)
  (= (departure-time bus1 stop-a) 30)   ;; spostato molto più tardi
  (= (departure-time bus1 stop-b) 25)   ;; arriva alle 25, parte subito

  ;; Connessioni BUS2: A->D->C
  (can-travel bus2 stop-a stop-d)
  ;(can-travel bus2 stop-d stop-c)
  (= (travel-time bus2 stop-a stop-d) 3)  ;; più veloce da A a D
  (= (travel-time bus2 stop-d stop-c) 4)  ;; più veloce da D a C
  (= (departure-time bus2 stop-a) 5)      ;; parte presto
  (= (departure-time bus2 stop-d) 8)     ;; arriva alle 12, parte subito

  ;; Connessioni METRO1: B->D e D->C (aggiunta D->C)
  (can-travel metro1 stop-b stop-d)
  (can-travel metro1 stop-d stop-c)
  (= (travel-time metro1 stop-b stop-d) 3)
  (= (travel-time metro1 stop-d stop-c) 2) ;; tempo breve da D a C
  (= (departure-time metro1 stop-b) 9)     ;; parte presto da B
  (= (departure-time metro1 stop-d) 12)    ;; parte presto da D

  (= (delay metro1) 0)
  (= (delay bus1) 0)
  (= (delay bus2) 0)


  ;; Tempo iniziale
  (= (total-time) 0)
)

    
  (:goal (at user stop-c))
  (:metric minimize (total-time)))
