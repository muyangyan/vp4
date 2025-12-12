;; 5p5 maze as a counter-example for right-hand-on-wall technique

;;   1 2 3 4
;; 1 . . . .
;; 2 . . . .
;; 3 . W A .
;; 4 . . . G

(define (problem maze-dir-5p5)
  (:domain maze-dir)
  (:objects
       agent1 - agent
       p1 p2 p3 p4 - position
  )
  (:init
    (inc p1 p2) (inc p2 p3) (inc p3 p4)
    (dec p4 p3) (dec p3 p2) (dec p2 p1) 

    (wall p2 p3)

    (at agent1 p3 p3)
    (dir-down)
  )
  (:goal
    (at agent1 p4 p4))
  )
