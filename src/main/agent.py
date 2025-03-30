import json

class Agent():
    def __init__(self):
        self.disposition = {
            "resource wastefulness": 1,
            "influence wastefulness": 1,

            "influence":1,
            "resources":1,

            "risk tolerance": 1,
            "point focus": 1,

            "fighter": 1,
            "carrier": 1,
            "cruiser": 1,
            "destroyer": 1,
            "dreadnought": 1,
            "infantry": 1,
            "space dock": 1,
            "PDS": 1
        }

    def strategic_model(self, game):
        pass

    def tactical_model(self, action, game):
        if action == "expand":
            pass
        elif action == "reinforce":
            pass
        elif action == "produce":
            pass
