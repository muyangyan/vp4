;; adapted from: https://github.com/SoarGroup/Domains-Planning-Domain-Definition-Language/blob/master/pddl/maze6p6.pddl

;; 6p6 maze

;;   1 2 3 4 5 6
;; 1 A . . . . .
;; 2 . . . . . .
;; 3 W W W W . .
;; 4 . . G . W .
;; 5 . W W W . .
;; 6 . . . . . .

(define (problem maze-6p6)
  (:domain maze)
  (:objects
       agent1 - agent
       p1 p2 p3 p4 p5 p6 - position
  )
  (:init
    (inc p1 p2) (inc p2 p3) (inc p3 p4) (inc p4 p5) (inc p5 p6)
    (dec p6 p5) (dec p5 p4) (dec p4 p3) (dec p3 p2) (dec p2 p1) 

    (wall p1 p3) (wall p2 p3) (wall p3 p3) (wall p4 p3)
    (wall p5 p4)
    (wall p2 p5) (wall p3 p5) (wall p4 p5)

    (at agent1 p1 p1))
  (:goal
    (at agent1 p3 p4))
  )
