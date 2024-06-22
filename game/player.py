class Player:
    STARTING_RESOURCES = {
        "builders": 2,
        "soldiers": 2,
        "mages": 2,

        "bricks": 2,
        "weapons": 2,
        "crystals": 2,

        "castle": 30,
        "fence": 10
    }

    def __init__(self, player_id):
        self.id = player_id
        self.lost = False
        self.name = ""
        self.ready = False
        self.hand = []

        self.resources = {
            "builders": 2,
            "soldiers": 2,
            "mages": 2,

            "bricks": 2,
            "weapons": 2,
            "crystals": 2,

            "castle": 30,
            "fence": 10
        }

    def resources_turn(self):
        self.resources["bricks"] += self.resources["builders"]
        self.resources["weapons"] += self.resources["soldiers"]
        self.resources["crystals"] += self.resources["mages"]

    def give_damage(self, dmg):
        attack = self.resources["fence"] - dmg

        self.resources["castle"] += min(0, attack)
        self.resources["castle"] = max(0, self.resources["castle"])

        self.resources["fence"] = max(0, attack)

        self.lost = self.resources["castle"] == 0

    def can_be_played(self, card):
        for resource, value in card.cost.items():
            if resource != "damage":
                new_value = self.resources[resource] + value
                if new_value < 0 and resource not in ["castle", "fence"]:
                    return False
        return True

    def update_state(self, effect):
        for resource, value in effect.items():
            if resource != "damage":
                new_value = self.resources[resource] + value
                self.resources[resource] = max(new_value, 0)
            else:
                self.give_damage(value)

        for resource in ["builders", "soldiers", "mages"]:
            if self.resources[resource] == 0:
                self.resources[resource] = 1

        self.lost = self.resources["castle"] == 0
