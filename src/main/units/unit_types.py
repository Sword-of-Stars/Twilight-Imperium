from .ship import Ship

class Carrier(Ship):
    def __init__(self, system=None):
        super().__init__(self, 
            name = "carrier",
            combat = 9,
            move = 1,
            capacity = 4,
            cost = 3,
            sustain = False,
            system = system
            )
        
class Dreadnought(Ship):
    def __init__(self, system=None):
        super().__init__(self, 
            name = "dreadnought",
            combat = 5,
            move = 1,
            capacity = 1,
            cost = 4,
            sustain = True,
            system = system,
            special_combat = {
                "bombardment": (1, 5)
            }
            )
    def bombard(self):
        hits = sum([super().make_attack_roll() for i in range(1)])
        return hits
        
class Cruiser(Ship):
    def __init__(self, system=None):
        super().__init__(self, 
            name = "cruiser",
            combat = 7,
            move = 2,
            capacity = 0,
            cost = 2,
            sustain = False,
            system = system
            )
        
class Destroyer(Ship):
    def __init__(self, system=None):
        super().__init__(self, 
            name = "destroyer",
            combat = 9,
            move = 2,
            capacity = 0,
            cost = 2,
            sustain = False,
            system = system,
            special_combat = {
                "anti-fighter barrage": (2,9)
                }
            )
        
    def anti_fighter_barrage(self):
        hits = sum([super().make_attack_roll() for i in range(2)])
        return hits
        
class WarSun(Ship):
    def __init__(self, system=None):
        super().__init__(self, 
            name = "warsun",
            combat = 3,
            move = 2,
            capacity = 6,
            cost = 12,
            sustain = True,
            system = system,
            special = ["x planetary shield"],
            special_combat = {
                "bombardment": (3,3),
                "combat": (3,3)
                }
            )
        
    def make_attack_roll(self):
        hits = sum([super().make_attack_roll() for i in range(3)])
        return hits
    
    def bombard(self):
        hits = sum([super().make_attack_roll() for i in range(3)])
        return hits
        
class Fighter(Ship):
    def __init__(self, system=None):
        super().__init__(self, 
            name = "fighter",
            combat = 9,
            move = 0,
            capacity = 0,
            cost = 0.5,
            sustain = False,
            system = system
            )