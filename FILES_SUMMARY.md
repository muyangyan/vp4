# Files Summary - PRISM MDP Verification

## Documentation Files

### 📘 README_PRISM.md
Main entry point with quick overview and links to detailed guides.

### 📗 QUICKSTART.md  
5-minute quick start guide for getting up and running immediately.

### 📕 PRISM_GUIDE.md
Comprehensive guide covering:
- PRISM installation
- MDP modeling
- PCTL property specification
- Policy verification workflow
- Troubleshooting
- Advanced features

### 📙 EXAMPLE_OUTPUT.md
Detailed example showing what PRISM verification output looks like, including:
- Model statistics
- Property verification results
- Optimal policy visualization
- Interpretation of results

### 📄 FILES_SUMMARY.md
This file - overview of all files in the project.

---

## MDP Model Files (.prism)

### simple_mdp.prism
**Difficulty**: Beginner  
**Size**: 3×3 grid  
**Type**: Deterministic  
**Purpose**: Learning PRISM basics

**Description**: Simple deterministic grid where robot moves from (0,0) to (2,2). Actions always succeed as intended. Good for understanding MDP structure and PRISM syntax.

**Key Features**:
- No stochasticity
- No hazards
- Minimal state space (9 states)
- Clear optimal policy

---

### stochastic_mdp.prism
**Difficulty**: Intermediate  
**Size**: 3×3 grid  
**Type**: Stochastic  
**Purpose**: Realistic planning under uncertainty

**Description**: Robot navigates 3×3 grid with stochastic movements (90% intended, 10% slip). Includes hazard at (1,1) that must be avoided.

**Key Features**:
- Stochastic transitions
- Single hazard obstacle
- Moderate state space
- Non-trivial optimal policy

---

### gridworld.prism
**Difficulty**: Advanced  
**Size**: 4×4 grid  
**Type**: Stochastic  
**Purpose**: Complex navigation with multiple hazards

**Description**: Larger grid with two hazards and higher uncertainty (80% intended, 20% slip). Demonstrates more realistic planning scenarios.

**Key Features**:
- High stochasticity
- Multiple hazards
- Larger state space (66 states)
- Complex policy routing

---

## Property Files (.props)

### simple_mdp.props
Properties for deterministic grid:
- Maximum probability of reaching goal (should be 1.0)
- Minimum steps to goal
- Time-bounded reachability
- Threshold verification

### stochastic_mdp.props
Properties for stochastic grid with hazard:
- Goal-reaching probability
- Safe goal-reaching (avoiding hazards)
- Hazard-hitting probability
- Expected steps and rewards
- Time-bounded properties

### gridworld.props
Comprehensive property set for complex grid:
- Multiple probability queries
- Multiple reward queries
- Safety properties
- Efficiency metrics
- Comparison of optimal vs worst-case policies

---

## Script Files

### install_prism.sh
**Purpose**: Automated PRISM installation  
**What it does**:
- Downloads PRISM 4.8.1 from GitHub
- Extracts to `~/prism/`
- Provides PATH configuration instructions
- Checks for Java dependency

**Usage**: `./install_prism.sh`

---

### verify_policy.sh
**Purpose**: Verify gridworld MDP  
**What it does**:
- Builds gridworld model
- Verifies all properties
- Exports optimal policy to file
- Exports adversary (induced DTMC)

**Usage**: `./verify_policy.sh`

---

### verify_all_models.sh
**Purpose**: Verify all three MDPs  
**What it does**:
- Checks PRISM installation
- Verifies simple_mdp
- Verifies stochastic_mdp
- Verifies gridworld
- Exports all optimal policies

**Usage**: `./verify_all_models.sh`

---

## Simulation Files

### simulate_policy.py
**Purpose**: Simulate policy without PRISM  
**Language**: Python 3  
**What it does**:
- Implements gridworld MDP
- Contains optimal policy (hard-coded)
- Simulates single episodes
- Runs Monte Carlo simulations
- Visualizes grid and paths
- Compares with PRISM results

**Usage**: 
```bash
# Single episode
python3 simulate_policy.py

# Monte Carlo (10,000 episodes)
python3 simulate_policy.py --monte-carlo 10000
```

**Output**:
- Grid visualization with policy arrows
- Episode-by-episode trace
- Success/hazard statistics
- Expected values estimation

---

## Example Output Files

### gridworld_policy_example.txt
Example of what an exported policy looks like from PRISM.

**Format**: `state_id:(state_vars)=action`

**Content**: Maps every state to its optimal action.

---

## Generated Files (after running verification)

These files are created when you run PRISM verification:

### *_policy.txt
Optimal policy for each model showing action to take in each state.

### *_adversary.tra  
Adversary file representing the induced DTMC when following the optimal policy.

---

## File Organization

```
vp4/
├── Documentation/
│   ├── README_PRISM.md          # Main entry point
│   ├── QUICKSTART.md            # 5-min quick start
│   ├── PRISM_GUIDE.md           # Comprehensive guide
│   ├── EXAMPLE_OUTPUT.md        # Example results
│   └── FILES_SUMMARY.md         # This file
│
├── Models/
│   ├── simple_mdp.prism         # Beginner model
│   ├── stochastic_mdp.prism     # Intermediate model
│   └── gridworld.prism          # Advanced model
│
├── Properties/
│   ├── simple_mdp.props         # Properties for simple
│   ├── stochastic_mdp.props     # Properties for stochastic
│   └── gridworld.props          # Properties for gridworld
│
├── Scripts/
│   ├── install_prism.sh         # Install PRISM
│   ├── verify_policy.sh         # Verify single model
│   └── verify_all_models.sh     # Verify all models
│
├── Simulation/
│   └── simulate_policy.py       # Python simulator
│
├── Examples/
│   └── gridworld_policy_example.txt  # Example policy
│
└── Planning_Domains/
    ├── deterministic/           # PDDL domains
    └── stochastic/             # Stochastic PDDL
```

---

## Workflow

### 1. Learning Path

**Step 1**: Read `QUICKSTART.md`  
**Step 2**: Try `simple_mdp.prism`  
**Step 3**: Read `PRISM_GUIDE.md`  
**Step 4**: Try `stochastic_mdp.prism`  
**Step 5**: Explore `gridworld.prism`  
**Step 6**: Create your own MDP

### 2. Verification Workflow

**Step 1**: Install PRISM (`./install_prism.sh`)  
**Step 2**: Choose a model  
**Step 3**: Define properties  
**Step 4**: Run verification  
**Step 5**: Analyze results  
**Step 6**: Export policy

### 3. Development Workflow

**Step 1**: Model your system in PRISM  
**Step 2**: Specify properties in PCTL  
**Step 3**: Verify with PRISM  
**Step 4**: Analyze policy  
**Step 5**: Refine model  
**Step 6**: Re-verify

---

## File Dependencies

```
verify_all_models.sh
    ├── requires: prism (installed)
    ├── reads: simple_mdp.prism
    ├── reads: simple_mdp.props
    ├── reads: stochastic_mdp.prism
    ├── reads: stochastic_mdp.props
    ├── reads: gridworld.prism
    ├── reads: gridworld.props
    └── generates: *_policy.txt, *_adversary.tra

simulate_policy.py
    ├── requires: python3
    ├── reads: (built-in policy)
    └── outputs: terminal visualization

install_prism.sh
    ├── requires: wget, tar
    ├── downloads: PRISM from GitHub
    └── creates: ~/prism/
```

---

## File Sizes (Approximate)

| File | Size | Lines |
|------|------|-------|
| simple_mdp.prism | 1 KB | 35 |
| stochastic_mdp.prism | 2 KB | 70 |
| gridworld.prism | 4 KB | 120 |
| simple_mdp.props | 0.5 KB | 10 |
| stochastic_mdp.props | 0.5 KB | 15 |
| gridworld.props | 1 KB | 25 |
| simulate_policy.py | 8 KB | 280 |
| PRISM_GUIDE.md | 15 KB | 450 |
| EXAMPLE_OUTPUT.md | 12 KB | 350 |

---

## Modification Guide

### To Create Your Own MDP:

1. **Copy a template**: Start with `simple_mdp.prism`
2. **Define states**: Add variables for your state space
3. **Define actions**: Add `[action]` commands with transitions
4. **Add rewards**: Define reward structures
5. **Label states**: Add labels for properties
6. **Create properties**: Write PCTL formulas in `.props` file
7. **Verify**: Run `prism yourmodel.prism yourprops.props`

### To Add Properties:

1. Open corresponding `.props` file
2. Add PCTL formula (see PRISM_GUIDE.md for syntax)
3. Run verification
4. Analyze results

### To Modify Simulation:

1. Edit `simulate_policy.py`
2. Change `GRID_SIZE`, `START`, `GOAL`, `HAZARDS`
3. Update `OPTIMAL_POLICY` dictionary
4. Run simulation

---

## Additional Resources

- **PRISM Homepage**: https://www.prismmodelchecker.org/
- **PRISM Manual**: https://www.prismmodelchecker.org/manual/
- **PRISM Tutorial**: https://www.prismmodelchecker.org/tutorial/
- **Case Studies**: https://www.prismmodelchecker.org/casestudies/
- **Forum**: https://www.prismmodelchecker.org/forum/

---

## Summary

This repository provides everything needed to:
- ✅ Learn PRISM model checking
- ✅ Verify MDP policies
- ✅ Understand PCTL properties
- ✅ Export optimal strategies
- ✅ Simulate policy behavior
- ✅ Build your own MDPs

**Total Files**: 17  
**Total Documentation**: 5 guides  
**Total Models**: 3 MDPs  
**Total Scripts**: 3 automation scripts  
**Total Tools**: 1 simulator

