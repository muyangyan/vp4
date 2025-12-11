;; An agent starts at (1,1) in a 3x3 grid.
;; The goal is to reach (3,1).
;; There is a wall at (2,1), forcing the agent to go around it. 

;;   1 2 3
;; 1 A W G
;; 2 . . .
;; 3 . . .


(define (problem maze-3x3-obstacle)
  (:domain maze)
  (:objects 
    agent1 - agent
    x1 x2 x3 y1 y2 y3 - position
  )
  (:init 
    (inc x1 x2) (inc x2 x3)
    (inc y1 y2) (inc y2 y3)
    (dec x3 x2) (dec x2 x1)
    (dec y3 y2) (dec y2 y1)
    
    ;; Wall at x=2, y=1
    (wall x2 y1)
    
    (at agent1 x1 y1)
  )
  (:goal (at agent1 x3 y1))
)
