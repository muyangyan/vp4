#!/bin/bash
# Script to verify MDP policy using PRISM model checker

echo "================================================"
echo "PRISM MDP Policy Verification"
echo "================================================"
echo ""

# Check if PRISM is installed
if ! command -v prism &> /dev/null; then
    echo "ERROR: PRISM is not installed or not in PATH"
    echo ""
    echo "To install PRISM:"
    echo "1. Download from: https://www.prismmodelchecker.org/download.php"
    echo "2. Extract and add to PATH, or run with full path"
    echo ""
    exit 1
fi

MODEL_FILE="gridworld.prism"
PROPS_FILE="gridworld.props"

if [ ! -f "$MODEL_FILE" ]; then
    echo "ERROR: Model file $MODEL_FILE not found"
    exit 1
fi

if [ ! -f "$PROPS_FILE" ]; then
    echo "ERROR: Properties file $PROPS_FILE not found"
    exit 1
fi

echo "Model: $MODEL_FILE"
echo "Properties: $PROPS_FILE"
echo ""

# Build the model
echo "Building MDP model..."
prism "$MODEL_FILE" -build

echo ""
echo "================================================"
echo "Verifying Properties"
echo "================================================"
echo ""

# Verify all properties
prism "$MODEL_FILE" "$PROPS_FILE" -prop 1,2,3,4,5,6,7,8,9,10

echo ""
echo "================================================"
echo "Exporting Optimal Strategy/Policy"
echo "================================================"
echo ""

# Export the optimal strategy (policy) for reaching the goal
# This generates a policy that maximizes probability of reaching goal
prism "$MODEL_FILE" -pf 'Pmax=? [ F goal ]' -exportstrat gridworld_policy.txt -exportstrattype actions

echo "Optimal policy exported to: gridworld_policy.txt"
echo ""

# Generate adversary (optimal strategy representation)
prism "$MODEL_FILE" -pf 'Pmax=? [ F goal ]' -exportadv gridworld_adversary.tra

echo "Adversary file exported to: gridworld_adversary.tra"
echo ""

echo "================================================"
echo "Policy Verification Complete"
echo "================================================"

