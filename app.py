import cv2
import mediapipe as mp
import statistics
import time
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk  # For converting OpenCV frame to Tkinter-compatible format

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Capture video
cap = cv2.VideoCapture(0)  # Use 0 for default webcam

# Initial calibration
initial_head_position = None
initial_head_shoulder_distance = None
countdown_start_time = time.time()
countdown_duration = 5

# Function to calculate distance
def calculate_distance(point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2) ** 0.5

def process_frame():
    global initial_head_position, initial_head_shoulder_distance, countdown_start_time

    ret, frame = cap.read()
    if not ret:
        return

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb)

    if result.pose_landmarks:
        left_shoulder = result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        head = result.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]

        left_shoulder_pos = (left_shoulder.x * frame.shape[1], left_shoulder.y * frame.shape[0])
        right_shoulder_pos = (right_shoulder.x * frame.shape[1], right_shoulder.y * frame.shape[0])
        head_pos = (head.x * frame.shape[1], head.y * frame.shape[0])

        current_head_position = head_pos[1]
        current_shoulder_level = left_shoulder_pos[1]
        current_head_shoulder_distance = abs(current_head_position - current_shoulder_level)

        time_elapsed = time.time() - countdown_start_time
        if initial_head_position is None or initial_head_shoulder_distance is None:
            if time_elapsed < countdown_duration:
                cv2.putText(frame, f"Sit Up Straight!: {int(countdown_duration - time_elapsed)}",
                            (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 2)
            else:
                initial_head_position = current_head_position
                initial_head_shoulder_distance = current_head_shoulder_distance
        else:
            posture_bad = False
            if current_head_shoulder_distance < initial_head_shoulder_distance - 30:
                posture_bad = True
                cv2.putText(frame, "Bad Posture: Shoulders too high", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            if current_head_position > initial_head_position + 30:
                posture_bad = True
                cv2.putText(frame, "Bad Posture: Head dropped", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Add info
            cv2.putText(frame, f"Head Shoulder Distance: {current_head_shoulder_distance:.2f}", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(frame, f"Head Pos: {current_head_position:.2f}", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Draw pose landmarks
        mp.solutions.drawing_utils.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Convert frame to image for Tkinter
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    imgtk = ImageTk.PhotoImage(image=img)

    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

    # Repeat after 10ms
    root.after(10, process_frame)

# === Tkinter GUI Setup ===
root = Tk()
root.title("Posture Corrector")

style = ttk.Style()
style.theme_create("space", parent="alt", settings={
    "TLabel": {"configure": {"background": "#0B1B3A", "foreground": "#B0C4DE", "font": ("Comic Sans", 12)}},
    "TFrame": {"configure": {"background": "#0B1B3A"}},
})
style.theme_use("space")

mainframe = ttk.Frame(root)
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe['padding'] = (10, 10, 10, 10)

# Add video label
video_label = Label(mainframe)
video_label.grid(column=0, row=0)

# Start video processing loop
process_frame()

# Clean exit on close
def on_closing():
    cap.release()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Run the app
root.mainloop()
