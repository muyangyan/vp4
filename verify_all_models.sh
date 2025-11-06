#!/bin/bash
# Verify all MDP models with PRISM

set -e

echo "================================================"
echo "PRISM MDP Policy Verification - All Models"
echo "================================================"
echo ""

# Check if PRISM is installed
if ! command -v prism &> /dev/null; then
    echo "ERROR: PRISM is not installed or not in PATH"
    echo ""
    echo "To install, run: ./install_prism.sh"
    echo ""
    exit 1
fi

# Function to verify a model
verify_model() {
    local model=$1
    local props=$2
    local name=$3
    
    echo "================================================"
    echo "Model: $name"
    echo "================================================"
    echo ""
    
    if [ ! -f "$model" ]; then
        echo "ERROR: Model file $model not found"
        return 1
    fi
    
    if [ ! -f "$props" ]; then
        echo "ERROR: Properties file $props not found"
        return 1
    fi
    
    echo "Building model..."
    prism "$model" -build
    
    echo ""
    echo "Verifying properties..."
    prism "$model" "$props"
    
    echo ""
    echo "Exporting optimal policy..."
    prism "$model" -pf 'Pmax=? [ F goal ]' \
        -exportstrat "${name}_policy.txt" \
        -exportstrattype actions 2>/dev/null || echo "(Policy export not applicable for this model)"
    
    echo ""
}

# Verify Simple MDP
if [ -f "simple_mdp.prism" ]; then
    verify_model "simple_mdp.prism" "simple_mdp.props" "simple"
fi

# Verify Stochastic MDP
if [ -f "stochastic_mdp.prism" ]; then
    verify_model "stochastic_mdp.prism" "stochastic_mdp.props" "stochastic"
fi

# Verify Grid World MDP
if [ -f "gridworld.prism" ]; then
    verify_model "gridworld.prism" "gridworld.props" "gridworld"
fi

echo "================================================"
echo "All Verifications Complete!"
echo "================================================"
echo ""
echo "Generated policy files:"
ls -1 *_policy.txt 2>/dev/null || echo "  (none)"
echo ""

