;; We have Block A on Block B.
;; The goal is to move Block A to the table.
;; Putting blocks down or stacking them carries a risk of detonation. We assume all blocks start safe.

(define (problem exploding-unstack)
  (:domain exploding-blocksworld)
  (:objects a b - block)
  (:init 
    (on a b) (on-table b)
    (clear a)
    (emptyhand)
    
    (no-destroyed a) (no-destroyed b)
    (no-detonated a) (no-detonated b)
    (no-destroyed-table)
  )
  (:goal (and (on-table a) (on-table b)))
)