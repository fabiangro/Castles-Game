from random import choice
from .player import Player
from .card import Card


class AntsGame:
    player_cards = 8
    def __init__(self):
        self.players = dict()
        self.turn = 0
        self.start_turn = 0
        self.has_started = False
        self.win = False
        self.cards = []
        self.debug_last_action = ""

    def start(self):
        self.init_cards()
        self.has_started = True
        self.deal_cards()

    def deal_cards(self):
        for player in self.players.values():
            for i in range(AntsGame.player_cards):
                player.hand.append(choice(self.cards))

    def add_player(self, player_id):
        player = Player(player_id)
        self.players[player_id] = player

    def remove_player(self, player_id):
        del self.players[player_id]

    def reset_game(self):
        self.start_turn = (self.start_turn + 1) % 2
        self.turn = self.start_turn

        for player in self.players.values():
            player.lost = False
            player.resources = Player.STARTING_RESOURCES

        self.reset_turn()

    def reset_turn(self):
        self.win = False
        self.empty_hands()
        for player in self.players.values():
            player.ready = False

    def empty_hands(self):
        for player in self.players.values():
            player.hand = []

    def next_turn(self):
        self.turn = (self.turn + 1) % 2

    def ready_players(self):
        return len([player for player in self.players.values() if player.ready])

    def players_are_ready(self):
        if len(self.players) < 2:
            return False
        for player in self.players.values():
            if not player.ready:
                return False
        return True

    def player_action(self, player_id, action: str):


        current_player = self.players[player_id]
        enemy_player = self.get_enemy_player(player_id)

        if action != self.debug_last_action and current_player and enemy_player and action != 'get':

            print(f"id={player_id} name={current_player.name} action=|{action}|")
            for player in self.players.values():
                print(player.resources)
            print()
            # self.debug_last_action = action
            # print(f"curr player:")
            # print(current_player.name)
            # print(current_player.resources)
            # print()
            # print(f"enem player:")
            # print(enemy_player.name)
            # print(enemy_player.resources)

        if self.win:
            if action == "start":
                self.reset_game()

            return self.get_game_status(current_player)

        elif action.startswith("name"):
            name = action.split()[1]
            current_player.name = name

        elif not self.has_started:
            if self.players_are_ready():
                self.reset_game()
                self.start()
            else:
                if action == "start":
                    current_player.ready = True
                elif action == "wait":
                    current_player.ready = False

            return self.get_game_status(current_player)

        elif current_player.lost:
            pass

        elif self.player_index_by_id(player_id) != self.turn:
            pass

        elif action == "get":
            pass

        elif action.startswith("use"):
            used_card_index = int(action.split()[1])
            used_card = current_player.hand(used_card_index)

            if current_player.can_be_played(used_card):
                current_player.update_state(used_card.player_effect)
                enemy_player.update_state(used_card.enemy_effect)

                current_player.hand[used_card_index] = choice(self.cards)
                enemy_player.resources_turn()
                self.next_turn()

        elif action.startswith("skip"):
            enemy_player.resources_turn()
            self.next_turn()

        elif action.startswith("replace"):
            used_card_index = int(action.split()[1])
            current_player.hand[used_card_index] = choice(self.cards)
            enemy_player.resources_turn()
            self.next_turn()

        return self.get_game_status(current_player)

    def is_full(self) -> bool:
        return len(self.players) == 2

    def get_game_status(self, current_player):
        enemy_player = None
        for player in self.players.values():
            if player is not current_player:
                enemy_player = player

        game_status = {
            "start": self.has_started,
            "lost": current_player.lost,
            "name": current_player.name,
            "enemy_name": enemy_player.name if enemy_player else None,
            "hand": [({
                        "name": card.name,
                        "player_effect": card.player_effect,
                        "enemy_effect": card.enemy_effect
                      }, current_player.can_be_played(card))
                     for card in current_player.hand],
            "win": self.win,
            "player_state": current_player.resources,
            "enemy_state": enemy_player.resources if enemy_player else None,
            "turn": self.turn == self.player_index_by_player(current_player),
            "ready": f"Waiting for players {self.ready_players()}/2",
        }
        if enemy_player:
            game_status["players"] = [(enemy_player.name, enemy_player.resources)]
        return game_status

    def get_enemy_player(self, current_player_id):
        for player_id in self.players:
            if player_id != current_player_id:
                return self.players[player_id]


    def player_index_by_id(self, player_id: int) -> int:

        for index, id in enumerate(self.players.keys()):
            if id == player_id:
                return index

    def player_index_by_player(self, player: Player) -> int:

        for index, name in enumerate(self.players.values()):
            if name is player:
                return index



    def init_cards(self):
        self.cards = [
            Card("builderplus",
                {
                "builders": 1,
                "soldiers": 0,
                "mages": 0,

                "bricks": 0,
                "weapons": 0,
                "crystals": 0,

                "castle": 0,
                "fence": 0,

                "damage": 0
            },
            {
                "builders": 0,
                "soldiers": 0,
                "mages": 0,

                "bricks": 0,
                "weapons": 0,
                "crystals": 0,

                "castle": 0,
                "fence": 0,

                "damage": 0
                }),
            Card("curse",
                 {
                     "builders": 1,
                     "soldiers": 1,
                     "mages": 1,

                     "bricks": 1,
                     "weapons": 1,
                     "crystals": 1,

                     "castle": 1,
                     "fence": 1,

                     "damage": 1
                 },
                 {
                     "builders": -1,
                     "soldiers": -1,
                     "mages": -1,

                     "bricks": -1,
                     "weapons": -1,
                     "crystals": -1,

                     "castle": -1,
                     "fence": -1,

                     "damage": -1
                 }),
            Card("chuj",
                 {
                     "builders": 0,
                     "soldiers": 0,
                     "mages": 0,

                     "bricks": 0,
                     "weapons": 0,
                     "crystals": 0,

                     "castle": 8,
                     "fence": 0,

                     "damage": 0
                 },
                 {
                     "builders": 0,
                     "soldiers": 0,
                     "mages": 0,

                     "bricks": 0,
                     "weapons": 0,
                     "crystals": 0,

                     "castle": -4,
                     "fence": 0,

                     "damage": 0
                 }),
            Card("name",
                 {
                     "builders": 0,
                     "soldiers": 0,
                     "mages": 0,

                     "bricks": 0,
                     "weapons": 0,
                     "crystals": 0,

                     "castle": 8,
                     "fence": -4,

                     "damage": 0
                 },
                 {
                     "builders": 0,
                     "soldiers": 0,
                     "mages": 0,

                     "bricks": 0,
                     "weapons": 0,
                     "crystals": 0,

                     "castle": 0,
                     "fence": 0,

                     "damage": 0
                 }),
            Card("enemystock",
                 {
                     "builders": 0,
                     "soldiers": 0,
                     "mages": 0,

                     "bricks": 0,
                     "weapons": -12,
                     "crystals": 0,

                     "castle": 0,
                     "fence": 0,

                     "damage": 0
                 },
                 {
                     "builders": 0,
                     "soldiers": 0,
                     "mages": 0,

                     "bricks": -12,
                     "weapons": -12,
                     "crystals": -12,

                     "castle": 0,
                     "fence": 0,

                     "damage": 0
                 }),
            Card("name",
                 {
                     "builders": 0,
                     "soldiers": 0,
                     "mages": 0,

                     "bricks": 0,
                     "weapons": 0,
                     "crystals": 0,

                     "castle": 0,
                     "fence": 0,

                     "damage": 0
                 },
                 {
                     "builders": 0,
                     "soldiers": 0,
                     "mages": 0,

                     "bricks": 0,
                     "weapons": 0,
                     "crystals": 0,

                     "castle": 0,
                     "fence": 0,

                     "damage": 0
                 }),
            Card("katachuj",
                 {
                     "builders": 0,
                     "soldiers": 0,
                     "mages": 0,

                     "bricks": 0,
                     "weapons": 12,

                     "castle": 0,
                     "fence": 0,

                     "damage": 0
                 },
                 {
                     "builders": 0,
                     "soldiers": 0,
                     "mages": 0,

                     "bricks": 0,
                     "weapons": 0,
                     "crystals": 0,

                     "castle": 0,
                     "fence": 0,

                     "damage": 10
                 }),
        ]


















