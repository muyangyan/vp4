;; goal: score a yahtzee in the single-reroll domain
(define (problem yahtzee-single-reroll-instance)
  (:domain yahtzee-single-reroll-single-shot)

  (:init)

  (:goal
    (and
      (rolled)
      (rerolled1) (rerolled2) (rerolled3) (rerolled4) (rerolled5)
      (or
        (and (d1=1) (d2=1) (d3=1) (d4=1) (d5=1))
        (and (d1=2) (d2=2) (d3=2) (d4=2) (d5=2))
        (and (d1=3) (d2=3) (d3=3) (d4=3) (d5=3))
        (and (d1=4) (d2=4) (d3=4) (d4=4) (d5=4))
        (and (d1=5) (d2=5) (d3=5) (d4=5) (d5=5))
        (and (d1=6) (d2=6) (d3=6) (d4=6) (d5=6))
      )
    )
  )
)
