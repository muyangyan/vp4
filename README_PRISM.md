# PRISM MDP Policy Verification Example

This repository contains complete examples of using the **PRISM model checker** to verify policies in Markov Decision Processes (MDPs).

## 🚀 Quick Start

**New to PRISM?** See [`QUICKSTART.md`](QUICKSTART.md) for a 5-minute guide.

**Want details?** See [`PRISM_GUIDE.md`](PRISM_GUIDE.md) for comprehensive documentation.

## What's Inside

✅ **3 MDP Models**: From simple to complex  
✅ **Property Specifications**: PCTL temporal logic formulas  
✅ **Verification Scripts**: Automated policy verification  
✅ **Simulation Tools**: Test policies without PRISM  
✅ **Complete Documentation**: Guides and examples  

## Quick Commands

```bash
# Install PRISM
./install_prism.sh

# Verify all models
./verify_all_models.sh

# Simulate policy
python3 simulate_policy.py --monte-carlo 10000
```

## Files

- **gridworld.prism**: MDP model specification for a 4x4 grid world navigation problem
- **gridworld.props**: Property specifications to verify on the MDP
- **verify_policy.sh**: Bash script to run PRISM verification and export optimal policies

## MDP Description

The grid world MDP models an agent navigating a 4x4 grid:
- **Start**: Position (0,0) - bottom-left corner
- **Goal**: Position (3,3) - top-right corner
- **Hazards**: Positions (1,1) and (2,2) - squares to avoid
- **Actions**: north, south, east, west
- **Stochastic Movement**: 
  - 80% probability of moving in intended direction
  - 10% probability of slipping perpendicular left
  - 10% probability of slipping perpendicular right

## Properties Verified

1. Maximum probability of reaching the goal
2. Minimum probability of reaching the goal
3. Maximum probability of reaching goal while staying safe
4. Minimum probability of hitting a hazard
5. Expected number of steps to reach goal (optimal policy)
6. Maximum expected total reward
7. Probability of reaching goal within 20 steps
8. Verification that goal is reachable with P ≥ 0.9
9. Expected hazard penalties
10. Maximum probability of reaching terminal state

## Installation

### Installing PRISM

1. **Download PRISM**:
   ```bash
   wget https://github.com/prismmodelchecker/prism/releases/download/v4.8.1/prism-4.8.1-linux64-x86.tar.gz
   ```

2. **Extract**:
   ```bash
   tar -xzf prism-4.8.1-linux64-x86.tar.gz
   ```

3. **Add to PATH** (add to ~/.bashrc for persistence):
   ```bash
   export PATH=$PATH:/path/to/prism-4.8.1-linux64-x86/bin
   ```

4. **Test installation**:
   ```bash
   prism -version
   ```

## Usage

### Run the verification script:
```bash
chmod +x verify_policy.sh
./verify_policy.sh
```

### Or run PRISM commands directly:

**Build the model**:
```bash
prism gridworld.prism -build
```

**Verify all properties**:
```bash
prism gridworld.prism gridworld.props
```

**Export optimal policy**:
```bash
prism gridworld.prism -pf 'Pmax=? [ F goal ]' -exportstrat gridworld_policy.txt -exportstrattype actions
```

**Verify specific property**:
```bash
prism gridworld.prism -pctl 'Pmax=? [ F goal ]'
```

## Output

The script produces:
1. **Verification results**: Numerical values for each property
2. **gridworld_policy.txt**: Optimal policy as action choices for each state
3. **gridworld_adversary.tra**: Adversary representation (induced DTMC under optimal policy)

## Understanding the Results

- **Policy**: The optimal policy tells you which action to take in each state to maximize the probability of reaching the goal
- **Probabilities**: Show the likelihood of satisfying temporal logic properties
- **Expected values**: Show the average cost/reward under optimal strategies

## Customization

Modify the MDP by editing `gridworld.prism`:
- Change `GRID_SIZE` for larger grids
- Adjust hazard locations
- Modify movement probabilities
- Add more rewards/penalties

Add new properties to `gridworld.props` using PCTL syntax.

## PCTL Syntax Reference

- `P=? [ F φ ]` - Probability of eventually satisfying φ
- `P=? [ φ U ψ ]` - Probability that φ holds until ψ
- `P=? [ F<=k φ ]` - Probability of satisfying φ within k steps
- `R=? [ F φ ]` - Expected reward until φ
- `Pmax`, `Pmin`, `Rmax`, `Rmin` - Optimal strategies for max/min

## References

- PRISM Manual: https://www.prismmodelchecker.org/manual/
- PRISM Case Studies: https://www.prismmodelchecker.org/casestudies/
- PCTL Logic: https://www.prismmodelchecker.org/manual/PropertySpecification/ThePCTLPropertySpecificationLanguage

