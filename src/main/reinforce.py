from pyomo.environ import *
from utils import powerset, calculate_fleet_value

def compute_vulnerability(system, player):
    # Heuristic: vulnerability = enemy proximity + lack of defense
    risk = estimate_invasion_risk(system, player)  # You can implement this based on nearby enemies
    ground_defense = sum(planet.num_ground_forces for planet in system.planets if planet.owner == player)
    ground_defense += sum(planet.num_pds for planet in system.planets if planet.owner == player)
    space_defense = sum(1 for ship in system.space_area if ship.owner == player)
    return risk - (0.5 * space_defense + ground_defense)  # Weighted

def filter_reinforce_targets(player):
    vulnerable_systems = {}
    controlled_systems = set([planet.system for planet in player.planets])
    print(f"Controlled systems: {controlled_systems}")
    for system in controlled_systems:
        vuln_score = compute_vulnerability(system, player)
        print(f"System {system.coords} vulnerability score: {vuln_score}")
        
        vulnerable_systems[system] = vuln_score
    return vulnerable_systems

def reachable_ships_for_reinforcement(player):
    reachable = dict()
    controlled_systems = set([planet.system for planet in player.planets])
    print(f"Controlled systems: {controlled_systems}")
    for ship in player.ships:
        if player.name not in ship.system.command_counters: 
            for tile in ship.get_reachable_tiles():
                if tile in controlled_systems and player.name not in tile.command_counters:
                    if tile not in reachable:
                        reachable[tile] = []
                    reachable[tile].append(ship)
    return reachable

def estimate_invasion_risk(system, player, max_range=2):
    """
    Heuristic to estimate how likely a system is to be invaded soon.
    - Considers nearby enemy ships within `max_range`.
    - Weighs enemy strength vs current defenses.
    """
    enemy_threat = 0
    defense_value = 0

    # Step 1: Sum enemy ship threat within range
    for other_system in system.get_neighbors(n=max_range):
        for ship in other_system.space_area:
            if ship.owner != player:
                # Use player's disposition to weigh importance of ship type
                enemy_threat += player.disposition.get(ship.name, 1)

    # Step 2: Sum local defenses
    for ship in system.space_area:
        if ship.owner == player:
            defense_value += player.disposition.get(ship.name, 1)

    for planet in system.planets:
        if planet.owner == player:
            defense_value += planet.num_ground_forces
            defense_value += player.disposition.get("pds", 1) * planet.num_pds
            if planet.has_space_dock:
                defense_value += player.disposition.get("space dock", 1)

    # Step 3: Compute risk
    raw_risk = enemy_threat - 0.6 * defense_value  # tune this weight as needed
    return max(raw_risk, 0)  # Risk can't be negative


def reinforce(player):
    reinforce_targets = filter_reinforce_targets(player)
    reachable = reachable_ships_for_reinforcement(player)

    if len(reachable) == 0 or len(reinforce_targets) == 0:
        return "INFEASIBLE"

    # Build list of options
    reinforce_options = []
    benefit_lookup = {}
    cost_lookup = {}

    for system in reinforce_targets:
        vuln_score = reinforce_targets[system]
        if system not in reachable:
            continue
        ship_combos = powerset(reachable[system])
        for combo in ship_combos:
            if not combo:
                continue
            capacity = sum(s.capacity for s in combo)
            ground_units = sum(s.num_ground_units for s in combo if hasattr(s, "num_ground_units"))
            if capacity < ground_units:
                continue  # Can't transport enough

            key = (system, frozenset(combo))
            reinforce_options.append(key)
            benefit_lookup[key] = vuln_score
            cost_lookup[key] = calculate_fleet_value(combo, player.disposition)

    # Optimization model
    model = ConcreteModel()
    model.x = Var(reinforce_options, domain=Binary)

    def obj_rule(m):
        return sum(
            m.x[opt] * (benefit_lookup[opt] - 0.5 * cost_lookup[opt])  # Adjust 0.5 as desired
            for opt in reinforce_options
        )
    model.obj = Objective(rule=obj_rule, sense=maximize)

    # Only one reinforcement choice
    if reinforce_options:
        model.reinforce_once = Constraint(expr=sum(model.x[opt] for opt in reinforce_options) <= 1)
    else:
        model.reinforce_once = Constraint(expr=Constraint.Feasible)  # No options, so the constraint is trivially feasible

    def fleet_limit(m):
        return sum(
            m.x[opt] * sum(1 for s in list(opt[1]) if s.name != "fighter")
            for opt in reinforce_options
        ) <= player.command_counters["fleet"]

    model.fleet_constraint = Constraint(rule=fleet_limit)

    SolverFactory('glpk').solve(model)

    if len(reinforce_options) == 0:
        return None, None

    best = max(reinforce_options, key=lambda opt: value(model.x[opt]))
    system, combo = best
    print("\nChosen reinforcement:")
    print(f"-> System: {system.coords}")
    print(f"-> Ships: {list(combo)}")

    return system, combo
