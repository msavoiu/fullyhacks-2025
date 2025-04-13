from tkinter import *
from tkinter import ttk

# Create the main application window
root = Tk()
root.title("Posture Corrector")  # Set window title
style = ttk.Style()

style.theme_create("space", parent="alt", settings={
    "TLabel": {"configure": {"background": "#0B1B3A", "foreground": "#B0C4DE", "font": ("Comic Sans", 12)}},
    "TFrame": {"configure": {"background": "#0B1B3A"}},
})
style.theme_use("space")

# Create a main frame with padding inside the root window
mainframe = ttk.Frame(root)
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))  # Attach frame to the window

# Allow the frame to expand with window resizing
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

label = ttk.Label(mainframe, text='test')
label.grid(column=0, row=0, sticky=W)

mainframe['padding'] = (50) # left: 100, top: 100, right: 100, bottom: 100


# Start the main event loop
root.mainloop()


