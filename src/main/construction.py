from pyomo.environ import *

from reinforce import compute_vulnerability

def construction(player):
    # === Input Data ===
    planets = player.planets
    planet_values = {planet: player.calculate_planet_value(planet) for planet in planets}
    planet_threats = {planet: compute_vulnerability(planet.system, player) for planet in planets}

    # Tuning weights
    dock_resource_weight = player.disposition["space dock"]
    dock_threat_penalty = 0.8
    pds_value_weight = player.disposition["pds"]
    pds_threat_weight = 1.2

    MAX_DOCKS_PER_PLANET = 1
    MAX_PDS_PER_PLANET = 2

    # === Pyomo Model ===
    model = ConcreteModel()
    planet_list = list(planets)

    # Binary decision variables
    model.build_dock = Var(planet_list, domain=Binary)
    model.build_pds = Var(planet_list, domain=Binary)

    model.structure_limits = ConstraintList()
    for p in planet_list:
        if p.has_space_dock:
            # Already has a dock, can't add more
            model.structure_limits.add(model.build_dock[p] == 0)
        if p.num_pds >= MAX_PDS_PER_PLANET:
            # Already maxed PDS
            model.structure_limits.add(model.build_pds[p] == 0)

    # === Constraints ===
    # Only one structure in total
    model.one_structure = Constraint(
        expr=sum(model.build_dock[p] for p in planet_list) + 
            sum(model.build_pds[p] for p in planet_list) == 1
    )

    # No planet can get both
    model.mutual_exclusive = ConstraintList()
    for p in planet_list:
        model.mutual_exclusive.add(model.build_dock[p] + model.build_pds[p] <= 1)

    # === Objective Function ===
    def utility(model):
        total = 0
        for p in planet_list:
            r = p.resources
            v = planet_values[p]
            t = planet_threats[p]
            
            # Space Dock score: high resource, low threat
            dock_score = dock_resource_weight * r - dock_threat_penalty * t
            
            # PDS score: high value, high threat
            pds_score = pds_value_weight * v + pds_threat_weight * t

            total += model.build_dock[p] * dock_score
            total += model.build_pds[p] * pds_score

        return total

    model.objective = Objective(rule=utility, sense=maximize)

    # === Solve ===
    solver = SolverFactory('glpk')
    result = solver.solve(model, tee=False)

    # Check solver status
    if result.solver.status != SolverStatus.ok or result.solver.termination_condition != TerminationCondition.optimal:
        #print("Solver failed to find an optimal solution.")
        return "failed"

    # === Output ===
    #print("\n--- Optimal Structure Placement ---")
    for p in planet_list:
        dock_value = model.build_dock[p].value
        pds_value = model.build_pds[p].value

        # Handle None values gracefully
        if dock_value is not None and dock_value > 0.5:
            #print(f"Build **Space Dock** on {p}")
            return "space dock", p
        elif pds_value is not None and pds_value > 0.5:
            #print(f"Build **PDS** on {p}")
            return "pds", p

    #print("No valid structure placement found.")
    return "failed"