import json
from random import choice
from copy import deepcopy
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
        self.debug_last_action = ""
        self.cards = []
        self.last_used_card = None
        with open("game/cards.jsonl") as file:
            for line in file:
                c = json.loads(line)
                card = Card(c["name"], c["cost"],
                            c["player_effect"], c["enemy_effect"])
                self.cards.append(card)

    def start(self):
        self.has_started = True
        self.start_turn = (self.start_turn + 1) % 2
        self.turn = self.start_turn
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
        self.last_used_card = None
        self.start_turn = (self.start_turn + 1) % 2

        for player in self.players.values():
            player.lost = False
            player.resources = deepcopy(Player.STARTING_RESOURCES)

        self.reset_turn()

    def player_use_card(self, current_player, enemy_player, card):
        current_player.update_state(card.cost)

        if card.name == "Thief":  # only card using enemy resources
            # steal no more than 5 from each enemy resource
            for res in ["bricks", "weapons", "crystals"]:
                card.player_effect[res] = min(enemy_player.resources[res], 5)

        current_player.update_state(card.player_effect)
        enemy_player.update_state(card.enemy_effect)

    def reset_turn(self):
        self.win = False
        self.has_started = False
        self.empty_hands()
        for player in self.players.values():
            player.ready = False

    def empty_hands(self):
        for player in self.players.values():
            player.hand = []

    def next_turn(self, player, enemy):
        self.turn = (self.turn + 1) % 2

        if player.resources["castle"] == 100:
            enemy.lost = True
        if enemy.lost:
            self.win = player.name
        else:
            enemy.resources_turn()

    def ready_players(self):
        return len(
            [player for player in self.players.values() if player.ready])

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

        elif self.player_index_by_id(player_id) != self.turn:
            pass

        elif action == "get":
            return self.get_game_status(current_player)

        elif action.startswith("skip"):
            self.next_turn(current_player, enemy_player)

        elif action.startswith("move"):
            action = action.split()

            action_type = action[1]  # 'use' or 'replace'
            card_index = int(action[2])  # card index from current player hand
            card = current_player.hand[card_index]
            if action_type == "use" and current_player.can_be_played(card):
                self.player_use_card(current_player, enemy_player, card)
            elif action_type == "replace":
                pass
            else:
                # unexpected action, e.g. card cannot be played
                return self.get_game_status(current_player)

            self.last_used_card = {"name": card.name, "action": action_type}
            current_player.hand[card_index] = choice(self.cards)
            self.next_turn(current_player, enemy_player)
        else:
            print(f"unexpected action value={action}")

        return self.get_game_status(current_player)

    def is_full(self):
        return len(self.players) == 2

    def get_game_status(self, current_player):
        enemy_player = None
        for player in self.players.values():
            if player is not current_player:
                enemy_player = player

        game_status = {
            "start": self.has_started,
            "win": self.win,
            "lost": current_player.lost,
            "turn": self.turn == self.player_index_by_player(current_player),
            "player": {"state": current_player.resources,
                       "name": current_player.name},
            "enemy": {"state": enemy_player.resources if enemy_player else None,
                      "name": enemy_player.name if enemy_player else None},
            "hand": [{"name": card.name,
                      "can_be_used": current_player.can_be_played(card)}
                     for card in current_player.hand],
            "last_used": self.last_used_card,
            "ready": f"Waiting for players {self.ready_players()}/2"
        }
        return game_status

    def get_enemy_player(self, current_player_id):
        for player_id in self.players:
            if player_id != current_player_id:
                return self.players[player_id]

    def player_index_by_id(self, player_id: int) -> int:

        for index, id_ in enumerate(self.players.keys()):
            if id_ == player_id:
                return index

    def player_index_by_player(self, player: Player) -> int:

        for index, name in enumerate(self.players.values()):
            if name is player:
                return index
