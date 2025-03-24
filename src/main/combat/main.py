import json
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import copy
import matplotlib.patches as patches
from matplotlib.ticker import PercentFormatter

# Add the parent directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from combat.ship import Ship

with open("src/data/ships.json") as f:
    ships = json.load(f)

def assign_hits(fleet, hits):
    """
    Assigns hits to ships in a fleet
    """
    if not fleet:
        return []
    
    priority = sorted(sorted(fleet, key=lambda x: x.cost), key=lambda x: x.health, reverse=True)
    
    for i in range(hits):
        if not priority:
            break
        priority[0].assign_hit()
        if priority[0].health <= 0:
            priority.pop(0)
    
    return priority

def simulate_combat(fleet_1, fleet_2, debug=False):
    """
    Simulates combat between two fleets
    Returns: winner (1 for player 1, -1 for player 2, 0 for draw),
             remaining ships for player 1, remaining ships for player 2
    """
    fleet_1 = copy.deepcopy(fleet_1)
    fleet_2 = copy.deepcopy(fleet_2)
    
    combat_round = 0
    while fleet_1 and fleet_2:
        combat_round += 1

        attacker_hits = sum([ship.make_attack_roll() for ship in fleet_1])
        defender_hits = sum([ship.make_attack_roll() for ship in fleet_2])

        fleet_2 = assign_hits(fleet_2, attacker_hits)
        fleet_1 = assign_hits(fleet_1, defender_hits)

        if debug and combat_round <= 3:  # Limit debug output
            print(f"Round {combat_round}:")
            print(f"Player 1 rolled {attacker_hits} hits")
            print(f"Player 2 rolled {defender_hits} hits")
            print("Player 1's fleet:")
            for ship in fleet_1:
                print(f"\t{ship}")
            print("Player 2's fleet:")
            for ship in fleet_2:
                print(f"\t{ship}")

    # Return winner and remaining fleets
    if fleet_1 and not fleet_2:
        return 1, fleet_1, []
    elif fleet_2 and not fleet_1:
        return -1, [], fleet_2
    else:
        return 0, [], []

def create_fleet(ship_list, owner):
    """Create a fleet from a list of ship names"""
    fleet = []
    for ship_name in ship_list:
        s = Ship(owner=owner, **ships[ship_name])
        fleet.append(s)
    return fleet

def get_ship_abbreviation(ship_name):
    """Get a single letter abbreviation for a ship type"""
    abbrev_map = {
        "Dreadnought": "D",
        "Carrier": "C",  # V for vessel/carrier
        "Fighter": "F",
        "Cruiser": "V",
        "Destroyer": "d",
        "Battleship": "B"
    }
    return abbrev_map.get(ship_name, ship_name[0].upper())

def get_outcome_key(fleet):
    """
    Convert a fleet to a standardized key showing which ships remain
    Format: "D,D,F" for 2 Dreadnoughts and 1 Fighter
    """
    if not fleet:
        return "NONE"
    
    # Count ships by type
    ship_counts = defaultdict(int)
    for ship in fleet:
        ship_counts[ship.name] += 1
    
    # Create a sorted key
    parts = []
    for ship_name in sorted(ship_counts.keys()):
        abbrev = get_ship_abbreviation(ship_name)
        count = ship_counts[ship_name]
        for _ in range(count):
            parts.append(abbrev)
    
    return ",".join(parts)

def run_simulations(fleet_1_config, fleet_2_config, num_simulations=10000):
    """Run multiple simulations and collect detailed results"""
    # Store results
    results = {
        "winner": {1: 0, -1: 0, 0: 0},
        "player1_survivors": defaultdict(int),
        "player2_survivors": defaultdict(int),
        "all_outcomes": []  # Store each individual outcome
    }
    
    for _ in range(num_simulations):
        # Create fresh fleets for each simulation
        fleet_1 = create_fleet(fleet_1_config, "Player 1")
        fleet_2 = create_fleet(fleet_2_config, "Player 2")
        
        # Run simulation
        winner, remaining_1, remaining_2 = simulate_combat(fleet_1, fleet_2)
        
        # Record winner
        results["winner"][winner] += 1
        
        # Record remaining ships
        p1_outcome = get_outcome_key(remaining_1)
        p2_outcome = get_outcome_key(remaining_2)
        
        results["player1_survivors"][p1_outcome] += 1
        results["player2_survivors"][p2_outcome] += 1
        
        # Store full outcome
        results["all_outcomes"].append((winner, p1_outcome, p2_outcome))
    
    return results

def create_distribution_graph(results, num_simulations, fleet_1_config, fleet_2_config):
    """
    Creates a distribution graph showing the frequency of different remaining ship combinations
    """
    fig, ax = plt.figure(figsize=(14, 8)), plt.gca()
    
    # Get overall win percentages
    p1_win_pct = results["winner"][1] / num_simulations * 100
    p2_win_pct = results["winner"][-1] / num_simulations * 100
    draw_pct = results["winner"][0] / num_simulations * 100
    
    # Create labels for player 1 outcomes (when player 1 wins)
    p1_outcomes = [(k, v) for k, v in results["player1_survivors"].items() if k != "NONE"]
    p1_outcomes.sort(key=lambda x: x[1], reverse=True)
    
    # Create labels for player 2 outcomes (when player 2 wins)
    p2_outcomes = [(k, v) for k, v in results["player2_survivors"].items() if k != "NONE"]
    p2_outcomes.sort(key=lambda x: x[1], reverse=True)
    
    # Prepare data for plotting
    all_outcomes = []
    all_counts = []
    
    # First add player 1 winning scenarios
    for outcome, count in p1_outcomes:
        if count > 0:
            all_outcomes.append(outcome.replace(",", ""))
            all_counts.append(count / num_simulations * 100)
    
    # Add draws in the middle if any
    if draw_pct > 0:
        all_outcomes.append("=")
        all_counts.append(draw_pct)
    
    # Then add player 2 winning scenarios
    for outcome, count in p2_outcomes:
        if count > 0:
            all_outcomes.append(outcome.replace(",", ""))
            all_counts.append(count / num_simulations * 100)
    
    # Create the plot
    bars = ax.bar(range(len(all_outcomes)), all_counts, width=0.7)
    
    # Add percentage labels above each bar
    for i, (bar, val) in enumerate(zip(bars, all_counts)):
        if val >= 1.0:  # Only show labels for bars with at least 1%
            ax.text(
                bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.5,
                f"{val:.0f}%",
                ha='center', va='bottom',
                fontsize=9, color='black'
            )
    
    # Set x-ticks to show outcomes
    ax.set_xticks(range(len(all_outcomes)))
    ax.set_xticklabels(all_outcomes)
    
    # Add large percentage overlays for each player's win chance
    if p1_win_pct > 0:
        ax.text(
            len(all_outcomes)//4,
            ax.get_ylim()[1] * 0.6,
            f"{p1_win_pct:.0f}%",
            color='red',
            fontsize=80,
            ha='center',
            va='center',
            alpha=0.6
        )
    
    if p2_win_pct > 0:
        ax.text(
            3 * len(all_outcomes)//4,
            ax.get_ylim()[1] * 0.6,
            f"{p2_win_pct:.0f}%",
            color='blue',
            fontsize=80,
            ha='center',
            va='center',
            alpha=0.6
        )
    
    # Create a light blue area under the graph
    ax.fill_between(
        range(-1, len(all_outcomes) + 1),
        0,
        [max(all_counts) * 1.1] * (len(all_outcomes) + 2),
        color='blue',
        alpha=0.1,
        zorder=-1
    )
    
    # Add a subtle line connecting the tops of the bars
    x_vals = range(len(all_outcomes))
    y_vals = [bar.get_height() for bar in bars]
    ax.plot(x_vals, y_vals, color='blue', alpha=0.3, linestyle='-', linewidth=2)
    
    # Fill area under the line
    ax.fill_between(x_vals, 0, y_vals, color='blue', alpha=0.2)
    
    # Add fleet compositions as title
    fleet1_str = ", ".join([f"{fleet_1_config.count(ship)}x {ship}" for ship in set(fleet_1_config)])
    fleet2_str = ", ".join([f"{fleet_2_config.count(ship)}x {ship}" for ship in set(fleet_2_config)])
    ax.set_title(f"Combat Results: {fleet1_str} vs {fleet2_str}\n{num_simulations:,} Simulations", fontsize=12)
    
    # Customize grid and axes
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Make y-axis start at 0
    ax.set_ylim(bottom=0)
    
    # Add light vertical lines to separate players
    if draw_pct > 0:
        draw_idx = all_outcomes.index("=")
        ax.axvline(x=draw_idx - 0.5, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=draw_idx + 0.5, color='gray', linestyle='--', alpha=0.5)
    else:
        # Place divider at the middle
        mid_point = len(all_outcomes) // 2
        ax.axvline(x=mid_point - 0.5, color='gray', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    return fig

# Example usage
if __name__ == "__main__":
    # Define fleet configurations
    fleet_1_config = ["Dreadnought", "Dreadnought"]
    fleet_2_config = ["Carrier", "Fighter", "Fighter", "Fighter", "Fighter"]
    
    # Run simulations
    num_simulations = 10000
    print(f"Running {num_simulations} simulations...")
    results = run_simulations(fleet_1_config, fleet_2_config, num_simulations)
    
    # Print summary statistics
    print("\nSummary:")
    print(f"Player 1 Wins: {results['winner'][1] / num_simulations * 100:.1f}%")
    print(f"Player 2 Wins: {results['winner'][-1] / num_simulations * 100:.1f}%")
    print(f"Draws: {results['winner'][0] / num_simulations * 100:.1f}%")
    
    # Create distribution graph
    fig = create_distribution_graph(results, num_simulations, fleet_1_config, fleet_2_config)
    plt.savefig("combat_outcome_distribution.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    # Print detailed outcome frequencies for debugging
    print("\nPlayer 1 Winning Scenarios:")
    p1_outcomes = [(k, v) for k, v in results["player1_survivors"].items() if k != "NONE"]
    p1_outcomes.sort(key=lambda x: x[1], reverse=True)
    for outcome, count in p1_outcomes:
        if count > 0:
            print(f"{outcome}: {count / num_simulations * 100:.1f}%")
    
    print("\nPlayer 2 Winning Scenarios:")
    p2_outcomes = [(k, v) for k, v in results["player2_survivors"].items() if k != "NONE"]
    p2_outcomes.sort(key=lambda x: x[1], reverse=True)
    for outcome, count in p2_outcomes:
        if count > 0:
            print(f"{outcome}: {count / num_simulations * 100:.1f}%")