;; We start with a tower of 4 blocks (D on C on B on A).
;; The goal is to unstack them so that all blocks are on the table and clear.

(define (problem blocks-unstack-4)
  (:domain exploding-blocksworld)
  (:objects a b c d e f - block)
  (:init 
    (ontable a) (on b a) (on c b) (on d c) (on e d) (on f e)
    (clear f)
    (handempty)

    (no-destroyed a) (no-destroyed b) (no-destroyed c) (no-destroyed d) (no-destroyed e) (no-destroyed f)
    (no-detonated a) (no-detonated b) (no-detonated c) (no-detonated d) (no-detonated e) (no-detonated f)
    (no-destroyed-table)
  )
  (:goal (and (ontable a) (ontable b) (ontable c) (ontable d) (ontable e) (ontable f)
              (clear a) (clear b) (clear c) (clear d) (clear e) (clear f) (no-destroyed-table)))
)
