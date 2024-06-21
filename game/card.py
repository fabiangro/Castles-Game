from .helper import STATS
class Card:
    def __init__(self, name, cost, player_effect, enemy_effect):
        self.name = name
        self.cost = cost
        self.player_effect = player_effect
        self.enemy_effect = enemy_effect

    def to_dict(self):
        return {
            "name": self.name,
            "cost": self.cost,
            "player_effect": self.player_effect,
            "enemy_effect": self.enemy_effect
        }