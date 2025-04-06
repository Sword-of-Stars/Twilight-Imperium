from pyomo.environ import *

def get_command_counters(player):
    # === Input Data ===
    planets = player.get_readied_planets()

    influence_per_cc = 3
    waste_aversion = player.disposition["resource wastefulness"]  # How much you dislike wasting resources

    # === Pyomo Model ===
    model = ConcreteModel()

    # Variables
    model.exhaust = Var(planets, domain=Binary)
    model.extra_ccs = Var(within=NonNegativeIntegers)
    
    # Expressions
    model.total_influence = Expression(
        rule=lambda m: sum(p.influence * m.exhaust[p] for p in planets)
    )
    model.total_resources = Expression(
        rule=lambda m: sum(p.resources * m.exhaust[p] for p in planets)
    )
    model.required_influence = Expression(rule=lambda m: m.extra_ccs * influence_per_cc)
    model.resource_waste = Expression(rule=lambda m: m.total_resources)

    # Constraints
    model.influence_sufficient = Constraint(
        expr=model.total_influence >= model.required_influence
    )
  
    # Objective: Maximize CCs gained while minimizing wasted resources
    model.objective = Objective(
        expr=model.extra_ccs - waste_aversion * model.resource_waste,
        sense=maximize
    )

    # Solve
    solver = SolverFactory('glpk')
    solver.solve(model)

    # Output
    '''print("\n--- Extra Command Counters ---")
    print(f"Bought: {int(model.extra_ccs.value)}")

    print("\n--- Planets Exhausted ---")'''
    exhausted_planets = [p for p in planets if model.exhaust[p].value == 1.0]

    '''print(f"\nTotal Influence Used: {model.total_influence():.2f}")
    print(f"Influence Required: {model.required_influence():.2f}")
    print(f"Wasted Resources: {model.resource_waste():.2f}")'''

    return int(model.extra_ccs.value), exhausted_planets
