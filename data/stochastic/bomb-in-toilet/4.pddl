;; There are 2 packages. The bomb is hidden in one of them with equal probability (1/2 each).
;; The goal is to defuse the bomb without clogging the toilet.

(define (problem bomb-and-toilet)
   (:domain bomb-and-toilet)
   (:requirements :negative-preconditions)
   (:objects package1 package2)
   (:init  (bomb-in-package package1))
   (:goal (and (bomb-defused) (not (toilet-clogged)))))