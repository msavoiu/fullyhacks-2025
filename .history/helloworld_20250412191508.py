from tkinter import *
from tkinter import ttk

# Conversion function: Converts feet to meters (commented out for now)
'''
def calculate(*args):
    try:
        value = float(feet.get())  # Get the value entered by the user
        meters.set(int(0.3048 * value * 10000.0 + 0.5)/10000.0)  # Convert to meters and round to 4 decimal places
    except ValueError:
        pass  # Ignore input errors
'''

# Create the main application window
root = Tk()
root.title("Posture Corrector")  # Set window title

# Create a main frame with padding inside the root window
mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))  # Attach frame to the window

# Allow the frame to expand with window resizing
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)


# Start the main event loop
root.mainloop()