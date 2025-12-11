;; An agent starts at (1,1) in a 3x3 grid.
;; The goal is to reach (3,3).
;; There are no walls, testing simple movement logic.

;;   1 2 3
;; 1 A . .
;; 2 . . .
;; 3 . . G

(define (problem maze-dir-3x3-open)
  (:domain maze-dir)
  (:objects 
    agent1 - agent
    x1 x2 x3 y1 y2 y3 - position
  )
  (:init 
    ;; Define Grid Logic
    (inc x1 x2) (inc x2 x3)
    (inc y1 y2) (inc y2 y3)
    (dec x3 x2) (dec x2 x1)
    (dec y3 y2) (dec y2 y1)
    
    ;; Initial State
    (at agent1 x1 y1)
    (dir_down)
  )
  (:goal (at agent1 x3 y3))
)
