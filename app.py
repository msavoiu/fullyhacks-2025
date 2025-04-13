import cv2
import mediapipe as mp
import statistics
import time
from tkinter import *
from tkinter import ttk, font as tkfont
from PIL import Image, ImageTk  # For converting OpenCV frame to Tkinter-compatible format

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

# Tkinter setup
root = Tk()
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
    bg_path = os.path.join(os.path.dirname(__file__), 'assets', 'test2.png')
    bg_img = Image.open(bg_path).resize((1000, 700)) 
    background = ImageTk.PhotoImage(bg_img)
except Exception as e:
    print("Error loading or resizing background image:", e)
    background = None

# Load custom font or fallback
try:
    font_path = os.path.join(os.path.dirname(__file__), 'assets', 'space_font_serif.ttf')
    space_font = tkfont.Font(file=font_path, size=24)
except Exception as e:
    print("Error: Could not load custom font. Using Arial.", e)
    space_font = tkfont.Font(family="Arial", size=24)

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

# Video label
video_label = Label(mainframe, width=desired_width, height=desired_height)
video_label.grid(column=0, row=0, sticky="N")

# Logo label
label = Label(mainframe, image=logo, font=space_font)
label.image = logo
label.grid(column=0, row=1, sticky="NE", pady=(100, 20), padx=(100, 0))

# Posture status label (uses space font)
posture_label = Label(mainframe, text="", font=space_font, bg = "white", fg="red")
posture_label.grid(column=0, row=1, sticky="NW", pady=(100, 10), padx=(50, 0))

def process_frame():
    global initial_head_position, initial_head_shoulder_distance, initial_eye_distance, countdown_start_time, countdown_duration, head_drop_count, shrug_count, too_close_count, count, count2, count3, posture_start_time, posture_start_time2, posture_start_time3

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
        right_shoulder_pos = (right_shoulder.x * frame.shape[1], right_shoulder.y * frame.shape[0])
        head_pos = (head.x * frame.shape[1], head.y * frame.shape[0])
        left_eye_pos = (left_eye.x * frame.shape[1], left_eye.y * frame.shape[0])
        right_eye_pos = (right_eye.x * frame.shape[1], right_eye.y * frame.shape[0])

        current_eye_distance = calculate_distance(left_eye_pos, right_eye_pos)

        current_head_position = head_pos[1]
        current_shoulder_level = left_shoulder_pos[1]
        current_head_shoulder_distance = abs(current_head_position - current_shoulder_level)

        time_elapsed = time.time() - countdown_start_time
        if current_head_shoulder_distance is None or initial_head_position is None or initial_eye_distance is None:
            if time_elapsed < countdown_duration:
                posture_label.config(
                    text=f"Calibrating... Sit up straight ({int(countdown_duration - time_elapsed)}s)", fg="yellow",font=space_font)
            else:
                initial_head_shoulder_distance = current_head_shoulder_distance
                initial_head_position = current_head_position
                initial_eye_distance = current_eye_distance
                posture_label.config(text="Calibration complete. Maintain good posture!", fg="green", font=space_font)
        else:
            if current_shoulder_level < initial_head_shoulder_distance - 30:
                if count == 1:
                    posture_start_time = time.time()
                    count += 1
                else:
                    posture_time_elapsed = time.time() - posture_start_time
                    if posture_time_elapsed >= 4:
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
                        head_drop_count += 1
                        posture_warning += "Head dropped."
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
                        head_drop_count += 1
                        posture_warning += "Head too close."
            else:
                count3 = 1
                posture_start_time3 = None


            if posture_warning:
                posture_label.config(text=posture_warning, fg="red",font=space_font)
            else:
                posture_label.config(text="Posture looks good!", fg="green",font=space_font)

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

# Run the app
root.mainloop()
