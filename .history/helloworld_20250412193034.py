from tkinter import *
from tkinter import ttk

# Create the main application window
root = Tk()
root.title("Posture Corrector")  # Set window title

# Create a main frame with padding inside the root window
mainframe = ttk.Frame(root)
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))  # Attach frame to the window

# Allow the frame to expand with window resizing
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

label = ttk.Label(mainframe, text='test')
label.grid(column=0, row=0, sticky=W)

mainframe['padding'] = 100           # 5 pixels on all sides
mainframe['padding'] = (5,10)      # 5 on left and right, 10 on top and bottom
mainframe['padding'] = (5,7,10,12) # left: 5, top: 7, right: 10, bottom: 12



# Start the main event loop
root.mainloop()