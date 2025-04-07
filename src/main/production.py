import pyomo.environ as pyo
from units import Carrier, Cruiser, Destroyer, Dreadnought, WarSun, Fighter, GroundForce, Ship

def produce(player, system):
    # Create model
    model = pyo.ConcreteModel("Unit Production with Planet Exhaustion and Influence Waste")

    # Define unit types and their attributes
    units = [Carrier(), Cruiser(), Destroyer(), Dreadnought(), WarSun(), Fighter(), GroundForce()]
    unit_names = [unit.name for unit in units]

    # Unit properties
    cost = {unit.name: unit.cost for unit in units}
    combat_value = {unit.name: unit.combat for unit in units}
    capacities = {unit.name: unit.capacity for unit in units}

    # Define decision variables (integer values for unit production)
    model.x = pyo.Var(unit_names, within=pyo.NonNegativeIntegers)

    # Define planet exhaustion variables
    planet_names = [planet.name for planet in player.planets]
    resources = {planet.name: planet.resources for planet in player.planets}  # Resource values
    influence = {planet.name: planet.influence for planet in player.planets}  # Influence values
    model.e = pyo.Var(planet_names, within=pyo.Binary)  # 1 if planet is exhausted, 0 otherwise

    # Total available resources and influence from exhausted planets
    model.available_resources = pyo.Expression(expr=sum(resources[p] * model.e[p] for p in planet_names))
    model.available_influence = pyo.Expression(expr=sum(influence[p] * model.e[p] for p in planet_names))

    # Constraint: Total unit cost must not exceed available resources
    model.budget_constraint = pyo.Constraint(
        expr=sum(cost[u] * model.x[u] for u in unit_names) <= model.available_resources
    )

    # Auxiliary variables for even-number enforcement
    model.y = pyo.Var(["infantry", "fighter"], within=pyo.NonNegativeIntegers)

    # Enforce Ground Forces & Fighters to be even
    model.even_constraints = pyo.ConstraintList()
    for unit in ["infantry", "fighter"]:
        model.even_constraints.add(model.x[unit] == 2 * model.y[unit])

    # Fighter capacity constraint
    vacant_capacity = 0  # Example vacant capacity term
    fighter_capacity = sum(model.x[u] * units[i].capacity for i, u in enumerate(unit_names) if isinstance(units[i], Ship))
    model.fighter_capacity_constraint = pyo.Constraint(expr=model.x["fighter"] <= fighter_capacity + vacant_capacity)

    # Constraint: Maximum number of total units produced
    max_units = sum([planet.has_space_dock * (planet.resources + 3) for planet in system.planets])  # Example maximum unit count
    model.max_units_constraint = pyo.Constraint(expr=sum(model.x[u] for u in unit_names) <= max_units)

    # Define resource waste variable
    model.resource_waste = pyo.Var(within=pyo.NonNegativeReals)
    
    # Resource waste constraint (difference between available resources and spending)
    model.resource_waste_constraint = pyo.Constraint(
        expr=model.resource_waste >= model.available_resources - sum(cost[u] * model.x[u] for u in unit_names)
    )

    # Define influence waste variable: If a planet is exhausted, its influence is wasted
    model.influence_waste = pyo.Var(within=pyo.NonNegativeReals)
    
    # Influence waste constraint (if a planet is exhausted for resources, its influence is wasted)
    model.influence_waste_constraint = pyo.Constraint(
        expr=model.influence_waste == sum(influence[p] * model.e[p] for p in planet_names)
    )

    # New Constraint: Limit non-fighter, non-infantry ships based on fleet supply
    non_fighter_units = [u.name for u in units if not isinstance(u, Fighter) and not isinstance(u, GroundForce)]
    existing_non_fighter_ships = sum(1 for ship in system.space_area if ship.owner == player and ship.name in non_fighter_units)
    model.fleet_supply_constraint = pyo.Constraint(
        expr=sum(model.x[u] for u in non_fighter_units) + existing_non_fighter_ships <= player.command_counters["fleet"]
    )

    # Objective: Maximize combat effectiveness - penalties for resource and influence waste
    waste_penalty = player.disposition["resource wastefulness"]  # Adjust to balance combat power vs. minimizing resource waste
    influence_penalty = (1-waste_penalty)  # Penalty for wasting influence
    model.objective = pyo.Objective(
        expr=sum(combat_value[u] * model.x[u] for u in unit_names) 
        - waste_penalty * model.resource_waste 
        - influence_penalty * model.influence_waste,
        sense=pyo.maximize
    )

    # Solve
    solver = pyo.SolverFactory('glpk')
    solver.solve(model)

    # Display results
    units_produced = {u: model.x[u]() for u in unit_names}

    exhausted_planets = []
    for p in planet_names:
        if model.e[p]() == 1:
            exhausted_planets.append(p)
    exhausted_planets = [p for p in player.planets if p.name in exhausted_planets]

    return units_produced, exhausted_planets