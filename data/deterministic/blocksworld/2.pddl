;; We start with three blocks (A, B, C) all on the table.
;; The goal is to build a single tower with A on the bottom, B in the middle, and C on top.

(define (problem blocks-tower-3)
  (:domain blocks)
  (:objects a b c - block)
  (:init 
    (ontable a) (ontable b) (ontable c)
    (clear a) (clear b) (clear c)
    (handempty)
  )
  (:goal (and (on b a) (on c b) (clear c) (ontable a)))
)