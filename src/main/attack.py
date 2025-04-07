from pyomo.environ import *
from utils import powerset, calculate_fleet_value
from combat_sim import run_n_simulations

def compute_system_benefit(system, disposition):
    resource_importance = disposition["resources"]
    influence_importance = disposition["influence"]

    planets = system.planets
    planet_resource_benefit = sum(planet.resources for planet in planets) * resource_importance 
    planet_influence_benefit = sum(planet.influence for planet in planets) * influence_importance 

    return planet_resource_benefit + planet_influence_benefit

def compute_enemy_system_value(system, player):
    enemy_strength = 0
    for ship in system.space_area:
        if ship.owner != player:
            enemy_strength += player.disposition[ship.name]
    for planet in system.planets:
        if planet.owner != player:
            if planet.has_space_dock:
                enemy_strength += player.disposition["space dock"]
            enemy_strength += player.disposition["pds"] * planet.num_pds
    return enemy_strength

def filter_and_simulate_battles_for_systems(player):
    reachable_tiles = dict()
    for ship in player.ships:
        if player.name not in ship.system.command_counters:
            for tile in ship.get_reachable_tiles():
                if player.name not in tile.command_counters:
                    if tile not in reachable_tiles:
                        reachable_tiles[tile] = []
                    reachable_tiles[tile].append(ship)

    # Filter systems to attack: empty or hostile
    reachable_tiles = {
        system: ships for system, ships in reachable_tiles.items()
        if (system.space_area == [] and sum(planet.owner == player for planet in system.planets) == 0)
        or (system.space_area != [] and system.space_area[0].owner != player)
    }

    # Get powerset of ships per tile
    powerset_reachable_tiles = {
        tile: powerset(ships) for tile, ships in reachable_tiles.items()
    }

    computed_win_probabilities = dict()
    for tile, ship_combos in powerset_reachable_tiles.items():
        computed_win_probabilities[tile] = {}
        for ship_combo in ship_combos:
            if not ship_combo:
                continue
            if tile.space_area == []:
                computed_win_probabilities[tile][ship_combo] = 1.0
            else:
                computed_win_probabilities[tile][ship_combo] = run_n_simulations(ship_combo, tile.space_area, n=100)[0]

    return computed_win_probabilities

def attack(player):
    aggressiveness = player.disposition["aggression"]
    system_options = filter_and_simulate_battles_for_systems(player)

    # Flatten options: (system, ship_combo)
    attack_options = []
    benefit_lookup = {}
    win_prob_lookup = {}
    pain_lookup = {}

    for system, ship_combos in system_options.items():
        for ships in ship_combos:
            # Infantry-capable check
            has_infantry = any(ship.capacity > 0 for ship in ships)
            benefit_val = compute_system_benefit(system, player.disposition)
            if not has_infantry and len(system.planets) > 0:
                benefit_val = 0  # Can't take planets

            # Use frozenset to represent the ship combo
            ship_combo_key = frozenset(ships)

            attack_options.append((system, ship_combo_key))
            benefit_lookup[(system, ship_combo_key)] = benefit_val
            win_prob_lookup[(system, ship_combo_key)] = system_options[system][ships]
            pain_lookup[(system, ship_combo_key)] = compute_enemy_system_value(system, player)

    if attack_options == []:
        return "failed"

    # Create model
    model = ConcreteModel()
    model.x = Var(attack_options, domain=Binary)

    # Objective function
    def objective_rule(m):
        return sum(
            m.x[(system, combo)] * (
                benefit_lookup[(system, combo)] * win_prob_lookup[(system, combo)] +
                aggressiveness * pain_lookup[(system, combo)] * win_prob_lookup[(system, combo)] - 
                (1 - win_prob_lookup[(system, combo)]) * (1-aggressiveness) * calculate_fleet_value(combo, player.disposition)
            )
            for (system, combo) in attack_options
        )
    model.obj = Objective(rule=objective_rule, sense=maximize)


    # Only one attack choice
    model.attack_once = Constraint(expr=sum(model.x[opt] for opt in attack_options) == 1)

    # Fleet capacity constraint
    def total_ships_used(m):
        total = 0
        for (system, combo) in attack_options:
            # Convert frozenset back to a list of ships
            combo_ships = list(combo)
            num_non_fighters = sum(1 for s in combo_ships if s.name != "fighter")
            total += m.x[(system, combo)] * num_non_fighters
        return total <= player.command_counters["fleet"]
        
    model.fleet_cap_constraint = Constraint(rule=total_ships_used)

   # Solve
    solver = SolverFactory('glpk')
    solver.solve(model)

    # Find the best attack option
    best = max(attack_options, key=lambda opt: value(model.x[opt]))
    system, combo = best

    # Allocate infantry to ships in the selected combo
    source_systems = set()
    for ship in combo:
        if ship.capacity > 0:
            source_systems.add(ship.system)
    print(f"Source systems: {", ".join([str(s._id) for s in source_systems])}")

    infantry_available = []
    for s in source_systems:
        infantry_available.extend([unit for unit in s.space_area if unit.name == "infantry" and unit.owner == player])
    
        for p in s.planets:
            #print(p.name)
            if p.owner == player:
                #print(f"-> {p.name} has {p.num_ground_forces} ground forces")
                infantry_available.extend(p.ground_forces)
    #print(f"Available infantry: {len(infantry_available)}")
    infantry_allocated = []
    for ship in combo:
        if ship.capacity > 0:
            #print(f"{ship.name} can carry {ship.capacity} units")
            # Allocate as many infantry as the ship can carry, without exceeding available infantry
            infantry_to_load = min(ship.capacity - len(ship.in_cargo), len(infantry_available))

            for infantry in infantry_available[:infantry_to_load]:
                if infantry.planet != None:
                    infantry.remove_from_planet()
            ship.in_cargo.extend(infantry_available[:infantry_to_load])
            infantry_allocated.extend(infantry_available[:infantry_to_load])
            infantry_available = infantry_available[infantry_to_load:]  # Remove allocated infantry
    for ships in combo:
        print(f"{ships.name} is carrying {len(ships.in_cargo)} infantry units")


    print("\nChosen attack:")
    # find the best attack option
    best = max(attack_options, key=lambda opt: value(model.x[opt]))
    system, combo = best
    '''for (system, combo) in attack_options:
        if value(model.x[(system, combo)]) > 0.5:'''
    print(f"-> System: {system.coords}")
    print(f"-> Ships: {[s.name for s in combo]}")  # Convert frozenset back to list

    return system, combo  # Return the chosen system and ship combo for further processing
