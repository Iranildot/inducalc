import customtkinter as ctk
from PIL import Image
import os

def convert_color(color:str|list|tuple, output:str="RGB") -> str|tuple:

    variable_type = type(color)

    # TO RGB
    if output.upper() == "RGB" and variable_type == str:
        
        hex_color = color.lstrip("#").upper()
        
        if len(hex_color) == 3:
            color = (int(hex_color[0] * 2, 16), int(hex_color[1] * 2, 16), int(hex_color[2] * 2, 16))
        else:
            color = (int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))
        
        return tuple(color)
    
    # TO HEXADECIMAL
    elif output.upper() == "HEX" and (variable_type == list or variable_type == tuple):

        red, green, blue = color
        
        return "#{:02X}{:02X}{:02X}".format(red, green, blue)
    
    
    return color

def list_icons(directory):

    # LIST ALL OF THE ICONS
    files = os.listdir(directory)
    
    # FILTER TO KEEP ONLY FILES
    file_paths = [os.path.join(directory, file) for file in files if os.path.isfile(os.path.join(directory, file))]
    
    return file_paths

def change_icons_color(color:str, *paths:str):

    def change_color(icon):
        # OPEN IMAGE WITH TRANSPARENCY
        image = Image.open(icon).convert("RGBA")

        # GET IMAGE'S DATA
        data = image.getdata()

        # CREATE A NEW LIST OF DATA
        new_data = []
        for item in data:
            # GETTING ALPHA VALUE (a)
            a = item[3]

            # NOT TRANSPARENT
            if a > 0:
                new_data.append((color[0], color[1], color[2], a))
            
            # TRANSPARENT
            else:
                new_data.append(item)

        # UPDATE IMAGE WITH NEW DATA
        image.putdata(new_data)

        # SAVE MODIFIED IMAGE
        image.save(icon, format="PNG")

    color = convert_color(color)

    for element in paths:

        if os.path.isdir(element):

            icons = list_icons(element)

            for icon in icons:
                change_color(icon=icon)
        
        elif os.path.isfile(element):
            change_color(element)

# OPENING THE LOGO
change_icons_color("#333333", "logo_dark.png")  # TO DARK MODE
change_icons_color("#DDDDDD", "logo_light.png") # TO LIGHT MODE

logo = ctk.CTkImage(
    light_image=Image.open("./assets/icons/logo_light.png"),
    dark_image=Image.open("./assets/icons/logo_dark.png"),
    size=(45, 40)
)

# THEME CHOOSER ICONS
change_icons_color("#333333", "./assets/icons/dark_mode.png") # TO DARK MODE
change_icons_color("#DDDDDD", "./assets/icons/light_mode.png") # TO LIGHT MODE

theme_icon = ctk.CTkImage(
    light_image=Image.open("./assets/icons/light_mode.png"),
    dark_image=Image.open("./assets/icons/dark_mode.png"),
    size=(25, 25)
)

# THEME CHOOSER ICON (SYSTEM)
change_icons_color("#333333", "./assets/icons/sync_dark.png") # TO DARK MODE
change_icons_color("#DDDDDD", "./assets/icons/sync_light.png") # TO LIGHT MODE

theme_icon_system = ctk.CTkImage(
    light_image=Image.open("./assets/icons/sync_light.png"),
    dark_image=Image.open("./assets/icons/sync_dark.png"),
    size=(25, 25)
)

# CREATE ICON
change_icons_color("#DDDDDD", "./assets/icons/create_dark.png") # TO DARK MODE
change_icons_color("#333333", "./assets/icons/create_light.png") # TO LIGHT MODE

create_icon = ctk.CTkImage(
    light_image=Image.open("./assets/icons/create_light.png"),
    dark_image=Image.open("./assets/icons/create_dark.png"),
    size=(25, 25)
)

# TECH FILE
change_icons_color("#DDDDDD", "./assets/icons/tech_file_dark.png") # TO DARK MODE
change_icons_color("#333333", "./assets/icons/tech_file_light.png") # TO LIGHT MODE

tech_file_icon = ctk.CTkImage(
    light_image=Image.open("./assets/icons/tech_file_light.png"),
    dark_image=Image.open("./assets/icons/tech_file_dark.png"),
    size=(25, 25)
)

# ADD
change_icons_color("#333333", "./assets/icons/add_dark.png") # TO DARK MODE
change_icons_color("#DDDDDD", "./assets/icons/add_light.png") # TO LIGHT MODE

add_icon = ctk.CTkImage(
    light_image=Image.open("./assets/icons/add_light.png"),
    dark_image=Image.open("./assets/icons/add_dark.png"),
    size=(25, 25)
)