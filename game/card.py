from .helper import STATS
class Card:
    def __init__(self, name="losowanazwa", player_effect=STATS, enemy_effect=STATS):
        self.name = name
        self.player_effect = player_effect
        self.enemy_effect = enemy_effect
