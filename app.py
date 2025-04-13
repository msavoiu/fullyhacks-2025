import cv2
import mediapipe as mp
import time
import os
import tkinter as tk
from tkinter import *
from tkinter import ttk, font as tkfont
from PIL import Image, ImageTk  # For converting OpenCV frame to Tkinter-compatible format
from tkinter import PhotoImage

from api import cerebrasRequest

# Functions for overlay

def show_overlay():
    overlay.deiconify()
    overlay.lift()

def hide_overlay():
    overlay.withdraw()
    overlay.lower()

def toggle_overlay():
    if overlay.state() == 'normal':
        hide_overlay()
    else:
        show_overlay()

desired_width = 621
desired_height = 431

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Capture video
cap = cv2.VideoCapture(0)  # Use 0 for default webcam

# Initial calibration
initial_shoulder_level = None
initial_head_position = None
initial_head_shoulder_distance = None
initial_eye_distance = None

# Track these to figure out when we should send a request to Cerebras
bad_posture = False
head_bad = False
shoulders_bad = False
face_bad = False
head_drop = 0
shoulder_hunch = 0
face_closeness = 0
mission_control_response = ""

# Popup flag
flag = False
posture_flag = False

# count how many times we encounter a type of bad posture
head_drop_count = 0
too_close_count = 0
shrug_count = 0

# function to calculate distance between two points
def calculate_distance(point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2) ** 0.5

countdown_start_time = time.time()
countdown_duration = 5

posture_start_time = None
posture_start_time2 = None
posture_start_time3 = None
count = 1
count2 = 1
count3 = 1

isCalibrated = 0

# Tkinter setup
root = Tk()
root.configure(bg="#1b063d")
root.title("Posture Corrector")

style = ttk.Style()
style.theme_create("space", parent="alt", settings={
    "TLabel": {"configure": {"background": "#0B1B3A", "foreground": "#B0C4DE", "font": ("Comic Sans", 12)}},
    "TFrame": {"configure": {"background": "#0B1B3A"}},
})
style.theme_use("space")

# Load logo
try:
    image_path = os.path.join(os.path.dirname(__file__), 'assets', 'slayce_logo.png')
    original_img = Image.open(image_path)
    resized_img = original_img.resize((100, 100))
    logo = ImageTk.PhotoImage(resized_img)
except Exception as e:
    print("Error loading or resizing logo image:", e)
    logo = None

# Load background
try:
    bg_path = os.path.join(os.path.dirname(__file__), 'assets', 'test3.png')
    bg_img = Image.open(bg_path).resize((1000, 700)) 
    background = ImageTk.PhotoImage(bg_img)
except Exception as e:
    print("Error loading or resizing background image:", e)
    background = None

# Load custom font or fallback
try:
    font_path = os.path.join(os.path.dirname(__file__), 'assets', 'space_font_serif.ttf')
    
    if os.path.exists(font_path):
        print("Custom font file found, attempting to use it.")
        space_font = tkfont.Font(family="Space Grotesk Light", size=18)
    else:
        raise FileNotFoundError("Font file not found.")

except Exception as e:
    print("Error: Could not load custom font. Using Arial.", e)
    space_font = tkfont.Font(family="Arial", size=18)

# Main frame setup
mainframe = ttk.Frame(root)
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe['padding'] = 0

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
mainframe.columnconfigure(0, weight=1)

# --- Set background ---
if background:
    bg_label = Label(mainframe, image=background)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    bg_label.lower()
    bg_label = Label(mainframe, image=background)

# Video label
video_label = Label(mainframe, width=desired_width, height=desired_height)
video_label.grid(column=0, row=0, sticky="N")

# Logo label
label = Label(mainframe, image=logo, font=space_font)
label.image = logo
label.grid(column=0, row=1, sticky="NE", pady=(100, 20), padx=(100, 0))

# Posture status label (uses space font)
posture_label = Label(mainframe, text="", font=space_font, bg = "white", fg="red")
posture_label.grid(column=0, row=1, sticky="NW", pady=(85, 10), padx=(50, 0))

title_label = Label(mainframe, text="Fully Hacks 2025", font=space_font, bg="white", fg="black")
title_label.grid(row=1, column=0, columnspan=3, pady=(20, 10), padx=0, sticky="n")

moving_logo = Label(root, image=logo, bg="#0B1B3A")
moving_logo.image = logo 
moving_logo.place(x=-100, y=50)  

def animate_logo(x=0):
    if x <= root.winfo_width():
        moving_logo.place(x=x, y=50)
        root.after(10, animate_logo, x+30) 
    else:
        moving_logo.place_forget()

def show_popup(message):
    popup = tk.Toplevel()
    popup.title("Alert from Mission Control!")
    popup.geometry("300x120")
    popup.configure(bg="#1b063d")

    label = tk.Label(popup, text=message, fg="white", bg="#1b063d", wraplength=280, font=("Arial", 11))
    label.pack(pady=10, padx=10)

    def on_close():
        global flag, posture_flag
        flag = False  # Reset the flag when the popup is closed
        popup.destroy()

    popup.protocol("WM_DELETE_WINDOW", on_close)

def process_frame():
    global initial_head_position, initial_head_shoulder_distance, initial_eye_distance, countdown_start_time, countdown_duration, bad_posture, head_bad, shoulders_bad, face_bad, head_drop, shoulder_hunch, face_closeness, head_drop_count, shrug_count, too_close_count, count, count2, count3, posture_start_time, posture_start_time2, posture_start_time3, isCalibrated, mission_control_response, flag, posture_flag

    ret, frame = cap.read()
    if not ret:
        return

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb)

    posture_warning = ""

    if result.pose_landmarks:
        left_shoulder = result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        head = result.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
        left_eye = result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_EAR]
        right_eye = result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EAR]

         # Convert landmark positions to pixel values
        left_shoulder_pos = (left_shoulder.x * frame.shape[1], left_shoulder.y * frame.shape[0])
        # right_shoulder_pos = (right_shoulder.x * frame.shape[1], right_shoulder.y * frame.shape[0])
        head_pos = (head.x * frame.shape[1], head.y * frame.shape[0])
        left_eye_pos = (left_eye.x * frame.shape[1], left_eye.y * frame.shape[0])
        right_eye_pos = (right_eye.x * frame.shape[1], right_eye.y * frame.shape[0])

        current_eye_distance = calculate_distance(left_eye_pos, right_eye_pos)

        current_head_position = head_pos[1]
        current_shoulder_level = left_shoulder_pos[1]
        current_head_shoulder_distance = abs(current_head_position - current_shoulder_level)

        #CHANGE
        if isCalibrated >= 1:
                    reset_label.place(relx=1.0, rely=1.0, anchor='se', x=-130, y=-70)


        time_elapsed = time.time() - countdown_start_time
        # if current_head_shoulder_distance is None or initial_head_position is None or initial_eye_distance is None:
        if initial_head_shoulder_distance is None or initial_head_position is None or initial_eye_distance is None:
            if time_elapsed < countdown_duration:
                posture_label.config(
                    text=f"Calibrating...Sit up straight\n({int(countdown_duration - time_elapsed)}s)", fg="black",font=space_font)
            else:
                initial_head_shoulder_distance = current_head_shoulder_distance
                initial_head_position = current_head_position
                initial_eye_distance = current_eye_distance
                posture_label.config(text="Calibration complete.\n Maintain good posture!", fg="green", font=space_font)
                root.update()
                animate_logo()
                # time.sleep(1.5)
                isCalibrated += 1
        else:
            if current_head_shoulder_distance < initial_head_shoulder_distance - 30:
                if count == 1:
                    posture_start_time = time.time()
                    count += 1
                else:
                    posture_time_elapsed = time.time() - posture_start_time
                    if posture_time_elapsed >= 4:
                        bad_posture = True
                        shoulder_hunch = current_head_shoulder_distance
                        shrug_count += 1
                        posture_warning += "Shoulders too high. "
            else:
                count = 1
                posture_start_time = None

            if current_head_position > initial_head_position + 30:
                if count2 == 1:
                    posture_start_time2 = time.time()
                    count2 += 1
                else:
                    posture_time_elapsed2 = time.time() - posture_start_time2
                    if posture_time_elapsed2 >= 4:
                        bad_posture = True
                        head_drop = current_head_position - initial_head_position
                        head_drop_count += 1
                        posture_warning += "\nHead dropped."
            else:
                count2 = 1
                posture_start_time2 = None

            if current_eye_distance > initial_eye_distance + 100:
                if count3 == 1:
                    posture_start_time3 = time.time()
                    count3 += 1
                else:
                    posture_time_elapsed3 = time.time() - posture_start_time3
                    if posture_time_elapsed3 >= 4:
                        bad_posture = True
                        face_closeness = current_eye_distance - initial_eye_distance
                        head_drop_count += 1
                        posture_warning += "Head too close."
            else:
                count3 = 1
                posture_start_time3 = None

            if bad_posture:
                if not posture_flag:
                    mission_control_response = cerebrasRequest(head_bad, shoulders_bad, face_bad, head_drop, shoulder_hunch, face_closeness)
                    posture_flag = True
            else:
                posture_flag = False

            if posture_warning:
                posture_label.config(text=posture_warning, fg="red",font=space_font)
            else:
                posture_label.config(text="Posture looks good!", fg="green",font=space_font)

        print("flag:", flag, "\nposture_flag:", posture_flag)
        if not flag and mission_control_response:
            show_popup(mission_control_response)
            flag = True
            mission_control_response = ""

        # Draw pose landmarks
        mp.solutions.drawing_utils.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Convert frame to image for Tkinter
    frame = cv2.resize(frame, (desired_width, desired_height))
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    imgtk = ImageTk.PhotoImage(image=img)

    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

    root.after(10, process_frame)
# Start video processing loop
process_frame()

# Clean exit on close
def on_closing():
    cap.release()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.geometry("1000x700")

# Overlay setup
overlay = Toplevel(root)
overlay.geometry("100x100")
overlay.overrideredirect(True)
overlay.configure(bg="#0B1B3A")
label = Label(overlay, text="Testing overlay...", bg="#0B1B3A", fg="white")

# Toggle overlay
def on_root_state_change(event):
    state = root.state()
    if state == 'iconic':  # Minimized
        show_overlay()
    elif state == 'normal':  # Restored
        hide_overlay()

root.bind('<Unmap>', on_root_state_change)
root.bind('<Map>', on_root_state_change)

ship_image = Image.open("assets/ship.png")  # Ensure the path is correct

# Resize the image to a desired size (e.g., 50x50)
ship_image = ship_image.resize((100, 100))  # Adjust width and height as needed

# Convert the image to a Tkinter-compatible format
ship_image = ImageTk.PhotoImage(ship_image)

def reset():
    globals().__setitem__('initial_shoulder_level', None)
    globals().__setitem__('initial_head_position', None)
    globals().__setitem__('initial_head_shoulder_distance', None)
    globals().__setitem__('initial_eye_distance', None)
    globals().__setitem__('countdown_start_time', time.time())
    reset_label.place_forget()

reset_label = Label(
    root,
    image=ship_image,
    bg="#1b063d",  # Set background to match window color
    bd=0  # Remove label border
)

reset_label.bind("<Button-1>", lambda event: reset())

# Run the app
root.mainloop()