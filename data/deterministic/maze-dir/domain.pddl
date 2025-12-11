;; maze with an agent-direction property
(define (domain maze-dir)
  (:requirements :strips)
  (:types agent position)
  (:predicates 
    (inc ?a ?b - position)
    (dec ?a ?b - position)
    (at ?a - agent ?x ?y - position)
    (wall ?x ?y)
    (dir_up) (dir_down) (dir_left) (dir_right)
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
                 (dir_up)
                 (not (dir_down))
                 (not (dir_left))
                 (not (dir_right))
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
                 (not (dir_up))
                 (dir_down)
                 (not (dir_left))
                 (not (dir_right))
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
                 (not (dir_up))
                 (not (dir_down))
                 (dir_left)
                 (not (dir_right))
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
                 (not (dir_up))
                 (not (dir_down))
                 (not (dir_left))
                 (dir_right)
            )
    )

  ;; actions to change the direction the agent is facing
  ;; Note: this can be avoided by setting the direction of the agent when attempting a move, but they are distinct in this definition
  (:action face-up
      :parameters ()
      :precondition ()
      :effect (and
                (dir_up)
                (not (dir_down))
                (not (dir_left))
                (not (dir_right))
                )
  )
  (:action face-down
      :parameters ()
      :precondition ()
      :effect (and
                (not (dir_up))
                (dir_down)
                (not (dir_left))
                (not (dir_right))
                )
  )
  (:action face-left
      :parameters ()
      :precondition ()
      :effect (and
                (not (dir_up))
                (not (dir_down))
                (dir_left)
                (not (dir_right))
                )
  )
  (:action face-right
      :parameters ()
      :precondition ()
      :effect (and
                (not (dir_up))
                (not (dir_down))
                (not (dir_left))
                (dir_right)
                )
  )
  
)
