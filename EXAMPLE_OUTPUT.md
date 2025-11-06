# Example PRISM Verification Output

This document shows what the verification results would look like when running PRISM on the grid world MDP.

## Model Statistics

```
Type:        MDP
Modules:     agent 
Variables:   x y at_goal at_hazard 
States:      66 (1 initial)
Transitions: 264
Choices:     132
```

## Property Verification Results

### Property 1: Maximum probability of reaching the goal
```
Pmax=? [ F goal ]
Result: 0.9823529411764706 (exact rational: 167/170)
```
**Interpretation**: Under the optimal policy, the agent reaches the goal with ~98.24% probability.

---

### Property 2: Minimum probability of reaching the goal
```
Pmin=? [ F goal ]
Result: 0.0
```
**Interpretation**: There exists a policy (worst case) where the agent never reaches the goal (e.g., moving away or hitting hazards).

---

### Property 3: Maximum probability of reaching goal while staying safe
```
Pmax=? [ safe U goal ]
Result: 0.9823529411764706
```
**Interpretation**: The optimal policy can reach the goal while avoiding hazards with ~98.24% probability.

---

### Property 4: Minimum probability of hitting a hazard
```
Pmin=? [ F hazard ]
Result: 0.0
```
**Interpretation**: There exists a policy that can avoid all hazards completely.

---

### Property 5: Expected steps to reach goal (optimal policy)
```
R{"steps"}min=? [ F goal ]
Result: 8.235294117647058
```
**Interpretation**: Under the optimal policy, it takes on average ~8.24 steps to reach the goal.

---

### Property 6: Maximum expected total reward
```
R{"goal_reward"}max=? [ F (goal | hazard) ]
Result: 98.23529411764706
```
**Interpretation**: Expected reward considering +100 for goal and -50 for hazards.

---

### Property 7: Probability of reaching goal within 20 steps
```
Pmax=? [ F<=20 goal ]
Result: 0.9823529411764706
```
**Interpretation**: The optimal policy reaches the goal within 20 steps with ~98.24% probability.

---

### Property 8: Goal reachable with P ≥ 0.9?
```
Pmax>=0.9 [ F goal ]
Result: true
```
**Interpretation**: Yes, the goal can be reached with at least 90% probability.

---

### Property 9: Expected hazard penalties
```
R{"hazard_penalty"}min=? [ F (goal | hazard) ]
Result: -0.8823529411764706
```
**Interpretation**: Under the optimal policy, expected penalty from hazards is ~-0.88.

---

### Property 10: Maximum probability of reaching terminal state
```
Pmax=? [ F (goal | hazard) ]
Result: 1.0
```
**Interpretation**: The agent always eventually reaches either the goal or a hazard.

---

## Optimal Policy Visualization

The optimal policy for maximizing the probability of reaching the goal:

```
Grid Layout:
+---+---+---+---+
| S | → | → | ↑ |  Row 3
+---+---+---+---+
| ↑ | H | H | ↑ |  Row 2
+---+---+---+---+
| ↑ | H | ↑ | ↑ |  Row 1
+---+---+---+---+
| ↑ | ↑ | ↑ | G |  Row 0
+---+---+---+---+
Col 0   1   2   3

Legend:
S = Start (0,0)
G = Goal (3,3)
H = Hazard (1,1) and (2,2)
Arrows = Optimal action in that state
```

### State-Action Policy Table

```
State (x,y) | Optimal Action | Goal Probability
------------|----------------|------------------
(0,0)       | east          | 0.9824
(1,0)       | east          | 0.9824
(2,0)       | east          | 0.9824
(3,0)       | north         | 0.9824
(0,1)       | north         | 0.9824
(1,1)       | (hazard)      | 0.0
(2,1)       | north         | 0.9824
(3,1)       | north         | 0.9824
(0,2)       | north         | 0.9824
(1,2)       | north         | 0.9824
(2,2)       | (hazard)      | 0.0
(3,2)       | north         | 0.9824
(0,3)       | east          | 0.9824
(1,3)       | east          | 0.9824
(2,3)       | east          | 0.9824
(3,3)       | (goal)        | 1.0
```

---

## Policy Analysis

### Key Insights:

1. **Optimal Strategy**: Move primarily east and north to reach (3,3)
2. **Hazard Avoidance**: The policy naturally routes around hazards due to the high probability of reaching the goal
3. **Robustness**: Even with 20% movement uncertainty, success rate is 98.24%
4. **Efficiency**: Average of 8.24 steps (vs 6 steps optimal deterministic path)

### Risk Assessment:

- **Hazard Risk**: Only ~1.76% chance of hitting a hazard
- **Slippage Impact**: Perpendicular slips add ~2.24 expected steps
- **Path Variance**: Due to stochastic transitions, actual paths vary

### Policy Characteristics:

- **Memoryless**: Action depends only on current state (x,y)
- **Deterministic**: Each state has a single best action
- **Optimal**: Maximizes probability of goal reachability
- **Stationary**: Policy doesn't change over time

---

## Generated Policy Files

### gridworld_policy.txt
Contains the optimal action for each state in format:
```
0:(0,0,false,false)=east
1:(1,0,false,false)=east
2:(2,0,false,false)=east
...
```

### gridworld_adversary.tra
Contains the induced DTMC (Discrete-Time Markov Chain) when following the optimal policy:
```
0 1 0.8
0 2 0.1
0 3 0.1
...
```
Each line: source_state target_state probability

---

## Verification Statistics

- **Model building time**: ~0.5 seconds
- **Property verification time**: ~0.2 seconds per property
- **Memory usage**: ~10 MB
- **State space exploration**: Complete (all 66 states)

---

## Alternative Policies

### Conservative Policy (Minimize Hazard Risk)
```
Pmin=? [ F hazard ]
Result: 0.0
```
This policy completely avoids hazards by routing far around them, though it may take more steps.

### Aggressive Policy (Minimize Steps)
```
R{"steps"}min=? [ F goal ]
Result: 8.235294117647058
```
This is the same as the goal-maximizing policy in this case, as the optimal path balances speed and safety.

---

## Sensitivity Analysis

If we increased the hazard penalty from -50 to -100:
- Policy might route further around hazards
- Goal-reaching probability might decrease slightly
- Expected steps might increase

If we increased movement accuracy from 80% to 90%:
- Goal-reaching probability would increase
- Expected steps would decrease
- Policy might take more direct paths

---

## Model Checking Command Reference

```bash
# Verify all properties
prism gridworld.prism gridworld.props

# Export optimal strategy
prism gridworld.prism -pf 'Pmax=? [ F goal ]' -exportstrat policy.txt

# Model check with specific property
prism gridworld.prism -pctl 'Pmax=? [ F goal ]'

# Generate counterexamples
prism gridworld.prism -pctl 'Pmax<0.5 [ F hazard ]'

# Simulate the model
prism gridworld.prism -sim -simpath 100 policy.txt
```

