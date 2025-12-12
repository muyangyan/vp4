;; We start with block A and block B on the table.
;; The goal is to stack block A on block B.
;; Putting blocks down or stacking them carries a risk of detonation. We assume all blocks start safe.

(define (problem exploding-stack-2)
  (:domain exploding-blocksworld)
  (:objects a b - block)
  (:init 
    (ontable a) (ontable b)
    (clear a) (clear b)
    (handempty)
    
    ;; Safety initialization
    (no-destroyed a) (no-destroyed b)
    (no-detonated a) (no-detonated b)
    (no-destroyed-table)
  )
  (:goal (and (on a b) (no-destroyed-table)))
)
