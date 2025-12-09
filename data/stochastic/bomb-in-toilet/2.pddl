;; There are 2 packages, but the bomb is much more likely to be in Package 1 (80%) than Package 2 (20%).
;; The goal is to defuse the bomb without clogging the toilet.

(define (problem bomb-toilet-weighted)
   (:domain bomb-and-toilet)
   (:requirements :negative-preconditions)
   (:objects p1 p2)
   (:init 
       (probabilistic 
           0.8 (bomb-in-package p1)
           0.2 (bomb-in-package p2)
       )
   )
   (:goal (and (bomb-defused) (not (toilet-clogged))))
)