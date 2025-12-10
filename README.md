# Verifying Properties of Probabilistic Planning Policies

Running MDP version:
prism bomb-in-toilet-mdp.prism -pctl $'Pmax=? [F bomb_defused & !toilet_clogged]'
or for the encoded "goal",
prism bomb-in-toilet-mdp.prism -pctl $'Pmax=? [F bomb_defused & !toilet_clogged]'

Running DTMC version (using the "goal" as the property):
prism bomb-in-toilet.dtmc -pctl $'P=? [F "goal"]'



if policy does not propose an applicable action, we are just stuck. no contingencies.

Note:
Current implementation of `verify_property` uses a call to `subprocess.run()`, which is inherently unsafe. Do not run this code on inputs you do not trust!
