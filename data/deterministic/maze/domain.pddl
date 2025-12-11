(define (domain maze)
  (:requirements :strips)
  (:types agent position)
  (:predicates 
    (inc ?a ?b - position)
    (dec ?a ?b - position)
    (at ?a - agent ?x ?y - position)
    (wall ?x ?y - position)
    )
   
  (:action 
    move-up
    :parameters (?omf - agent ?x ?y ?yn - position)
    :precondition (and (at ?omf ?x ?y)
                       (dec ?y ?yn)
                       (not (wall ?x ?yn))
                  )
    :effect (and (not (at ?omf ?x ?y))
                 (at ?omf ?x ?yn)
            )
  )

  (:action 
    move-down
    :parameters (?omf - agent ?x ?y ?yn - position)
    :precondition (and (at ?omf ?x ?y)
                       (inc ?y ?yn)
                       (not (wall ?x ?yn))
                  )
    :effect (and (not (at ?omf ?x ?y))
                 (at ?omf ?x ?yn)
            )
    )

  (:action 
    move-left
    :parameters (?omf - agent ?x ?y ?xn - position)
    :precondition (and (at ?omf ?x ?y)
                       (dec ?x ?xn)
                       (not (wall ?xn ?y)))
    :effect (and (not (at ?omf ?x ?y))
                 (at ?omf ?xn ?y)
            )
    )

  (:action 
    move-right
    :parameters (?omf - agent ?x ?y ?xn - position)
    :precondition (and (at ?omf ?x ?y)
                       (inc ?x ?xn)
                       (not (wall ?xn ?y))
                  )
    :effect (and (not (at ?omf ?x ?y))
                 (at ?omf ?xn ?y)
            )
    )

  )
