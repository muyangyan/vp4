# PRISM Model Checker - MDP Policy Verification Guide

## Overview

This repository demonstrates using the **PRISM model checker** to verify policies in Markov Decision Processes (MDPs). PRISM is a probabilistic model checker that can analyze MDPs, DTMCs, CTMCs, and other stochastic models.

## What is Policy Verification?

In an MDP:
- **States**: Represent configurations of the system
- **Actions**: Available choices in each state  
- **Transitions**: Probabilistic outcomes of actions
- **Policy**: A strategy that selects actions in each state
- **Verification**: Proving that a policy satisfies certain properties

PRISM can:
1. **Compute optimal policies** that maximize/minimize objectives
2. **Verify properties** using temporal logic (PCTL)
3. **Calculate probabilities** of reaching goal states
4. **Determine expected rewards/costs** under optimal strategies

## MDP Models in This Repository

### 1. Simple MDP (`simple_mdp.prism`)
- **Grid**: 3×3 deterministic grid
- **Goal**: Reach position (2,2) from (0,0)
- **Actions**: up, down, left, right (deterministic)
- **Use case**: Learning PRISM basics, understanding policy structure

**Expected Results**:
- P[reach goal] = 1.0 (deterministic)
- Min steps = 4 (Manhattan distance)
- Optimal policy: Go right 2 times, then up 2 times

### 2. Stochastic MDP (`stochastic_mdp.prism`)
- **Grid**: 3×3 with stochastic movements
- **Goal**: Reach (2,2) from (0,0)
- **Hazard**: Position (1,1) - causes crash
- **Actions**: up, down, left, right
- **Stochasticity**: 90% intended direction, 10% slip to perpendicular
- **Use case**: Realistic planning under uncertainty

**Expected Results**:
- P[reach goal] ≈ 0.90-0.95
- P[hit hazard] ≈ 0.05-0.10
- Expected steps ≈ 5-6
- Optimal policy: Route around hazard

### 3. Grid World MDP (`gridworld.prism`)
- **Grid**: 4×4 with stochastic movements
- **Goal**: Reach (3,3) from (0,0)
- **Hazards**: Positions (1,1) and (2,2)
- **Actions**: north, south, east, west
- **Stochasticity**: 80% intended, 10% left, 10% right slip
- **Use case**: More complex navigation with multiple hazards

## PRISM Installation

### Quick Install
```bash
./install_prism.sh
```

### Manual Install
1. Download PRISM from: https://www.prismmodelchecker.org/download.php
2. Extract: `tar -xzf prism-4.8.1-linux64-x86.tar.gz`
3. Add to PATH: `export PATH=$PATH:/path/to/prism/bin`
4. Verify: `prism -version`

### Requirements
- Java Runtime Environment (JRE)
- Linux, macOS, or Windows

## Running Verification

### Using the Script
```bash
./verify_policy.sh
```

### Manual Commands

**Build and analyze a model**:
```bash
prism simple_mdp.prism -build
```

**Verify all properties**:
```bash
prism simple_mdp.prism simple_mdp.props
```

**Verify single property**:
```bash
prism simple_mdp.prism -pctl 'Pmax=? [ F goal ]'
```

**Export optimal policy**:
```bash
prism stochastic_mdp.prism \
  -pf 'Pmax=? [ F goal ]' \
  -exportstrat policy.txt \
  -exportstrattype actions
```

**Export induced DTMC**:
```bash
prism stochastic_mdp.prism \
  -pf 'Pmax=? [ F goal ]' \
  -exportadv adversary.tra
```

## Understanding PRISM Output

### Model Statistics
```
States:      27 (1 initial)
Transitions: 216
Choices:     108
```
- **States**: Total reachable configurations
- **Transitions**: All possible state changes
- **Choices**: Total action-state pairs

### Property Results

**Probability Query**:
```
Pmax=? [ F goal ]
Result: 0.9234567890
```
This means: "Under the optimal policy, the goal is reached with 92.35% probability"

**Expected Reward Query**:
```
R{"steps"}min=? [ F goal ]
Result: 5.123456789
```
This means: "The optimal policy reaches the goal in 5.12 steps on average"

### Exported Policy Format

`policy.txt` contains:
```
0:(0,0,false)=right
1:(1,0,false)=right
2:(2,0,false)=up
...
```
Format: `state_id:(state_vars)=action`

## PCTL Property Syntax

### Probability Operators
- `P=? [ F φ ]` - Probability of eventually satisfying φ
- `P=? [ G φ ]` - Probability of always satisfying φ
- `P=? [ φ U ψ ]` - Probability that φ holds until ψ
- `P=? [ F<=k φ ]` - Probability of satisfying φ within k steps
- `P=? [ F[i,j] φ ]` - Probability of satisfying φ between i and j steps

### Reward Operators
- `R=? [ F φ ]` - Expected reward until φ
- `R=? [ C<=k ]` - Expected reward over k steps
- `R=? [ I=k ]` - Expected instantaneous reward at step k

### Strategy Selection
- `Pmax`, `Rmax` - Optimal strategy maximizing objective
- `Pmin`, `Rmin` - Optimal strategy minimizing objective

### Boolean Operators
- `&` - AND
- `|` - OR
- `!` - NOT
- `=>` - Implies

## Practical Examples

### Example 1: Safety Property
**Property**: "What is the maximum probability of reaching the goal while avoiding hazards?"
```prism
Pmax=? [ !hazard U goal ]
```

### Example 2: Time-Bounded Reachability
**Property**: "What is the probability of reaching the goal within 10 steps?"
```prism
Pmax=? [ F<=10 goal ]
```

### Example 3: Cost Minimization
**Property**: "What is the minimum expected cost to reach the goal?"
```prism
R{"cost"}min=? [ F goal ]
```

### Example 4: Threshold Verification
**Property**: "Can we reach the goal with at least 95% probability?"
```prism
Pmax>=0.95 [ F goal ]
```
Returns: `true` or `false`

## Policy Verification Workflow

1. **Model the System**
   - Define states, actions, transitions
   - Specify rewards/costs
   - Label important states

2. **Specify Properties**
   - Write PCTL formulas for desired behaviors
   - Include safety, liveness, and optimization goals

3. **Run PRISM**
   - Build the model
   - Verify properties
   - Export optimal policies

4. **Analyze Results**
   - Check if properties are satisfied
   - Extract optimal strategies
   - Understand probabilities and expected values

5. **Validate**
   - Simulate the policy
   - Compare with expected behavior
   - Refine model if needed

## Simulation Without PRISM

If PRISM is not installed, you can still simulate policies:

```bash
# Single episode
python3 simulate_policy.py

# Monte Carlo simulation
python3 simulate_policy.py --monte-carlo 10000
```

This demonstrates the policy behavior without formal verification.

## Common Issues and Solutions

### Issue: "PRISM not found"
**Solution**: Install PRISM and add to PATH

### Issue: "Error parsing model"
**Solution**: Check syntax, ensure all variables/constants are defined

### Issue: "State space too large"
**Solution**: 
- Reduce grid size
- Use state space reduction techniques
- Enable sparse matrices: `prism -sparse model.prism`

### Issue: "Verification taking too long"
**Solution**:
- Simplify model
- Use iterative methods: `prism -power model.prism`
- Set timeout: `prism -maxiters 10000 model.prism`

## Advanced Features

### Multi-Objective Queries
```bash
prism model.prism -pctl 'multi(Pmax=? [ F goal ], R{"cost"}min=? [ F goal ])'
```

### Parametric Model Checking
Use PARAM extension for parametric analysis

### Strategy Synthesis
```bash
prism model.prism \
  -pf 'Pmax=? [ F goal ]' \
  -exportstrat policy.txt \
  -exportstrattype actions
```

### Counterexample Generation
```bash
prism model.prism \
  -pctl 'P<0.5 [ F hazard ]' \
  -counterexample
```

## Further Reading

- **PRISM Manual**: https://www.prismmodelchecker.org/manual/
- **PCTL Specification**: https://www.prismmodelchecker.org/manual/PropertySpecification/ThePCTLPropertySpecificationLanguage
- **Case Studies**: https://www.prismmodelchecker.org/casestudies/
- **Tutorials**: https://www.prismmodelchecker.org/tutorial/

## Summary

This repository provides:
- ✅ Multiple MDP models (simple → complex)
- ✅ Property specifications in PCTL
- ✅ Verification scripts
- ✅ Policy simulation tools
- ✅ Comprehensive documentation
- ✅ Installation guide

**Next Steps**:
1. Install PRISM: `./install_prism.sh`
2. Run verification: `./verify_policy.sh`
3. Analyze results in output files
4. Modify models for your own problems

