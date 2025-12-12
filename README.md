# Verifying Properties of Probabilistic Planning Policies (VP4)

vp4 verifies properties about a policy on input PDDL domains and problems using PRISM.

## Usage

To run vp4, call

```bash
python3 main.py path/to/domain
```

This will evaluate each combination of properties, policies, and problems over the specified domain. The expected directory structure is:

```text
path/to/domain
| - domain.pddl       --> The domain
| - 1.pddl            --> The problem instance(s)
| - 2.pddl
| - 3.pddl
| - policy_name.json  --> The policy file(s)
| - other_policy.json
| - goal.pctl         --> The property file(s)
| - liveness.pctl
| - sample.pctl
```

To only compile the MDP and DTMC (e.g. to manually inspect or run the output), run

```bash
python3 run.py path/to/domain/ problem.pddl policy.json property.pctl generate-dtmc-only
```

(Note: the property passed will be ignored, as it is applied in the PRISM runtime.)

To run the generated dtmc (in `tmp/dtmc.prism`), run

```bash
prism tmp/dtmc.prism -pctl $'P=? [ <your_PCTL_query> ]'
```

A common PCTL query may be `F "goal"`, as a goal is defined in every input problem.

## Installation

vp4 uses external Python dependencies. For this, install the required packages in `requirements.txt` (e.g. `pip3 install -r requirements.txt`).

vp4 additionally requires PRISM to be installed. See [PRISM Manual | Installing PRISM ](https://www.prismmodelchecker.org/manual/InstallingPRISM/Instructions) for instructions to install PRISM.

## Additional Tools

In response to the "combinatorial explosion" of predicates encountered by this technique, a proof-of-concept tool was created to deflate the generated DTMC's for the `deterministic/maze` domain.

To run maze examples:
- Generate the `dtmc.prism` for the maze: `python3 run.py data/deterministic/maze-dir/ 2.pddl right_hand_on_wall_split.json goal.pctl generate-dtmc-only`
- Deflate DTMC: `./proof_of_concepts/clean.sh tmp/dtmc.prism`
- Manually run PRISM (with additional memory, as needed): `prism tmp/dtmc.prism -pctl $'P=? [ F "goal" ]' -cuddmaxmem 16g`

## Additional Information

This project is the result of a group project for CS 560: Reasoning About Programs (Fall 2025) at Purdue University.
