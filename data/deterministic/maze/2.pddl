;; An agent starts at (1,1) in a 3p3 grid.
;; The goal is to reach (3,1).
;; There is a wall at (2,1), forcing the agent to go around it. 

;;   1 2 3
;; 1 A W G
;; 2 . . .
;; 3 . . .


(define (problem maze-3p3-obstacle)
  (:domain maze)
  (:objects 
    agent1 - agent
    p1 p2 p3 - position
  )
  (:init 
    (inc p1 p2) (inc p2 p3)
    (dec p3 p2) (dec p2 p1)
    
    ;; Wall at x=2, y=1
    (wall p2 p1)
    
    (at agent1 p1 p1)
  )
  (:goal (at agent1 p3 p1))
)
