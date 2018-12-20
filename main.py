from PIL import PngImagePlugin
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageEnhance
import os


def create_image(team_number, card, team_pics_path, out_path, padding_left, padding_top, width):
    try:
        team_path = "{}/{}.JPG".format(team_pics_path, team_number)
        print(team_path)
        team_pic = Image.open(team_path)
        team_pic = team_pic.convert("RGBA")
    except:
        print("\033[0;31m TEAM PIC ERROR FOR TEAM NUMEBR: {} RETURNING \033[0m".format(team_number))
        return
    w1, h1 = team_pic.size
    team_pic.thumbnail((width, int(width * h1 / w1)), Image.ANTIALIAS)
    contrast = ImageEnhance.Contrast(team_pic)
    team_pic = contrast.enhance(1.15)
    team_pic.paste(card, (int(team_pic.size[0] * padding_left), int(team_pic.size[1] * padding_top)), card.convert("RGBA"))
    team_pic.save("{}/{}".format(out_path, team_number), "PNG")


def init_card(width, height, brand):
    card = Image.new('RGBA', (width, height))
    brand.thumbnail((width, int(brand.size[1] * width / brand.size[0])), Image.ANTIALIAS)
    card.paste(brand, (0, 0), brand.convert("RGBA"))
    return card, brand.size[1]


def png_safe():
    Image.MAX_IMAGE_PIKELS = None
    PngImagePlugin.MAX_TEXT_CHUNK = 1000000000000


def uni_logo_to_card(team_number, csv, card, team_info_top, uni_logos_path, uni_logo_height, padding=0.1):
    try:
        uni_logo = Image.open("{}/{}".format(uni_logos_path, csv[team_number][csv[0].index("uni")]))
    except:
        print("\033[0;31m UNI LOGO ERROR FOR TEAM NUMEBR: {} RETURNING \033[0m".format(team_number))
        return
    uni_logo.thumbnail((int(uni_logo_height), int(uni_logo_height)), Image.ANTIALIAS)
    card.paste(uni_logo, (int((card.size[0] - uni_logo.size[0]) / 2), int(team_info_top + 10)), uni_logo.convert("RGBA"))
    card.save("temp", "PNG")
    return card, int(team_info_top + uni_logo.size[1] * 1.02) + 20


def csv_loader(path_to_csv):
    csv = {}
    read = open(path_to_csv, "r")
    arr = [line.rstrip() for line in read]
    for i in range(len(arr)):
        csv[i] = [x.strip('"') for x in arr[i].split(',')]
    return csv


def text_wrap(text, font, max_width):
    lines = []
    # If the width of the text is smaller than image width
    # we don't need to split it, just add it to the lines array
    # and return
    if font.getsize(text)[0] <= max_width:
        lines.append(text)
    else:
        # split the line by spaces to get words
        words = text.split(' ')
        i = 0
        # append every word to a line while its width is shorter than image width
        while i < len(words):
            line = ''
            while i < len(words) and font.getsize(line + words[i])[0] <= max_width:
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            # when the line gets longer than the max width do not append the word, add the line to the lines array
            lines.append(line)
    return lines


def write_text_and_wrap(source_image, text, x, y,max_width, font_size=50, font_file_path="./Fonts/Arial.ttf", fill=(0, 0, 0)):
    # size() returns a tuple of (width, height)
    image_size = source_image.size

    # create the ImageFont instance
    font = ImageFont.truetype( font_file_path, size=font_size, encoding="unic")

    # get shorter lines
    lines = text_wrap(text, font=font, max_width=max_width)
    line_height = font.getsize('hg')[1]

    drawable_object = ImageDraw.Draw(source_image)

    for line in lines:
        # draw the line on the image
        drawable_object.text((x, y), line, fill=fill, font=font)
        # update the y position so that we can use it for next line
        y = y + line_height


def shrink_font_to_fit( text, font_file_path, prefered_font_size, max_width ):
    font_size = 1

    font = ImageFont.truetype(font_file_path, font_size)
    while font.getsize(text)[0] < max_width and font_size <= prefered_font_size:
        font_size += 1
        font = ImageFont.truetype(font_file_path, font_size)

    #  de-increment to be sure it is less than criteria
    return font


def write_text_and_shrink(source_image, text, x, y,max_width, font_size=50,font_file_path = "./Fonts/Arial.ttf", fill=(0, 0, 0)):
    # create the ImageFont instance
    font = shrink_font_to_fit(text=text, font_file_path=font_file_path, prefered_font_size=font_size, max_width=max_width)

    drawable_object = ImageDraw.Draw(source_image)
    drawable_object.text((x, y), text, fill=fill, font=font)


def write_university_title( basePicture , title, padding_percentage = 0.05, vertical_parts=3):
    x = basePicture.width * padding_percentage
    y = 0
    write_text_and_shrink(basePicture,x=x, y=y, text=title, max_width=int(basePicture.width * (1 - 2 * padding_percentage)), font_size=30,fill=(255,255,255))


def write_student_names( basePicture , names , padding_percentage = 0.06,vertical_parts=3):
    x = basePicture.width * padding_percentage
    for (shit,name) in enumerate(names):
        y = int(basePicture.height * shit/vertical_parts)
        write_text_and_shrink(basePicture, x=x, y=y, text=str(name).upper(), max_width=int(basePicture.width * (1 - 2 * padding_percentage)), font_size=20,fill=(255,255,255))


def write_names( csv , team_number, card , top):
    h = 90
    raw_image = Image.new('RGBA', (card.width, h), (255, 255, 255, 0))
    names = [csv[team_number][csv[0].index("Contestant 1")], csv[team_number][csv[0].index("Contestant 2")] , csv[team_number][csv[0].index("Contestant 3")]]
    write_student_names(raw_image, names)
    card.paste( raw_image, (0, top), raw_image.convert("RGBA"))
    return (card,top + h)


def write_title( csv, team_number, card, top):
    h = 60
    raw_image = Image.new('RGBA', (card.width, 30), (255, 255, 255, 0))
    write_university_title(raw_image, csv[team_number][csv[0].index("Institution")])
    card.paste(raw_image, (0, top), raw_image.convert("RGBA"))
    return card,top+h


png_safe()
csv = csv_loader("teams.csv")
brand = Image.open("brand")
width = 1366
height = int(3 / 5 * width)


for i in range(1, 100):
    try:
        card, top = init_card(int(width * 0.25), int(height * 1), brand)
        card, top = uni_logo_to_card(i, csv, card, top, "new_logos", 80)
        card, top = write_title(csv, i, card, top)
        card, top = write_names(csv, i, card, top)
        create_image(i, card, "./teams", "out", 0.03, 0.1, width)
    except Exception as e:
        print("team {} failed".format(i), e.__cause__)

