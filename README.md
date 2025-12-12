# Verifying Properties of Probabilistic Planning Policies

Running MDP version:
prism bomb-in-toilet-mdp.prism -pctl $'Pmax=? [F bomb_defused & !toilet_clogged]'
or for the encoded "goal",
prism bomb-in-toilet-mdp.prism -pctl $'Pmax=? [F bomb_defused & !toilet_clogged]'

Running DTMC version (using the "goal" as the property):
prism bomb-in-toilet.dtmc -pctl $'P=? [F "goal"]'


To run maze examples (only successfully tested on 3x3's!):
- Generate the `dtmc.prism` for the maze: `python3 run.py data/deterministic/maze-dir/ 2.pddl right_hand_on_wall_split.json goal.pctl generate-dtmc-only`
- Prune the unnecessary transitions: `./proof_of_concepts/clean.sh tmp/dtmc.prism`
- Manually run PRISM (with additional memory, if needed): `prism tmp/dtmc.prism -pctl $'P=? [ F "goal" ]' -cuddmaxmem 16g`
- Optionally time the output (and/or print verbose logs): `/usr/bin/time prism tmp/dtmc.prism -pctl $'P=? [ F "goal" ]' -v -cuddmaxmem 16g`

If policy does not propose an applicable action, we are just stuck. No contingencies.
