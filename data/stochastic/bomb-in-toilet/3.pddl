;; There are 5 packages. The bomb is hidden in one of them with equal probability (1/5 each).
;; The goal is to defuse the bomb without clogging the toilet.

(define (problem bomb-and-toilet)
   (:domain bomb-and-toilet)
   (:requirements :negative-preconditions)
   (:objects package1 package2 package3 package4 package5)
   (:init (probabilistic 0.2 (bomb-in-package package1)
                         0.2 (bomb-in-package package2)
                         0.2 (bomb-in-package package3)
                         0.2 (bomb-in-package package4)
                         0.2 (bomb-in-package package5)))
   (:goal (and (bomb-defused) (not (toilet-clogged)))))
