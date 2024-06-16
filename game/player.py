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
    def __init__(self, id):
        self.id = id
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
        print("resources turn name=", self.name)
        self.resources["bricks"] += self.resources["builders"]
        self.resources["weapons"] += self.resources["soldiers"]
        self.resources["crystals"] += self.resources["mages"]

    def give_damage(self, dmg):
        if self.resources["fence"] < dmg:
            dmg -= self.resources["fence"]
            self.resources["fence"] = 0
            self.resources["castle"] -= dmg
            if self.resources["castle"] <= 0:
                self.resources["castle"] = 0
                self.lost = True
        else:
            self.resources["fence"] -= dmg

    def can_be_played(self, card):
        for resource, value in card.player_effect.items():
            if resource != "damage":
                new_value = self.resources[resource] + value
                if new_value <= 0 and resource not in ["castle", "fence"]:
                    return False
        return True

    def update_state(self, card_effect):
        for resource, value in card_effect:
            if resource != "damage":
                new_value = self.resources[resource] + value
                self.resources[resource] = new_value if new_value >= 0 else 0

        for resource in ["builders", "soldiers", "mages"]:
            if self.resources[resource] == 0:
                self.resources[resource] = 1

        self.give_damage(card_effect["damage"])

