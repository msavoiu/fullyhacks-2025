from tkinter import *
from tkinter import ttk

# Create the main application window
root = Tk()
root.title("Posture Corrector")  # Set window title

# Create a main frame with padding inside the root window
mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))  # Attach frame to the window

# Allow the frame to expand with window resizing
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

label = ttk.Label(mainframe, text='Full name:')
label.grid(column=0, row=0, sticky=W)



# Start the main event loop
root.mainloop()