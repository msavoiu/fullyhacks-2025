from fontTools.ttLib import TTFont
import os

# Path to your .ttf file
font_path = os.path.join(os.path.dirname(__file__), 'assets', 'space_font_serif.ttf')
font = TTFont(font_path)

# Extract the internal name (NameID 4 is the full name)
internal_name = None
for record in font['name'].names:
    if record.nameID == 4 and record.platformID == 1:
        internal_name = record.toStr()
        break

print("✅ Internal font name:", internal_name)