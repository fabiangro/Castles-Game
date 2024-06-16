import pygame
from client.network import Network
import client.gui_functions as gui


class Client:
    """Represents a client, with gui handling.

    :param name: The name of the player using the client.
    """


    def __init__(self, name: str = 'Player'):
        #: The name of the player using the client.
        self.name = name[0:8]

        #: The current state of the game.
        self.game_status = None

        #: The pygame display window.
        self.window = pygame.display.set_mode(
            (gui.width, gui.height))

        #: The font used for text rendering.
        self.font = None

        #: The color used for text displaying.
        self.text_color = (255, 255, 255)

        #: The button used for displaying options.
        self.options_button = None

        #: The button used to determine if player is ready.
        self.start_button = None

    def draw_players(self):
        """Display text: player's name, number of cards, moves for every player in current game.
        """

        players_locations = gui.players_cards(
            self.game_status["players"])

        for player in players_locations:

            text1 = player
            text2 = f"resources: {players_locations[player][0]}" if \
            players_locations[player][0] != 0 else "Eliminated"
            text1 = self.font.render(text1, True, self.text_color)
            text2 = self.font.render(text2, True, self.text_color)

            self.window.blit(text1, (10, 10))
            self.window.blit(text2, (10, 30))

            # player_moves = [move for p, move in self.game_status["moves"] if
            #                 "You: " + p == player or p == player]
            # move_font_size = pygame.font.SysFont('arial', 15)
            #
            # for i, move in enumerate(player_moves):
            #     move = move_font_size.render(" ".join(move), True,
            #                                  self.text_color)
            #     self.window.blit(move, (players_locations[player][1][0],
            #                             players_locations[player][1][
            #                                 1] + 60 + 20 * i))

    # def draw_checked_move(self):
    #     """Draw result of check action by any player with information who checked, who was checked, who gets the card.
    #     """
    #
    #     cards_location = gui.get_cards_location(
    #         self.game_status["checked"])
    #     check_result = self.game_status["check_result"]
    #
    #     text_color = (255, 255, 255)
    #
    #     upper_text = f"{check_result[0]} checked {check_result[1]}'s move: {' '.join(self.game_status['moves'][-1][1])}!"
    #     down_text = f"{check_result[2]} gets the card!"
    #
    #     upper_text = self.font.render(upper_text, True, text_color)
    #     down_text = self.font.render(down_text, True, text_color)
    #
    #     self.window.blit(upper_text, (50, 60))
    #     self.window.blit(down_text, (335, 475))
    #
    #     if check_result[3]:
    #         loser_text = f"That was the last card, {check_result[2]} is eliminated!"
    #         loser_text = self.font.render(loser_text, True, text_color)
    #         self.window.blit(loser_text, (150, 540))
    #
    #     for image, location in cards_location.items():
    #         self.window.blit(image, location)

    # def draw_hand(self):
    #     """Draw player using client cards.
    #     """
    #
    #     hand = self.game_status["hand"]
    #     cards_location = gui.hand_to_cards_location(hand)
    #
    #     for card_image, location in cards_location.values():
    #         self.window.blit(card_image, location)

    def draw_check_buttons(self):
        """Draw button for checking moves.
        """

        self.window.blit(gui.skip_button_image,
                         gui.button_check_location)
        self.window.blit(gui.show_button_image,
                         gui.button_check_location2)

    def draw_turn(self):
        """Display text who turn it is.
        """

        text_location = (gui.width // 2, gui.height - 40)

        text = "Your turn" if self.game_status[
            "turn"] else f"{self.game_status['enemy_name']}'s turn"
        turn = self.font.render(text, True, self.text_color)
        self.window.blit(turn, text_location)

    def draw_all(self):
        """If game has started draw: players, hand, check button, turn.
        """

        if self.game_status == "Game did not start yet":
            self.window.blit(gui.background_image, (0, 0))
            pygame.display.update()
            return

        if isinstance(self.game_status, str) and self.game_status.startswith(
                "End of Game"):
            pass

        self.draw_players()

        self.draw_check_buttons()
        self.draw_turn()

        pygame.display.update()

    def draw_ready_players(self) -> None:
        """Draw how many players are ready.
        """

        text_location = (gui.width // 2 - 50, gui.height - 40)

        text = self.game_status["ready"]
        turn = self.font.render(text, True, self.text_color)
        self.window.blit(turn, text_location)

    def draw_who_win(self) -> None:
        """Draw who win.
        """

        text_location = (gui.width // 2 - 100, gui.height - 90)

        text = f"The game has ended, the player {self.game_status['win']} has won!"
        win = self.font.render(text, True, self.text_color)
        self.window.blit(win, text_location)

    def get_click(self, mouse_pos):
        """Check if the check button was clicked.

        :param mouse_pos: Mouse position when clicked.
        :return: If check button was clicked returns "check", None otherwise.
        """

        if self.game_status == "Game did not start yet":
            return None

        if isinstance(self.game_status, str) and self.game_status.startswith(
                "End of Game"):
            return None

        mouse_x, mouse_y = mouse_pos

        check_button_width, check_button_height = gui.button_size

        check_button_x, check_button_y = gui.button_check_location

        if check_button_x <= mouse_x <= check_button_x + check_button_width and \
                check_button_y <= mouse_y <= check_button_y + check_button_height:
            return "skip"

        check_button2_x, check_button2_y = gui.button_check_location2

        if check_button2_x <= mouse_x <= check_button2_x + check_button_width and \
                check_button2_y <= mouse_y <= check_button2_y + check_button_height:
            return "show"

        return None

    def start(self, ip='localhost', port=5556):
        """Initialize gui and connection to the server, and run the game.
        """

        pygame.display.set_caption(gui.title)
        pygame.font.init()
        self.font = pygame.font.SysFont('arial', 30)
        self.options_button = gui.OptionBox(gui.width - 220, 40,
                                            200, 40, (150, 150, 150),
                                            (100, 200, 255), self.font,
                                            ["MOVE", "USE", "REPLACE"])
        self.start_button = gui.OptionBox(gui.width - 220, 40,
                                          200, 40, (150, 150, 150),
                                          (100, 200, 255), self.font,
                                          ["Ready?", "Start", "Wait"])

        client = Network(ip, port)
        client.connect()
        self.main_loop(client)
        client.close()

    def button_update(self, option_list) -> None:
        """Update the option list for option button.

        :param option_list: List of options to apply to the option button.
        """

        self.options_button.update_display(option_list)

    def main_loop(self, client) -> None:
        """Handle game events, and display gui.

        :param client: Network object used to connect to the server.
        """

        action = ["get"]

        move = "move "
        clock = pygame.time.Clock()
        client.send("name " + self.name)

        while True:
            clock.tick(gui.fps)



            client.send(action[0])
            if action[0].startswith("move"):
                move = "move "
            action[0] = "get"

            self.game_status = client.receive_data()
            game_status = self.game_status
            event_list = pygame.event.get()

            for event in event_list:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.MOUSEBUTTONUP:
                    mouse_pos = pygame.mouse.get_pos()
                    clicked = self.get_click(mouse_pos)
                    if clicked == "show":
                        if isinstance(self.game_status,
                                      dict) and "player_state" in self.game_status and "enemy_state" in self.game_status:
                            player_state = self.game_status["player_state"]
                            enemy_state = self.game_status["enemy_state"]
                            print(f"\nYour resources={player_state}")
                            print(f"Enemy resources={enemy_state}")
                            print()
                            print("Your cards:")
                            for card, can_be_used in self.game_status["hand"]:
                                print(card["name"].upper(), f"can use={can_be_used}", end="\n\t")
                                print("YOU:", {x: y for x, y in card["player_effect"].items() if y != 0}, end="\n\t")
                                print("ENEMY:", {x: y for x, y in card["enemy_effect"].items() if y != 0}, end="\n")
                    elif clicked == "skip":
                        action[0] = clicked if clicked else "get"

            self.window.blit(gui.background_image, (0, 0))

            if not game_status["start"]:
                self.start_button.selected = 0
                self.start_button.draw(self.window)
                self.draw_ready_players()

                pygame.display.update()

                clicked_option = self.start_button.update(event_list)
                if clicked_option == "Start":
                    action[0] = "start"
                elif clicked_option == "Wait":
                    action[0] = "wait"

            else:
                if not (game_status["turn"]):
                    self.options_button.option_list = ["MOVE", "USE", "REPLACE"]

                if game_status["turn"]:

                    self.options_button.draw(self.window)
                    self.options_button.selected = 0
                    clicked_option = self.options_button.update(event_list)

                    if isinstance(clicked_option,
                                  str) and clicked_option != "MOVE":

                        if clicked_option == "RESET":
                            self.options_button.update_display(["MOVE", "USE", "REPLACE"])
                            move = "move "

                        elif clicked_option in ["USE", "REPLACE"]:
                            self.button_update(
                                [clicked_option] + [f"Card {i}" for i in range(1, 9)] + ["RESET"])
                            if clicked_option not in move:
                                move += clicked_option.lower() + " "

                        elif clicked_option in [f"Card {i}" for i in range(1, 9)]:
                            move += clicked_option.lower()
                            action[0] = move

                self.draw_all()

