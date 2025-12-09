;; We start with Block A on top of Block B, and Block B is on the table.
;; The goal is to reverse this so that Block B is on top of Block A.

(define (problem blocks-swap)
  (:domain blocks)
  (:objects a b - block)
  (:init 
    (on-table b) 
    (on a b) 
    (clear a) 
    (handempty)
  )
  (:goal (and (on b a) (on-table a) (clear b)))
)