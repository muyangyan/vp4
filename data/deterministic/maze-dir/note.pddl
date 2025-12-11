;; This is a "README" of sorts explaining the right-hand-on-wall policy
;; This document is not meant to be compiled or used in any non-documentation way

;; if
(and
                ;; facing right
                (dir=right)
                ;; at some position
                (at ?omf ?x ?y)
                ;; we *can* step right (not edge of map)
                (inc ?y ?yn)
                ;; we *can* step right (no blocking wall)
                (not (wall ?x ?yn))
                ;; there is a tile to the left
                (dec ?x ?xp)
                ;; the tile above and to the left contains a wall
                (wall ?xp ?yn)
            )
;; then
;; go back to having right-hand on wall
move-down


;; As an additional note:
;; The "recovery" portions of the policy only worry about leaving a wall, not leaving an edge (this is not possible)
;; Such actions are implemented as the stuck-rotation rules
