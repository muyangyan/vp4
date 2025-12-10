(define (domain yahtzee-single-reroll-single-shot)
  (:requirements :probabilistic-effects :conditional-effects)

  ;; Dice positions
  (:predicates
     (rolled)
     (rerolled1) (rerolled2) (rerolled3) (rerolled4) (rerolled5)
     (d1=1) (d1=2) (d1=3) (d1=4) (d1=5) (d1=6)
     (d2=1) (d2=2) (d2=3) (d2=4) (d2=5) (d2=6)
     (d3=1) (d3=2) (d3=3) (d3=4) (d3=5) (d3=6)
     (d4=1) (d4=2) (d4=3) (d4=4) (d4=5) (d4=6)
     (d5=1) (d5=2) (d5=3) (d5=4) (d5=5) (d5=6)
  )

  ;; Initial full roll of all dice
  (:action roll-initial
     :precondition (not (rolled))
     :effect (and
         (rolled)
         (probabilistic
            1.0
            (and
              ;; d1
              (probabilistic
                1/6 (d1=1) 1/6 (d1=2) 1/6 (d1=3)
                1/6 (d1=4) 1/6 (d1=5) 1/6 (d1=6))
              ;; d2
              (probabilistic
                1/6 (d2=1) 1/6 (d2=2) 1/6 (d2=3)
                1/6 (d2=4) 1/6 (d2=5) 1/6 (d2=6))
               ;; d3
              (probabilistic
                1/6 (d3=1) 1/6 (d3=2) 1/6 (d3=3)
                1/6 (d3=4) 1/6 (d3=5) 1/6 (d3=6))
               ;; d4
              (probabilistic
                1/6 (d4=1) 1/6 (d4=2) 1/6 (d4=3)
                1/6 (d4=4) 1/6 (d4=5) 1/6 (d4=6))
               ;; d5
              (probabilistic
                1/6 (d5=1) 1/6 (d5=2) 1/6 (d5=3)
                1/6 (d5=4) 1/6 (d5=5) 1/6 (d5=6))
            )
         )
     )
  )

  ;; Reroll actions: one per die
  (:action reroll-d1
     :precondition (and (rolled) (not (rerolled1)))
     :effect (and
         (rerolled1)
         ;; clear d1 first
         (not (d1=1)) (not (d1=2)) (not (d1=3))
         (not (d1=4)) (not (d1=5)) (not (d1=6))
         ;; reassign
         (probabilistic
            1/6 (d1=1) 1/6 (d1=2) 1/6 (d1=3)
            1/6 (d1=4) 1/6 (d1=5) 1/6 (d1=6))
     )
  )
  (:action decline-reroll-d1
    :precondition (and (rolled) (not (rerolled1)))
    :effect (rerolled1)
  )

  (:action reroll-d2
     :precondition (and (rolled) (not (rerolled2)))
     :effect (and
         (rerolled2)
         ;; clear d2 first
         (not (d2=1)) (not (d2=2)) (not (d2=3))
         (not (d2=4)) (not (d2=5)) (not (d2=6))
         ;; reassign
         (probabilistic
            1/6 (d2=1) 1/6 (d2=2) 1/6 (d2=3)
            1/6 (d2=4) 1/6 (d2=5) 1/6 (d2=6))
     )
  )
  (:action decline-reroll-d2
    :precondition (and (rolled) (not (rerolled2)))
    :effect (rerolled2)
  )
  
  (:action reroll-d3
     :precondition (and (rolled) (not (rerolled3)))
     :effect (and
         (rerolled3)
         ;; clear d3 first
         (not (d3=1)) (not (d3=2)) (not (d3=3))
         (not (d3=4)) (not (d3=5)) (not (d3=6))
         ;; reassign
         (probabilistic
            1/6 (d3=1) 1/6 (d3=2) 1/6 (d3=3)
            1/6 (d3=4) 1/6 (d3=5) 1/6 (d3=6))
     )
  )
  (:action decline-reroll-d3
    :precondition (and (rolled) (not (rerolled3)))
    :effect (rerolled3)
  )

  (:action reroll-d4
     :precondition (and (rolled) (not (rerolled4)))
     :effect (and
         (rerolled4)
         ;; clear d4 first
         (not (d4=1)) (not (d4=2)) (not (d4=3))
         (not (d4=4)) (not (d4=5)) (not (d4=6))
         ;; reassign
         (probabilistic
            1/6 (d4=1) 1/6 (d4=2) 1/6 (d4=3)
            1/6 (d4=4) 1/6 (d4=5) 1/6 (d4=6))
     )
  )
  (:action decline-reroll-d4
    :precondition (and (rolled) (not (rerolled4)))
    :effect (rerolled4)
  )

  (:action reroll-d5
     :precondition (and (rolled) (not (rerolled5)))
     :effect (and
         (rerolled5)
         ;; clear d5 first
         (not (d5=1)) (not (d5=2)) (not (d5=3))
         (not (d5=4)) (not (d5=5)) (not (d5=6))
         ;; reassign
         (probabilistic
            1/6 (d5=1) 1/6 (d5=2) 1/6 (d5=3)
            1/6 (d5=4) 1/6 (d5=5) 1/6 (d5=6))
     )
  )
  (:action decline-reroll-d5
    :precondition (and (rolled) (not (rerolled5)))
    :effect (rerolled5)
  )

)
