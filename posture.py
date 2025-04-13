import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
cap = cv2.VideoCapture(1)

# store the initial positions of the head and shoulders
initial_shoulder_distance = None
initial_head_position = None

#function to calculate distance between two points
def calculate_distance(point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2) ** 0.5


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = pose.process(rgb)

    if result.pose_landmarks:
        # Get the current positions
        left_shoulder = result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        head = result.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]

        # Convert landmark positions to pixel values
        left_shoulder_pos = (left_shoulder.x * frame.shape[1], left_shoulder.y * frame.shape[0])
        right_shoulder_pos = (right_shoulder.x * frame.shape[1], right_shoulder.y * frame.shape[0])
        head_pos = (head.x * frame.shape[1], head.y * frame.shape[0])

        # Calculate the shoulder distance (Euclidean distance between left and right shoulders)
        current_shoulder_distance = calculate_distance(left_shoulder_pos, right_shoulder_pos)

        # Calculate the head position (just the y-coordinate for head drop detection)
        current_head_position = head_pos[1]
        
        if initial_shoulder_distance is None or initial_head_position is None:
            initial_shoulder_distance = current_shoulder_distance
            initial_head_position = current_head_position
            print("Initial shoulder distance:", initial_shoulder_distance)
            print("Initial head position:", initial_head_position)

        # Posture analysis: Check for deviation from the initial values
        posture_bad = False
        if current_shoulder_distance < initial_shoulder_distance * 0.9:  # Shoulders too close
            posture_bad = True
            cv2.putText(frame, "Bad Posture: Shoulders too close", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if current_head_position > initial_head_position + 30:  # Head dropped by more than 30 pixels
            posture_bad = True
            cv2.putText(frame, "Bad Posture: Head dropped", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Display the shoulder distance and head position on the frame
        cv2.putText(frame, f"Shoulder Dist: {current_shoulder_distance:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(frame, f"Head Pos: {current_head_position:.2f}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Draw pose landmarks on the frame
        mp.solutions.drawing_utils.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    cv2.imshow("Posture Detection", frame)
    if cv2.waitKey(10) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
