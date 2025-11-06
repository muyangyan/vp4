# PRISM MDP Verification - Quick Start Guide

## 5-Minute Quick Start

### Option 1: With PRISM Installed

```bash
# 1. Verify PRISM is installed
prism -version

# 2. Run verification on all models
./verify_all_models.sh

# 3. View results
cat simple_policy.txt
cat stochastic_policy.txt
```

### Option 2: Without PRISM (Simulation Only)

```bash
# 1. Run single episode simulation
python3 simulate_policy.py

# 2. Run Monte Carlo simulation (10,000 episodes)
python3 simulate_policy.py --monte-carlo 10000
```

### Option 3: Install PRISM First

```bash
# 1. Run installation script
./install_prism.sh

# 2. Add to PATH
export PATH=$PATH:$HOME/prism/prism-4.8.1-linux64-x86/bin

# 3. Verify installation
prism -version

# 4. Run verification
./verify_all_models.sh
```

## What You'll Get

### MDP Models
- **simple_mdp.prism**: 3×3 deterministic grid (learning)
- **stochastic_mdp.prism**: 3×3 stochastic with hazard (realistic)
- **gridworld.prism**: 4×4 stochastic with multiple hazards (complex)

### Property Files
- **\*.props**: PCTL formulas to verify on each model

### Output Files
- **\*_policy.txt**: Optimal policies (action per state)
- **\*_adversary.tra**: Induced DTMC under optimal policy
- Verification results in terminal

## Example: Simple MDP

### Model
```prism
module robot
    x : [0..2] init 0;
    y : [0..2] init 0;
    
    [right] x<2 -> (x'=x+1);
    [up] y<2 -> (y'=y+1);
    // ... more actions
endmodule
```

### Property
```prism
// What's the minimum steps to reach goal (2,2)?
R{"steps"}min=? [ F goal ]
```

### Result
```
Result: 4
```

### Policy
```
State (0,0): right
State (1,0): right  
State (2,0): up
State (2,1): up
State (2,2): done (goal!)
```

## Understanding Results

### Probability Results
```
Pmax=? [ F goal ]
Result: 0.9523
```
**Means**: 95.23% chance of reaching goal under optimal policy

### Reward Results
```
R{"steps"}min=? [ F goal ]
Result: 5.234
```
**Means**: Expected 5.234 steps to reach goal under optimal policy

### Boolean Results
```
Pmax>=0.9 [ F goal ]
Result: true
```
**Means**: Yes, we can reach goal with ≥90% probability

## Common Commands

### Build Model
```bash
prism model.prism -build
```

### Verify Property
```bash
prism model.prism -pctl 'Pmax=? [ F goal ]'
```

### Export Policy
```bash
prism model.prism -pf 'Pmax=? [ F goal ]' -exportstrat policy.txt
```

### Verify All Properties
```bash
prism model.prism properties.props
```

## File Structure

```
vp4/
├── simple_mdp.prism              # Simple deterministic model
├── simple_mdp.props              # Properties for simple model
├── stochastic_mdp.prism          # Stochastic model with hazard
├── stochastic_mdp.props          # Properties for stochastic model
├── gridworld.prism               # Complex 4x4 grid model
├── gridworld.props               # Properties for gridworld
├── install_prism.sh              # Install PRISM
├── verify_all_models.sh          # Verify all models
├── simulate_policy.py            # Simulate policy without PRISM
├── QUICKSTART.md                 # This file
├── PRISM_GUIDE.md                # Comprehensive guide
└── EXAMPLE_OUTPUT.md             # Example verification output
```

## Next Steps

1. **Learn More**: Read `PRISM_GUIDE.md`
2. **See Examples**: Check `EXAMPLE_OUTPUT.md`
3. **Modify Models**: Edit `.prism` files for your problem
4. **Add Properties**: Edit `.props` files with new PCTL formulas
5. **Analyze Results**: Study the optimal policies generated

## Troubleshooting

### "PRISM not found"
- Install with `./install_prism.sh`
- Add to PATH: `export PATH=$PATH:/path/to/prism/bin`

### "Java not found"
- Install Java: `sudo apt-get install default-jre`

### "Model building fails"
- Check syntax in `.prism` file
- Ensure all variables are initialized
- Verify transitions are well-formed

### "Python simulation differs from PRISM"
- This is expected - simulation uses sampling
- Run more episodes: `--monte-carlo 100000`
- PRISM gives exact mathematical results

## Key Concepts

### MDP Components
- **States**: System configurations
- **Actions**: Available choices
- **Transitions**: Probabilistic outcomes
- **Rewards**: Costs or benefits

### Policy
- Maps each state to an action
- **Deterministic**: Single action per state
- **Optimal**: Maximizes/minimizes objective

### Verification
- **Model Checking**: Prove properties hold
- **PCTL**: Probabilistic temporal logic
- **Synthesis**: Generate optimal policies

## Resources

- **PRISM Website**: https://www.prismmodelchecker.org/
- **Manual**: https://www.prismmodelchecker.org/manual/
- **Tutorials**: https://www.prismmodelchecker.org/tutorial/
- **Case Studies**: https://www.prismmodelchecker.org/casestudies/

## Questions?

See `PRISM_GUIDE.md` for detailed documentation on:
- PCTL syntax and semantics
- Advanced model checking features
- Optimization techniques
- Troubleshooting guide

