;; We start with a tower of 4 blocks (D on C on B on A).
;; The goal is to unstack them so that all blocks are on the table and clear.

(define (problem blocks-unstack-4)
  (:domain exploding-blocksworld)
  (:objects a b c d e f - block)
  (:init 
    (ontable a) (clear a) (no-destroyed a) (no-detonated a)
    (ontable b) (clear b) (no-destroyed b) (no-detonated b)
    (ontable c) (clear c) (no-destroyed c) (no-detonated c)
    (ontable d) (clear d) (no-destroyed d) (no-detonated d)
    (ontable e) (clear e) (no-destroyed e) (no-detonated e)
    (ontable f) (clear f) (no-destroyed f) (no-detonated f)

    (handempty)
    (no-destroyed-table)
  )
  (:goal (and (ontable a) (on b a) (on c b) (on d c) (on e d) (on f e)
              (clear f) (no-destroyed-table)))
)
