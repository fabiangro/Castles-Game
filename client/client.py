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
    CARD_WIDTH = 140
    CARD_HEIGHT = 190
    CARD_SIZE = (CARD_WIDTH, CARD_HEIGHT)

    def __init__(self, name: str = 'Player', ip='localhost', port=5555):
        #: The name of the player using the client.
        self.name = name[0:8]
        self.ip = ip
        self.port = port

        #: The current state of the game.
        self.game_status = None

        #: The pygame display window.
        self.window = pygame.display.set_mode((gui.width, gui.height),
                                             pygame.RESIZABLE, 0)  # pygame.RESIZABLE maybe todo?
        self.bg_image = pygame.image.load('assets/bg.jpg')
        self.background = pygame.transform.scale(self.bg_image, (gui.width, gui.height))
        #: The font used for text rendering.
        self.font = None

        #: The color used for text displaying.
        self.text_color = (255, 255, 255)
        self.font_size = 30

        #: The button used to determine if player is ready.
        self.start_button = None
        self.card_buttons = []

    def draw_player_stocks(self, player_state, pos, title_width):
        player_lines = [
            f"BUILDERS: {player_state['builders']}",
            f"Bricks: {player_state['bricks']}",
            "",
            f"SOLDIERS: {player_state['soldiers']}",
            f"Weapons: {player_state['weapons']}",
            "",
            f"MAGES: {player_state['mages']}",
            f"Crystals: {player_state['crystals']}",
            "",
            f"Castle: {player_state['castle']}",
            f"Fence: {player_state['fence']}",
        ]
        player_pos_x, player_pos_y = pos

        for i, line in enumerate(player_lines):
            text = self.font.render(line, True, (0, 0, 0))
            line_width, line_height = self.font.size(line)
            x = player_pos_x + title_width // 2 - line_width // 2
            y = player_pos_y + 40 * (i + 1)

            if line.split(":")[0] in ["Bricks", "Weapons", "Crystals"]:
                res = line.split(":")[0].lower()
                image = pygame.image.load(f"assets/{res}.png")
                image = pygame.transform.scale(image,
                                               (line_height, line_height))
                pos = (
                    player_pos_x + title_width // 2 + line_width // 2 + 3, y)
                self.window.blit(image, pos)

            self.window.blit(text, (x, y))

    def draw_players(self):
        gap = 16
        if self.game_status["enemy"]:
            for player in ["player", "enemy"]:
                name = self.game_status[player]["name"]
                state = self.game_status[player]["state"]

                font = pygame.font.SysFont('arial', int(self.font_size * 1.25),
                                           bold=True)
                title_text = f"{name}'s resources"
                title = font.render(title_text, True, (255, 0, 0))
                t_width, t_height = font.size(title_text)

                # current player on the left, enemy on the right:
                x = gap if player == "player" else self.window.get_width() - gap - t_width
                y = gap
                self.window.blit(title, (x, y))
                self.draw_player_stocks(state, (x, y + t_height), t_width)

    def create_card_buttons(self):
        self.card_buttons = []
        gap = (self.window.get_width()//50)
        cards_width = 8 * Client.CARD_WIDTH + 7 * gap
        cards_start_pos = self.window.get_width() // 2 - cards_width // 2

        for i, card in enumerate(self.game_status["hand"]):
            card_name = card["name"]
            can_be_used = card["can_be_used"]
            image_path = f'assets/cards/{card_name}.png'
            pos = (cards_start_pos + i * Client.CARD_WIDTH + i*gap,
                   self.window.get_height() - 300)
            card_button = CardButton(image_path, pos, Client.CARD_SIZE)
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
        self.window.blit(gui.skip_button_image, gui.skip_button_location)

    def handle_mouse_motion(self, mouse_pos):
        for card_button in self.card_buttons:
            if card_button.rect.collidepoint(mouse_pos):
                card_button.highlight()
            else:
                card_button.unhighlight()

    def draw_turn(self):
        text = "Your turn" if self.game_status["turn"] \
            else f"{self.game_status['enemy']['name']}'s turn"

        turn = self.font.render(text, True, self.text_color)

        text_width, text_height = self.font.size(text)
        text_location = (self.window.get_width() // 2 - text_width // 2,
                         self.window.get_height() - 60)

        self.window.blit(turn, text_location)

    def draw_all(self):
        self.draw_card_buttons()
        self.draw_players()
        self.draw_castles()
        self.draw_skip_button()
        self.draw_last_used_card()
        self.draw_turn()
        pygame.display.update()

    def draw_ready_players(self, dots) -> None:
        text = self.game_status["ready"]
        font = pygame.font.SysFont('arial', 80, bold=True)
        turn = font.render(text, True, self.text_color)

        text_width, text_height = font.size(text)
        text_location = (self.window.get_width() // 2 - text_width // 2,
                         self.window.get_height() // 2 - text_height // 2)

        dots_text = font.render("." * dots, True, self.text_color)

        self.window.blit(turn, text_location)
        dots_location = (self.window.get_width() // 2 + text_width // 2,
                         self.window.get_height() // 2 - text_height // 2)
        self.window.blit(dots_text, dots_location)

    def draw_who_win(self) -> None:
        text_location = (self.window.get_width() // 2 - 100,
                         self.window.get_height() - 90)

        text = (f"The game has ended, the player "
                f"{self.game_status['win']} has won!")
        win = self.font.render(text, True, self.text_color)
        self.window.blit(win, text_location)

    def draw_last_used_card(self):
        card = self.game_status["last_used"]
        if card:
            card_name = card["name"]
            image = pygame.image.load(f"assets/cards/{card_name}.png")
            image = pygame.transform.scale(image, Client.CARD_SIZE)

            self.window.blit(image,
                             (self.window.get_width() // 2 - Client.CARD_WIDTH // 2, 100))

            if card["action"] == "replace":
                font = pygame.font.SysFont('arial', 28, bold=True)
                discard_text = font.render("DISCARD", True, (255, 0, 0))
                discard_text.set_alpha(127)
                width = font.size("DISCARD")[0]
                pos = (self.window.get_width() // 2 - width // 2,
                       100 + Client.CARD_HEIGHT // 2)
                self.window.blit(discard_text, pos)

    def draw_castles(self):
        scale = self.window.get_height() // 3
        loc_y = (self.window.get_height() * 6) // 10

        player_state = self.game_status["player"]["state"]
        enemy_state = self.game_status["enemy"]["state"]
        player_height = max(1, player_state["castle"] / 100 * scale)
        enemy_height = max(1, (enemy_state["castle"] / 100) * scale)

        castle_img_path = "assets/castle.png"
        castle = pygame.image.load(castle_img_path)
        width = 150

        player_castle = pygame.transform.scale(castle, (width, player_height))
        enemy_castle = pygame.transform.scale(castle, (width, enemy_height))
        d = 80
        self.window.blit(player_castle,
                         (self.window.get_width() // 2 - (width + d),
                          loc_y - player_height))
        self.window.blit(enemy_castle,
                         (self.window.get_width() // 2 + d,
                          loc_y - enemy_height))

        side = width // 10
        fence_img = pygame.image.load("assets/fence.jpg")
        img = pygame.transform.scale(fence_img, (side, side))

        pl_fence_h = int((player_state["fence"] / 100) * scale)
        en_fence_h = int((enemy_state["fence"] / 100) * scale)

        for fence_h,  x_pos in [(pl_fence_h, self.window.get_width()//2 - d + side),
                                (en_fence_h, self.window.get_width()//2 + d - 2*side)]:
            squares = fence_h // side
            for i in range(1, squares+1):
                self.window.blit(img, (x_pos, loc_y - i*side))
            remainder = fence_h % side
            if remainder > 0:
                cropped = img.subsurface((0, side-remainder, side, remainder))
                y = loc_y - (squares+1)*side + side-remainder
                self.window.blit(cropped, (x_pos, y))

    def get_click(self, mouse_pos):  # todo: nooby method to change (button to replace)
        mouse_x, mouse_y = mouse_pos

        button_width, button_height = gui.button_size

        button_x, button_y = gui.skip_button_location

        if (button_x <= mouse_x <= button_x + button_width and
                button_y <= mouse_y <= button_y + button_height):
            return "skip"

        return None

    def start(self, ip='localhost', port=5556):
        """Initialize gui and connection to the server, and run the game.
        """
        icon = pygame.image.load("assets/castle.png")
        icon = pygame.transform.scale(icon, (32, 32))

        pygame.display.set_icon(icon)
        pygame.display.set_caption(gui.title)
        pygame.font.init()
        self.font = pygame.font.SysFont('arial', self.font_size, bold=True)

        self.start_button = gui.OptionBox(self.window.get_width() // 2 - 100,
                                          50, 200, 40,
                                          (150, 150, 150), (100, 200, 255),
                                          self.font,
                                          ["Ready?", "Start", "Wait"])

        client = Network(ip, port)
        client.connect()
        self.main_loop(client)
        client.close()

    def main_loop(self, client) -> None:

        action = ["get"]

        clock = pygame.time.Clock()
        client.send("name " + self.name)
        t0 = time.time()
        dummy_timer = 0
        while True:
            # clock.tick(gui.fps)

            client.send(action[0])
            action[0] = "get"

            self.game_status = client.receive_data()
            game_status = self.game_status
            event_list = pygame.event.get()

            for event in event_list:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type in [pygame.WINDOWRESIZED,
                                    pygame.WINDOWSIZECHANGED]:
                    w, h = event.x, event.y
                    self.background = pygame.transform.scale(self.bg_image,
                                                             (w, h))
                elif event.type == pygame.MOUSEBUTTONUP:
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

            self.window.blit(self.background, (0, 0))

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
