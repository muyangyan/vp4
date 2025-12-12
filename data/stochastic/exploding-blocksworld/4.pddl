;; We start with Block A in hand, and Block B is on the table.
;; The goal is to put Block B is on top of Block A.

(define (problem blocks-swap)
  (:domain exploding-blocksworld)
  (:objects a b - block)
  (:init 
    (ontable b) 
    (clear b) 
    (holding a)
  )
  (:goal (and (on b a) (ontable a) (clear b) (no-destroyed-table)))
)
