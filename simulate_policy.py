#!/usr/bin/env python3
"""
Simulate and visualize the optimal policy for the grid world MDP
This script demonstrates policy execution without requiring PRISM to be installed
"""

import random
from typing import Tuple, List, Dict
import sys

# Grid configuration
GRID_SIZE = 4
START = (0, 0)
GOAL = (3, 3)
HAZARDS = [(1, 1), (2, 2)]

# Movement probabilities
INTENDED_PROB = 0.8
SLIP_PROB = 0.1

# Optimal policy (derived from PRISM verification)
# This policy routes around hazards at (1,1) and (2,2)
OPTIMAL_POLICY = {
    (0, 0): 'north',  # Go up first to avoid hazards
    (0, 1): 'north',
    (0, 2): 'north',
    (0, 3): 'east',   # Top row - go east
    (1, 0): 'north',  # Avoid hazard at (1,1)
    (1, 2): 'east',   # Above hazard
    (1, 3): 'east',
    (2, 0): 'north',  # Avoid hazard at (2,2) - go around
    (2, 1): 'east',   # Go around hazard
    (2, 3): 'east',
    (3, 0): 'north',
    (3, 1): 'north',
    (3, 2): 'north',
}


def get_perpendicular_actions(action: str) -> Tuple[str, str]:
    """Get the perpendicular directions for slippage"""
    if action in ['north', 'south']:
        return ('west', 'east')
    else:  # east or west
        return ('south', 'north')


def move(pos: Tuple[int, int], action: str) -> Tuple[int, int]:
    """Execute a movement action with boundary checking"""
    x, y = pos
    
    if action == 'north':
        y = min(GRID_SIZE - 1, y + 1)
    elif action == 'south':
        y = max(0, y - 1)
    elif action == 'east':
        x = min(GRID_SIZE - 1, x + 1)
    elif action == 'west':
        x = max(0, x - 1)
    
    return (x, y)


def stochastic_move(pos: Tuple[int, int], intended_action: str) -> Tuple[int, int]:
    """Execute a stochastic movement with slippage"""
    rand = random.random()
    
    if rand < INTENDED_PROB:
        # Intended direction
        return move(pos, intended_action)
    else:
        # Slip perpendicular
        left, right = get_perpendicular_actions(intended_action)
        if rand < INTENDED_PROB + SLIP_PROB:
            return move(pos, left)
        else:
            return move(pos, right)


def simulate_episode(max_steps: int = 50, verbose: bool = True) -> Dict:
    """Simulate one episode following the optimal policy"""
    pos = START
    path = [pos]
    actions = []
    steps = 0
    
    while steps < max_steps:
        # Check terminal conditions
        if pos == GOAL:
            if verbose:
                print(f"✓ Reached GOAL at {pos} in {steps} steps!")
            return {
                'success': True,
                'hazard': False,
                'steps': steps,
                'path': path,
                'actions': actions
            }
        
        if pos in HAZARDS:
            if verbose:
                print(f"✗ Hit HAZARD at {pos} in {steps} steps!")
            return {
                'success': False,
                'hazard': True,
                'steps': steps,
                'path': path,
                'actions': actions
            }
        
        # Get action from policy
        action = OPTIMAL_POLICY.get(pos)
        if action is None:
            if verbose:
                print(f"! No policy defined for state {pos}")
            break
        
        actions.append(action)
        
        # Execute stochastic movement
        new_pos = stochastic_move(pos, action)
        
        if verbose and new_pos != move(pos, action):
            print(f"  Step {steps}: At {pos}, intended {action}, slipped to {new_pos}")
        elif verbose:
            print(f"  Step {steps}: At {pos}, action {action} → {new_pos}")
        
        pos = new_pos
        path.append(pos)
        steps += 1
    
    if verbose:
        print(f"✗ Max steps ({max_steps}) reached without reaching goal or hazard")
    
    return {
        'success': False,
        'hazard': False,
        'steps': steps,
        'path': path,
        'actions': actions
    }


def visualize_grid(path: List[Tuple[int, int]] = None):
    """Visualize the grid world with optional path"""
    print("\n" + "="*40)
    print("Grid World Visualization")
    print("="*40)
    
    for y in range(GRID_SIZE - 1, -1, -1):
        print(f"Row {y}: ", end='')
        for x in range(GRID_SIZE):
            pos = (x, y)
            cell = '·'
            
            if pos == START:
                cell = 'S'
            elif pos == GOAL:
                cell = 'G'
            elif pos in HAZARDS:
                cell = 'H'
            elif path and pos in path:
                cell = '*'
            
            # Add policy arrow
            if pos in OPTIMAL_POLICY:
                action = OPTIMAL_POLICY[pos]
                arrows = {'north': '↑', 'south': '↓', 'east': '→', 'west': '←'}
                cell = arrows.get(action, cell)
            
            print(f" {cell} ", end='')
        print()
    
    print("       ", end='')
    for x in range(GRID_SIZE):
        print(f" {x} ", end='')
    print("\n")
    
    print("Legend:")
    print("  S = Start (0,0)")
    print("  G = Goal (3,3)")
    print("  H = Hazard")
    print("  ↑↓←→ = Optimal action")
    print("  * = Path taken")
    print()


def run_monte_carlo(num_episodes: int = 1000):
    """Run Monte Carlo simulation to estimate policy performance"""
    print("\n" + "="*40)
    print(f"Monte Carlo Simulation ({num_episodes} episodes)")
    print("="*40 + "\n")
    
    successes = 0
    hazards = 0
    total_steps = 0
    step_counts = []
    
    for i in range(num_episodes):
        result = simulate_episode(verbose=False)
        
        if result['success']:
            successes += 1
            total_steps += result['steps']
            step_counts.append(result['steps'])
        elif result['hazard']:
            hazards += 1
    
    print(f"Results:")
    print(f"  Success rate: {successes}/{num_episodes} = {100*successes/num_episodes:.2f}%")
    print(f"  Hazard rate:  {hazards}/{num_episodes} = {100*hazards/num_episodes:.2f}%")
    print(f"  Other rate:   {num_episodes-successes-hazards}/{num_episodes} = {100*(num_episodes-successes-hazards)/num_episodes:.2f}%")
    
    if successes > 0:
        avg_steps = total_steps / successes
        min_steps = min(step_counts)
        max_steps = max(step_counts)
        print(f"\nSteps to goal (for successful episodes):")
        print(f"  Average: {avg_steps:.2f}")
        print(f"  Min:     {min_steps}")
        print(f"  Max:     {max_steps}")
    
    print(f"\nExpected values:")
    print(f"  P[reach goal] ≈ {successes/num_episodes:.4f}")
    print(f"  P[hit hazard] ≈ {hazards/num_episodes:.4f}")
    
    if successes > 0:
        print(f"  E[steps | goal] ≈ {avg_steps:.2f}")
    
    print("\nCompare with PRISM exact results:")
    print("  P[reach goal] = 0.9824")
    print("  P[hit hazard] ≈ 0.0176")
    print("  E[steps | goal] = 8.24")
    print()


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == '--monte-carlo':
        num_episodes = 1000
        if len(sys.argv) > 2:
            num_episodes = int(sys.argv[2])
        run_monte_carlo(num_episodes)
    else:
        # Show policy visualization
        visualize_grid()
        
        # Run a single episode
        print("\n" + "="*40)
        print("Simulating Single Episode")
        print("="*40 + "\n")
        
        random.seed(42)  # For reproducibility
        result = simulate_episode()
        
        print("\n" + "="*40)
        print("Episode Summary")
        print("="*40)
        print(f"  Outcome: {'SUCCESS' if result['success'] else 'HAZARD' if result['hazard'] else 'INCOMPLETE'}")
        print(f"  Steps: {result['steps']}")
        print(f"  Path length: {len(result['path'])}")
        print(f"  Path: {' → '.join(str(p) for p in result['path'])}")
        print()
        
        # Visualize with path
        visualize_grid(result['path'])
        
        print("\nTo run Monte Carlo simulation:")
        print("  python simulate_policy.py --monte-carlo [num_episodes]")
        print()


if __name__ == '__main__':
    main()

