import requests
import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import json
from io import BytesIO
import time

# Paste your Unsplash Access Key in the main function at the bottom of the code
# Paste your font style in the get_quote function at the top of the code

def get_quote():
    # Retrieve quote from API
    response = requests.get("https://stoic-quotes.com/api/quote").json()
    quote, author = response["text"], response["author"]
    max_line_length = 30
    font_size = 200
    font_style = "Set up your own font style here"
    return quote, author, max_line_length, font_size, font_style

def get_photo_url(Access_Key, orientation, Search_Term):
    # API
    url = "https://api.unsplash.com/photos/random"
    params = {
        "query": Search_Term,
        "orientation": orientation,
        "client_id": Access_Key
    }
    response = requests.get(url, params=params)
    photo_data = json.loads(response.text)
    photo_url = photo_data["urls"]["raw"]
    return photo_url

def download_photo(photo_url):
    # Download photo and open with PIL
    photo_response = requests.get(photo_url)
    bg_image = Image.open(BytesIO(photo_response.content))
    return bg_image

def crop_photo(bg_image):
    # Crop photo to square aspect ratio
    width, height = bg_image.size
    if width > height:
        left = (width - height) // 2
        top = 0
        right = left + height
        bottom = height
    else:
        left = 0
        top = (height - width) // 2
        right = width
        bottom = top + width
    bg_image = bg_image.crop((left, top, right, bottom))
    max_quote_height = int(bg_image.height * 0.75)
    return bg_image

def adjust_brightness(bg_image, brightness_factor):
    # Adjust brightness of photo
    enhancer = ImageEnhance.Brightness(bg_image)
    bg_image = enhancer.enhance(brightness_factor)
    return bg_image

def split_quote(quote, max_line_length):
    words = quote.split()
    lines = []
    line = ""
    for word in words:
        if len(line) + len(word) + 1 <= max_line_length:
            line += " " + word if line else word
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def split_long_lines(lines, max_line_length):
    # Split long lines into multiple lines
    new_lines = []
    for i, line in enumerate(lines):
        if len(line) <= max_line_length:
            new_lines.append(line)
        else:
            words = line.split()
            new_line = words[0]
            for word in words[1:]:
                if len(new_line) + len(word) + 1 <= max_line_length:
                    new_line += " " + word
                else:
                    if i + 1 < len(lines):
                        next_word = lines[i+1].split()[0]
                        if len(new_line) + len(next_word) + 1 <= max_line_length:
                            new_line += " " + next_word
                            lines[i+1] = " ".join(lines[i+1].split()[1:])
                        else:
                            spaces_to_add = max_line_length - len(new_line)
                            num_words = len(new_line.split())
                            space_per_word = spaces_to_add // (num_words - 1)
                            remainder_spaces = spaces_to_add % (num_words - 1)
                            spaces_between_words = " " * space_per_word
                            new_line = spaces_between_words.join(new_line.split())
                            new_line += " " * remainder_spaces
                            new_lines.append(new_line)
                            new_line = next_word
                            lines[i+1] = " ".join(lines[i+1].split()[1:])
                    else:
                        spaces_to_add = max_line_length - len(new_line)
                        num_words = len(new_line.split())
                        space_per_word = spaces_to_add // (num_words - 1)
                        remainder_spaces = spaces_to_add % (num_words - 1)
                        spaces_between_words = " " * space_per_word
                        new_line = spaces_between_words.join(new_line.split())
                        new_line += " " * remainder_spaces
                        new_lines.append(new_line)
                        new_line = word
            new_lines.append(new_line)
    return new_lines

def add_text_to_image(bg_image, new_lines, font_style, font_size, author,Author_size) :
    # Add text to image
    draw = ImageDraw.Draw(bg_image)
    font = ImageFont.truetype(font_style, size=font_size)
    text_bbox = draw.textbbox((0, 0), '\n'.join(new_lines), font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    max_text_height = int(bg_image.height * 0.75)

    if text_height > max_text_height:
        font_size = int(font_size * max_text_height / text_height)
        font = ImageFont.truetype(font_style, size=font_size)
        text_bbox = draw.textbbox((0, 0), '\n'.join(new_lines), font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

    text_x = int((bg_image.width - text_width) / 2)
    text_y = int((bg_image.height - text_height) / 4)
    
    # Draw text on image
    draw.multiline_text((text_x, text_y), '\n'.join(new_lines), font=font, align='center')

    #Calculate bounding box for text
    text_bbox = (int((bg_image.width - text_width) / 2), int((bg_image.height - text_height) / 4), int((bg_image.width + text_width) / 2), int((bg_image.height + text_height) * 3 / 4))

    #Draw text on image
    draw.multiline_text(text_bbox[:2], '\n'.join(new_lines), font=font, fill="white", align='center')

    # Add author to image
    author_font = ImageFont.truetype(font_style, size=Author_size)
    author_text = " - " + author
    author_bbox = draw.textbbox((0, 0), author_text, font=author_font)
    author_width = author_bbox[2] - author_bbox[0]
    author_x = (bg_image.width - author_width) / 2
    author_y = int(bg_image.height * 0.875 - author_bbox[3] / 2)  # center of the lower 25% of the image

    draw.text((author_x, author_y), author_text, font=author_font, fill="white")
    
    return bg_image
   
if __name__ == '__main__':
    Access_Key = "Get Access Key from Unsplash"
    orientation = "landscape"
    Search_Term = "mountains"
    brightness_factor = 0.1
    quote, author, max_line_length, font_size, font_style = get_quote()
    photo_url = get_photo_url(Access_Key, orientation, Search_Term)
    bg_image = download_photo(photo_url)
    bg_image = crop_photo(bg_image)
    Untouched = bg_image.copy()
    lines = split_quote(quote, max_line_length)
    new_lines = split_long_lines(lines, max_line_length)
    add_text_to_image(bg_image, new_lines, font_style, font_size, author , Author_size = 200)
    A_size = 200
    bg_image.save("my_quote_image.png")
    Happy = input("Ideal Font Size?: ")
    Happy2 = input("Ideal Quote Size?: ")
    while True:
        if Happy == "yes" and Happy2 == "yes":
            break
        else:
            print("Okay, let's try again!")
            # ask for new font size if it's not already set to desired value
            if Happy != "yes":
                font_size = int(input("Font Size: "))
            # ask for new quote size if it's not already set to desired value
            if Happy2 != "yes":
                A_size = int(input("Author Size: "))
            # create a copy of bg_image before modifying it
            new_bg_image = Untouched.copy()
            add_text_to_image(new_bg_image, new_lines, font_style, font_size, author , Author_size = A_size)
            new_bg_image.save("my_quote_image.png")
            # update Happy and Happy2 with user input, or "yes" if already set to desired value
            Happy = input("Ideal Font Size?: ") if Happy != "yes" else "yes"
            Happy2 = input("Ideal Quote Size?: ") if Happy2 != "yes" else "yes"
            bg_image = new_bg_image
    adjust_brightness(bg_image, brightness_factor)
    bg_image.save("my_quote_image.png")
    print("Done!")