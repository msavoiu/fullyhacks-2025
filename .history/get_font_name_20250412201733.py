from fontTools.ttLib import TTFont
import os

# Path to the font file
font_path = os.path.join(os.path.dirname(__file__), 'assets', 'space_font_serif.ttf')
font = TTFont(font_path)

# Try to get full name (nameID 4), fallback to font family (nameID 1)
internal_name = None

# Try nameID 4 (Full font name)
for record in font['name'].names:
    if record.nameID == 4:
        internal_name = record.toStr()
        break

# Fallback to nameID 1 (Font family)
if not internal_name:
    for record in font['name'].names:
        if record.nameID == 1:
            internal_name = record.toStr()
            break

print("✅ Internal font name:", internal_name)