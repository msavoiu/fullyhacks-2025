from tkinter import *
from tkinter import ttk
from tkinter import font as tkfont
from PIL import Image, ImageTk
import os

# Create the main application window
root = Tk()
root.title("Posture Corrector")  # Set window title
style = ttk.Style()

style.theme_create("space", parent="alt", settings={
    "TLabel": {"configure": {"background": "#0B1B3A", "foreground": "#B0C4DE", "font": ("Comic Sans", 12)}},
    "TFrame": {"configure": {"background": "#0B1B3A"}},
})
style.theme_use("space")


try:
    image_path = os.path.join(os.path.dirname(__file__), 'assets', 'slayce_logo.png')
    original_img = Image.open(image_path)
    resized_img = original_img.resize((150, 150))  # Resize to 150x150
    logo = ImageTk.PhotoImage(resized_img)
except Exception as e:
    print("Error loading or resizing image:", e)
    logo = None


# Trying to use the space_font_serif font. If it fails, then fallback on Arial.
try:
    import os

    font_path = os.path.join(os.path.dirname(__file__), 'assets', 'space_font_serif.ttf')
    space_font = tkfont.Font(family="Space Grotesk Light", size=24)

except Exception as e:
    print("Error: Could not load custom font. Using Arial.", e)
    space_font = tkfont.Font(family="Arial", size=24)

# Create a main frame with padding inside the root window
mainframe = ttk.Frame(root)
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))  # Attach frame to the window

# Allow the frame to expand with window resizing
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

label = Label(mainframe, text='test', image=logo, font=space_font)
label.image = logo
label.grid(column=0, row=0, sticky=W)

mainframe['padding'] = (50) # 50 on each side

root.geometry("1000x600")

# Start the main event loop
root.mainloop()