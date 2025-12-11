;; maze with an agent-direction property
(define (domain maze-dir)
  (:requirements :strips)
  (:types agent position)
  (:predicates 
    (inc ?a ?b - position)
    (dec ?a ?b - position)
    (at ?a - agent ?x ?y - position)
    (wall ?x ?y)
    (dir-up) (dir-down) (dir-left) (dir-right)
    )
   
  (:action 
    move-up
    :parameters (?omf - agent)
    :precondition (and (at ?omf ?x ?y)
                       (dec ?y ?yn)
                       (not (wall ?x ?yn))
                  )
    :effect (and (not (at ?omf ?x ?y))
                 (at ?omf ?x ?yn)
                 (dir-up)
                 (not (dir-down))
                 (not (dir-left))
                 (not (dir-right))
            )
  )

  (:action 
    move-down
    :parameters (?omf - agent)
    :precondition (and (at ?omf ?x ?y)
                       (inc ?y ?yn)
                       (not (wall ?x ?yn))
                  )
    :effect (and (not (at ?omf ?x ?y))
                 (at ?omf ?x ?yn)
                 (not (dir-up))
                 (dir-down)
                 (not (dir-left))
                 (not (dir-right))
            )
    )

  (:action 
    move-left
    :parameters (?omf - agent)
    :precondition (and (at ?omf ?x ?y)
                       (dec ?x ?xn)
                       (not (wall ?xn ?y)))
    :effect (and (not (at ?omf ?x ?y))
                 (at ?omf ?xn ?y)
                 (not (dir-up))
                 (not (dir-down))
                 (dir-left)
                 (not (dir-right))
            )
    )

  (:action 
    move-right
    :parameters (?omf - agent)
    :precondition (and (at ?omf ?x ?y)
                       (inc ?x ?xn)
                       (not (wall ?xn ?y))
                  )
    :effect (and (not (at ?omf ?x ?y))
                 (at ?omf ?xn ?y)
                 (not (dir-up))
                 (not (dir-down))
                 (not (dir-left))
                 (dir-right)
            )
    )

  ;; actions to change the direction the agent is facing
  ;; Note: this can be avoided by setting the direction of the agent when attempting a move, but they are distinct in this definition
  (:action face-up
      :parameters ()
      :precondition ()
      :effect (and
                (dir-up)
                (not (dir-down))
                (not (dir-left))
                (not (dir-right))
                )
  )
  (:action face-down
      :parameters ()
      :precondition ()
      :effect (and
                (not (dir-up))
                (dir-down)
                (not (dir-left))
                (not (dir-right))
                )
  )
  (:action face-left
      :parameters ()
      :precondition ()
      :effect (and
                (not (dir-up))
                (not (dir-down))
                (dir-left)
                (not (dir-right))
                )
  )
  (:action face-right
      :parameters ()
      :precondition ()
      :effect (and
                (not (dir-up))
                (not (dir-down))
                (not (dir-left))
                (dir-right)
                )
  )
  
)
