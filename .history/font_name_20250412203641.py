from fontTools.ttLib import TTFont
import os

font_path = os.path.join(os.path.dirname(__file__), 'assets', 'space_font_serif.ttf')
font = TTFont(font_path)

print("---- FONT INFO ----")
for record in font['name'].names:
    if record.nameID == 1:
        print("Font family name:", record.toStr())
    if record.nameID == 4:
        print("Full font name:", record.toStr())