;; An agent starts at (1,1) in a 3x3 grid.
;; The goal is to reach (3,3).
;; There are no walls, testing simple movement logic.

;;   1 2 3
;; 1 A . .
;; 2 . . W
;; 3 . W G

(define (problem maze-3x3-open)
  (:domain maze-dir)
  (:objects 
    agent1 - agent
    p1 p2 p3 - position
  )
  (:init 
    ;; Define Grid Logic
    (inc p1 p2) (inc p2 p3)
    (dec p3 p2) (dec p2 p1)

    (wall p2 p3)
    (wall p3 p2)
    
    ;; Initial State
    (at agent1 p1 p1)
  )
  (:goal (at agent1 p3 p3))
)
