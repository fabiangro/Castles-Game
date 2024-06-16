# from game import Deck
import pygame


class OptionBox:
    def __init__(self, x, y, w, h, color, highlight_color, font, option_list, selected=0):
        self.color = color
        self.highlight_color = highlight_color
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.option_list = option_list
        self.selected = selected
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf):
        pygame.draw.rect(surf, self.highlight_color if self.menu_active else self.color, self.rect)
        pygame.draw.rect(surf, (0, 0, 0), self.rect, 2)
        try:
            msg = self.font.render(self.option_list[self.selected], 1, (0, 0, 0)) # buguje
        except:
            msg = self.font.render("BUG TO REPAIR", 1, (0, 0, 0))

        surf.blit(msg, msg.get_rect(center=self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.option_list):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                pygame.draw.rect(surf, self.highlight_color if i == self.active_option else self.color, rect)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center=rect.center))
            outer_rect = (
            self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.rect.height * len(self.option_list))
            pygame.draw.rect(surf, (0, 0, 0), outer_rect, 2)

    def update_display(self, option_list):
        self.option_list = option_list
        self.selected = 0

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)

        self.active_option = -1
        for i in range(len(self.option_list)):
            rect = self.rect.copy()
            rect.y += (i + 1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.selected = self.active_option
                    self.draw_menu = False
                    return self.option_list[self.active_option]
        return -1

title = "Bluff Game"
width, height = 1288, 812
fps = 60

card_size = (100, 140)
free_space = 30
player_cards_y = height - card_size[1] - 45

button_size = (150, 60)
button_check_location = free_space, height - button_size[1] - free_space
button_check_location2 = width - button_size[0] - free_space * 2, height - button_size[1] - free_space

font_size = 45

background_image = pygame.image.load('assets/background3.jpg')

skip_button_image = pygame.image.load('assets/skip.png')
skip_button_image = pygame.transform.scale(skip_button_image, button_size)

show_button_image = pygame.image.load('assets/show.png')
show_button_image = pygame.transform.scale(show_button_image, button_size)

button_checked_image = pygame.image.load('assets/checked_button.jpg')
button_checked_image = pygame.transform.scale(button_checked_image, button_size)

card_reverse = pygame.image.load('assets/reverse.jpg')
card_reverse = pygame.transform.scale(card_reverse, card_size)

# def create_cards_image_dict():
#     card_images = {}
#     deck = Deck()
#     deck = deck.deck
#
#     for card in deck:
#         card = str(card)
#         path = f"assets/{card}.png"
#         card_images[card] = pygame.image.load(path)
#         card_images[card] = pygame.transform.scale(card_images[card], card_size)
#
#     return card_images
#
#
# cards_images = create_cards_image_dict()



# def hand_to_cards_location(hand): # returns {str(card): (card_image, (x, y))}
#     hand = sorted(hand)
#     num_players = len(hand)
#     cards_locations = {}
#
#     total_width = num_players * (card_size[0] + free_space - 1)
#     start_loc = (width - total_width) // 2
#
#     for card in hand:
#         cards_locations[str(card)] = cards_images[str(card)], (start_loc, player_cards_y)
#         start_loc += free_space + card_size[0]
#
#     return cards_locations


def players_cards(players): # list of players, returns {player_name: (num_cards, (x, y))}
    num_players = len(players)
    players_locations = {}

    total_width = num_players * (card_size[0] + free_space - 1)
    start_loc = (width - total_width) // 2

    for player in players:
        location = start_loc, free_space
        players_locations[player[0]] = player[1], location
        start_loc += free_space * 3 + card_size[0]

    return players_locations


# def get_cards_location(cards):
#     cards = sorted(cards)
#     cards_location = {}
#     num_cards = len(cards)
#     start_loc_y = 0 + card_size[1] + free_space
#     start_loc_x = free_space
#     i = 0
#
#     for card in cards:
#         i += 1
#         card_img = cards_images[str(card)]
#         cards_location[card_img] = start_loc_x, start_loc_y
#         start_loc_x += card_size[0] // 2
#         if i >= 20:
#             start_loc_y += card_size[1] + free_space // 2
#
#     return cards_location

