import cv2
import mediapipe as mp
import statistics
import time

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
cap = cv2.VideoCapture(1)

# store the initial positions of the head and shoulders for calibration
initial_shoulder_distance = None
initial_head_position = None

# function to calculate distance between two points
def calculate_distance(point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2) ** 0.5

# countdown timer
countdown_start_time = time.time() #current time for comparison
countdown_duration = 5  # seconds

posture_start_time = None
posture_start_time2 = None
count = 1
count2 = 1

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # this just makes the cam act as a mirror
    frame = cv2.flip(frame, 1)
    # makes the frame compatible for mediapipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = pose.process(rgb)

    # if we detect a person
    if result.pose_landmarks:
        # Get the current positions of head and two shoulders
        left_shoulder = result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        head = result.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]

        # Convert landmark positions to pixel values
        left_shoulder_pos = (left_shoulder.x * frame.shape[1], left_shoulder.y * frame.shape[0])
        right_shoulder_pos = (right_shoulder.x * frame.shape[1], right_shoulder.y * frame.shape[0])
        head_pos = (head.x * frame.shape[1], head.y * frame.shape[0])

        # # Calculate the shoulder distance (Euclidean distance between left and right shoulders)
        # current_shoulder_distance = calculate_distance(left_shoulder_pos, right_shoulder_pos)

        # Calculate the head position (just the y-coordinate for head drop detection)
        current_head_position = head_pos[1]

        # Calculate the distance between the head and the shoulders (scrunched shoulders pose)
        current_shoulder_level = left_shoulder_pos[1] # statistics.mean([left_shoulder_pos[1], right_shoulder_pos[1]])
        current_head_shoulder_distance = abs(current_head_position - current_shoulder_level)

        # Handle countdown for initial posture capture
        time_elapsed = time.time() - countdown_start_time
        if current_head_shoulder_distance is None or initial_head_position is None:
            # if we are still counting down then we display it, if not we capture the positions of the head and shoulders
            if time_elapsed < countdown_duration:
                cv2.putText(frame, f"Sit Up Straight!: {int(countdown_duration - time_elapsed)}",
                            (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 2)
            else:
                initial_head_shoulder_distance = current_head_shoulder_distance
                initial_head_position = current_head_position
                print("Initial head-shoulder distance:", initial_head_shoulder_distance)
                print("Initial head position:", initial_head_position)
        # we have already initialized the values now we constantly compare them
        else:
            # Posture analysis: Check for deviation from the initial values
            shoulder_raise_threshold = -30  # Adjust this threshold based on testing

            # Check for shoulders raised (shoulders too high)
            if current_head_shoulder_distance < initial_head_shoulder_distance + shoulder_raise_threshold:
                if count == 1:
                    posture_start_time = time.time()
                    count += 1
                else:
                    posture_time_elapsed = time.time() - posture_start_time
                    if posture_time_elapsed >= 7:
                        cv2.putText(frame, "Bad Posture: Shoulders too high", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                # Reset if posture improves
                count = 1
                posture_start_time = None

            # Check for head dropped
            if current_head_position > initial_head_position + 30:
                if count2 == 1:
                    posture_start_time2 = time.time()
                    count2 += 1
                else:
                    posture_time_elapsed2 = time.time() - posture_start_time2
                    if posture_time_elapsed2 >= 7:
                        cv2.putText(frame, "Bad Posture: Head dropped", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                # Reset if posture improves
                count2 = 1
                posture_start_time2 = None


            # Display the shoulder distance and head position on the frame
            cv2.putText(frame, f"Head Shoulder Distance: {current_head_shoulder_distance:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(frame, f"Head Pos: {current_head_position:.2f}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Draw pose landmarks on the frame
        mp.solutions.drawing_utils.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # the frame of the pop up window and the title for it
    cv2.imshow("Posture Detection", frame)
    if cv2.waitKey(10) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()