from copy import deepcopy
import random

from units.unit_types import Fighter

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

def hit_fighters(fleet, hits):
    """
    Assigns hits to fighters in a fleet
    """
    if not fleet:
        return []
    
    for hit in range(hits):
        for ship in fleet:
            if ship.name == "fighter":
                ship.assign_hit()
                if ship.health <= 0:
                    fleet.remove(ship)
                    break
    return fleet

def simulate_space_combat(fleet_1, fleet_2, debug=False):
    """
    Simulates combat between two fleets
    Returns: winner (1 for player 1, -1 for player 2, 0 for draw),
             remaining ships for player 1, remaining ships for player 2
    """
    fleet_1 = deepcopy(fleet_1)
    fleet_2 = deepcopy(fleet_2)

    combat_round = 0
    while fleet_1 and fleet_2:
        combat_round += 1

        # anti-fighter barrage
        for ship in fleet_2:
            if ship.name == "destroyer" and [s.name for s in fleet_1].count("fighter") > 0:
                afb_hits = ship.anti_fighter_barrage()
                fleet_1 = hit_fighters(fleet_1, afb_hits)

        for ship in fleet_1:
            if ship.name == "destroyer" and [s.name for s in fleet_2].count("fighter") > 0:
                afb_hits = ship.anti_fighter_barrage()
                fleet_2 = hit_fighters(fleet_2, afb_hits)

        # Attack rolls
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
    
def run_n_simulations(fleet_1, fleet_2, n=100, debug=False):
    """
    Runs n simulations of combat between two fleets
    Returns: win rate for player 1, win rate for player 2, draw rate
    """
    fleet_1_wins = 0
    fleet_2_wins = 0
    draws = 0

    for _ in range(n):
        result, _, _ = simulate_space_combat(fleet_1, fleet_2, debug)
        if result == 1:
            fleet_1_wins += 1
        elif result == -1:
            fleet_2_wins += 1
        else:
            draws += 1

    total = fleet_1_wins + fleet_2_wins + draws
    return fleet_1_wins / total, fleet_2_wins / total, draws / total
