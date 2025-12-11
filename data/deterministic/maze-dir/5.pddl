;; 5x5 maze as a counter-example for right-hand-on-wall technique

;;   1 2 3 4 5
;; 1 . . . . .
;; 2 . . . . .
;; 3 . . W A G
;; 4 . . . . .
;; 5 . . . . .

(define (problem maze-dir-5x5)
  (:domain maze-dir)
  (:objects
       agent1 - agent
       x1 x2 x3 x4 x5 y1 y2 y3 y4 y5 - position
  )
  (:init
    (inc x1 x2) (inc x2 x3) (inc x3 x4) (inc x4 x5)
    (inc y1 y2) (inc y2 y3) (inc y3 y4) (inc y4 y5)
    (dec x5 x4) (dec x4 x3) (dec x3 x2) (dec x2 x1) 
    (dec y5 y4) (dec y4 y3) (dec y3 y2) (dec y2 y1) 

    (wall x3 y3)

    (at agent1 x4 y3)
    (dir-down)
  )
  (:goal
    (at agent1 x5 y3))
  )
