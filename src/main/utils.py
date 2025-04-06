import json

def load_json(file):
    with open(file, "r") as f:
        return json.load(f)
    
from itertools import chain, combinations

def powerset(iterable):
    "powerset([s1, s2, s3]) → (), (s1,), (s2,), ..., (s1, s2, s3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))

def calculate_fleet_value(fleet, disposition):
    """
    Calculate the total value of a fleet based on the ships it contains.
    """
    return sum(disposition[ship.name] for ship in fleet)  # Assuming each ship has a 'value' attribute


# Helper functions for cube coordinates
def cube_add(a, b):
    """Add two cube coordinates."""
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])

def cube_scale(a, k):
    """Scale a cube coordinate by k."""
    return (a[0] * k, a[1] * k, a[2] * k)

# Cube directions for moving in the hex grid
# These directions follow the order:
# 0: (1, -1, 0)
# 1: (1, 0, -1)
# 2: (0, 1, -1)
# 3: (-1, 1, 0)
# 4: (-1, 0, 1)
# 5: (0, -1, 1)
cube_directions = [
    (1, -1, 0),
    (1, 0, -1),
    (0, 1, -1),
    (-1, 1, 0),
    (-1, 0, 1),
    (0, -1, 1)
]

def hex_ring(center, radius):
    """
    Generate the hexes that form a ring at a given radius from the center.
    Uses cube coordinates.
    
    Parameters:
      center (tuple): The center of the grid in cube coordinates (x, y, z).
      radius (int): The distance (radius) of the ring.
    
    Returns:
      list of tuples: Cube coordinates of hexes on the ring.
    """
    results = []
    if radius == 0:
        return [center]
    
    # Starting hex: move from center in one of the cube directions scaled by radius.
    # The redblobgames algorithm uses direction index 4 as the starting point.
    hex = cube_add(center, cube_scale(cube_directions[4], radius))
    
    # Walk around the ring in 6 directions.
    for i in range(6):
        for _ in range(radius):
            results.append(hex)
            # Move to the next hex in the current direction.
            hex = cube_add(hex, cube_directions[i])
    
    return results

def generate_concentric_rings(center, max_radius):
    """
    Generate concentric rings from the center up to the max_radius.
    
    Parameters:
      center (tuple): The center hex in cube coordinates.
      max_radius (int): The maximum radius to generate.
    
    Returns:
      list of lists: Each inner list contains the cube coordinates of a ring.
    """
    all_rings = []
    for r in range(max_radius + 1):
        ring = hex_ring(center, r)
        all_rings.append(ring)
    return all_rings

def round_cubic(qf, rf, sf):
  q = round(qf)
  r = round(rf)
  s = round(sf)
   
  q_diff = abs(q - qf)
  r_diff = abs(r - rf)
  s_diff = abs(s - sf)

  if q_diff > r_diff and q_diff > s_diff:
      q = -r - s
  elif r_diff > s_diff:
      r = -q - s
  else:
      s = -q - r

  return (q, r, s)