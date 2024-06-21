import PIL
from PIL import Image, ImageDraw, ImageFont
import json


def save_card_image(card):
    width, height = 140, 190
    background_color = (255, 229, 204)

    image = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(image)

    border_color = (153, 76, 0)  # Czarny
    border_thickness = 4
    draw.rectangle([(border_thickness//2, border_thickness//2),
                    (width - border_thickness//2, height - border_thickness//2)],
                   outline=border_color, width=border_thickness)

    card_name = "\n".join(card["name"].split(" "))
    file_name = card["name"]
    card_desc = card["desc"]

    # font_name = ImageFont.load_default(20)
    # font_desc = ImageFont.load_default(20)
    font_desc = ImageFont.truetype("arial.ttf", 20)
    font_name = ImageFont.truetype("OpenSans-Bold.ttf", 20)

    text_color = (0, 0, 0)

    name_bbox = draw.textbbox((0, 0), card_name, font=font_name)
    name_width = name_bbox[2] - name_bbox[0]
    name_x = (width - name_width) // 2
    name_y = 40  # Odległość od góry
    draw.text((name_x, name_y), card_name, font=font_name, fill=(255, 0, 0))

    lines = card_desc.split('\n')

    total_text_height = sum([draw.textbbox((0, 0), line, font=font_desc)[3]
                             - draw.textbbox((0, 0), line, font=font_desc)[1]
                             for line in lines])

    desc_y = (height + name_y + name_bbox[3] + border_thickness) // 2
    current_y = desc_y - total_text_height // 2

    for line in lines:
        line_bbox = draw.textbbox((0, 0), line, font=font_desc)
        line_width = line_bbox[2] - line_bbox[0]
        line_x = (width - line_width) // 2
        draw.text((line_x, current_y), line, font=font_desc, fill=text_color)
        current_y += line_bbox[3] - line_bbox[1] + 8

    if card["cost"]:
        stock = next(iter(card["cost"]))
        value = abs(card["cost"][stock])

        small_image_path = f'assets/{stock}.png'

        small_image = Image.open(small_image_path).convert("RGBA")
        small_image = small_image.resize((20, 20),
                                         PIL.Image.LANCZOS)
        image.paste(small_image, (border_thickness * 3, border_thickness * 3),
                    small_image)

        stock_bbox = draw.textbbox((border_thickness*4, border_thickness*4), str(value), font=font_name)
        stock_width = stock_bbox[2] - stock_bbox[0]
        stock_x = border_thickness*4 + 17
        stock_y = border_thickness*2
        draw.text((stock_x, stock_y), str(value), font=font_name,
                  fill=(0, 0, 0),  stroke_fill=(0, 0, 0))

    image.save(f'assets/{file_name}.png')


with open("game/cards.jsonl", 'r') as file:
    for line in file:
        card = json.loads(line)
        save_card_image(card)

