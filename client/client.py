import time
import pygame
from client.network import Network
import client.gui_functions as gui


class CardButton:
    def __init__(self, image_path, pos, size=(140, 190)):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, size)
        self.path = image_path
        self.can_be_used = False
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pos
        self.size = size
        self.highlighted = False

    def draw(self, window):
        window.blit(self.image, self.rect.topleft)
        if not self.can_be_used:
            overlay = pygame.Surface(self.size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            window.blit(overlay, self.rect.topleft)
        if self.highlighted:
            pygame.draw.rect(window, (255, 255, 255), self.rect, 5)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def highlight(self):
        self.highlighted = True

    def unhighlight(self):
        self.highlighted = False


class Client:
    def __init__(self, name: str = 'Player', ip='localhost', port=5555):
        #: The name of the player using the client.
        self.name = name[0:8]
        self.ip = ip
        self.port = port

        #: The current state of the game.
        self.game_status = None

        #: The pygame display window.
        self.window = pygame.display.set_mode(
            (gui.width, gui.height))  # pygame.RESIZABLE maybe todo?

        #: The font used for text rendering.
        self.font = None

        #: The color used for text displaying.
        self.text_color = (255, 255, 255)

        #: The button used to determine if player is ready.
        self.start_button = None
        self.card_buttons = []

    def draw_players(self):
        player_state = self.game_status["player_state"]

        player_lines = [
            "Your resources:",
            f"builders: {player_state['builders']}",
            f"bricks: {player_state['bricks']}",
            "",
            f"soldiers: {player_state['soldiers']}",
            f"weapons: {player_state['weapons']}",
            "",
            f"mages: {player_state['mages']}",
            f"crystals: {player_state['crystals']}",
            "",
            f"castle: {player_state['castle']}",
            f"fence: {player_state['fence']}",
        ]

        player_pos_x = 10
        player_pos_y = 10
        player_labels = []

        for line in player_lines:
            player_labels.append(self.font.render(line, True, (0, 0, 0)))

        for i, line in enumerate(player_labels):
            self.window.blit(line, (player_pos_x, player_pos_y + 45*i))

        enemy_state = self.game_status["enemy_state"]

        enemy_lines = [
            "Enemy resources:",
            f"builders: {enemy_state['builders']}",
            f"bricks: {enemy_state['bricks']}",
            "",
            f"soldiers: {enemy_state['soldiers']}",
            f"weapons: {enemy_state['weapons']}",
            "",
            f"mages: {enemy_state['mages']}",
            f"crystals: {enemy_state['crystals']}",
            "",
            f"castle: {enemy_state['castle']}",
            f"fence: {enemy_state['fence']}",
        ]

        enemy_pos_x = 1020
        enemy_pos_y = 10
        enemy_labels = []

        for line in enemy_lines:
            enemy_labels.append(self.font.render(line, True, (0, 0, 0)))

        for i, line in enumerate(enemy_labels):
            self.window.blit(line, (enemy_pos_x, enemy_pos_y + 45 * i))

    def create_card_buttons(self):
        self.card_buttons = []
        cards_width = 8 * 140 + 7*10
        cards_start_pos = gui.width//2 - cards_width//2
        for i, (card, can_be_used) in enumerate(self.game_status["hand"]):
            card_name = card["name"]
            image_path = f'assets/{card_name}.png'
            pos = (cards_start_pos + i * 150, gui.height - 300)
            card_button = CardButton(image_path, pos)
            card_button.can_be_used = can_be_used
            self.card_buttons.append(card_button)

    def draw_card_buttons(self):
        for card_button in self.card_buttons:
            card_button.draw(self.window)

    def get_card_click(self, mouse_pos, mouse_button):
        if mouse_button == 1:  # Left mouse button
            for i, card_button in enumerate(self.card_buttons):
                if card_button.is_clicked(mouse_pos):
                    return f"use {i}"
        elif mouse_button == 3:  # Right mouse button
            for i, card_button in enumerate(self.card_buttons):
                if card_button.is_clicked(mouse_pos):
                    return f"replace {i}"
        return None

    def draw_skip_button(self):
        self.window.blit(gui.skip_button_image, gui.button_check_location)

    def handle_mouse_motion(self, mouse_pos):
        for card_button in self.card_buttons:
            if card_button.rect.collidepoint(mouse_pos):
                card_button.highlight()
            else:
                card_button.unhighlight()

    def draw_turn(self):
        text = "Your turn" if self.game_status[
            "turn"] else f"{self.game_status['enemy_name']}'s turn"
        turn = self.font.render(text, True, self.text_color)

        text_width, text_height = self.font.size(text)
        text_location = (gui.width//2 - text_width//2, gui.height - 40)

        self.window.blit(turn, text_location)

    def draw_all(self):
        if self.game_status == "Game did not start yet":
            self.window.blit(gui.background_image, (0, 0))
            pygame.display.update()
            return

        if isinstance(self.game_status, str) and self.game_status.startswith(
                "End of Game"):
            pass

        self.draw_card_buttons()
        self.draw_players()
        self.draw_castles()
        self.draw_skip_button()
        self.draw_turn()
        pygame.display.update()

    def draw_ready_players(self, dots) -> None:
        text = self.game_status["ready"]
        font = pygame.font.SysFont('arial', 80, bold=True)
        turn = font.render(text, True, self.text_color)

        text_width, text_height = font.size(text)
        text_location = (gui.width // 2 - text_width // 2,
                         gui.height//2 - text_height//2)

        dots_text = font.render("." * dots, True, self.text_color)

        self.window.blit(turn, text_location)
        dots_location = (gui.width // 2 + text_width//2,
                         gui.height//2 - text_height//2)
        self.window.blit(dots_text, dots_location)

    def draw_who_win(self) -> None:
        text_location = (gui.width // 2 - 100, gui.height - 90)

        text = f"The game has ended, the player {self.game_status['win']} has won!"
        win = self.font.render(text, True, self.text_color)
        self.window.blit(win, text_location)

    def draw_castles(self):
        player_height = max(1, self.game_status["player_state"]["castle"] / 100 * 400)
        enemy_height = max(1, self.game_status["enemy_state"]["castle"] / 100 * 400)

        castle_img_path = "assets/castle.png"
        player_castle = pygame.image.load(castle_img_path)
        player_castle = pygame.transform.scale(player_castle, (150, player_height))

        enemy_castle = pygame.image.load(castle_img_path)
        enemy_castle = pygame.transform.scale(enemy_castle, (150, enemy_height))

        self.window.blit(player_castle, (gui.width//2 - 200, 550 - player_height))
        self.window.blit(enemy_castle, (gui.width//2 + 50, 550 - enemy_height))

    def get_click(self, mouse_pos):
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

        return None

    def start(self, ip='localhost', port=5556):
        """Initialize gui and connection to the server, and run the game.
        """

        pygame.display.set_caption(gui.title)
        pygame.font.init()
        self.font = pygame.font.SysFont('arial', 30, bold=True)

        self.start_button = gui.OptionBox(gui.width//2 - 100, 50,
                                          200, 40, (150, 150, 150),
                                          (100, 200, 255), self.font,
                                          ["Ready?", "Start", "Wait"])

        client = Network(ip, port)
        client.connect()
        self.main_loop(client)
        client.close()

    def main_loop(self, client) -> None:
        """Handle game events, and display gui.

        :param client: Network object used to connect to the server.
        """
        action = ["get"]

        clock = pygame.time.Clock()
        client.send("name " + self.name)
        t0 = time.time()
        dummy_timer = 0

        while True:
            clock.tick(gui.fps)

            client.send(action[0])
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
                    mouse_button = event.button

                    clicked = self.get_click(mouse_pos)

                    if clicked == "skip":
                        action[0] = clicked if clicked else "get"
                    else:
                        clicked_card = self.get_card_click(mouse_pos,
                                                           mouse_button)
                        if isinstance(clicked_card, str):
                            action[0] = f"move {clicked_card}"
                        else:
                            action[0] = "get"

            self.window.blit(gui.background_image, (0, 0))

            if not game_status["start"]:
                self.start_button.selected = 0
                self.start_button.draw(self.window)

                if time.time() - t0 > 0.3:
                    dummy_timer = (dummy_timer + 1) % 4
                    t0 = time.time()

                self.draw_ready_players(dummy_timer)

                pygame.display.update()

                clicked_option = self.start_button.update(event_list)
                if clicked_option == "Start":
                    action[0] = "start"
                elif clicked_option == "Wait":
                    action[0] = "wait"

            elif game_status["win"]:
                self.draw_who_win()
                self.start_button.selected = 0
                self.start_button.draw(self.window)
                self.draw_all()

                clicked_option = self.start_button.update(event_list)
                if clicked_option == "Start":
                    action[0] = "start"
                elif clicked_option == "Wait":
                    action[0] = "wait"

            else:
                if not (game_status["turn"]):
                    pass

                if game_status["turn"]:
                    mouse_pos = pygame.mouse.get_pos()
                    self.handle_mouse_motion(mouse_pos)

                self.draw_all()
                self.create_card_buttons()

            pygame.display.update()

