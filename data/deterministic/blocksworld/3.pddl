;; We start with a tower of 4 blocks (D on C on B on A).
;; The goal is to unstack them so that all blocks are on the table and clear.

(define (problem blocks-unstack-4)
  (:domain blocks)
  (:objects a b c d - block)
  (:init 
    (ontable a) (on b a) (on c b) (on d c)
    (clear d)
    (handempty)
  )
  (:goal (and (ontable a) (ontable b) (ontable c) (ontable d)
              (clear a) (clear b) (clear c) (clear d)))
)