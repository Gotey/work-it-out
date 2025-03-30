import cv2
import mediapipe as mp

# === CONFIGURATION ===
CONFIG = {
    "show_labels": True,
    "min_visibility": 0.5,
    "show_reps": True,
    "vertical_margin": 20  # pixel threshold for head vs wrist difference
}

# === Setup Pose Detection ===
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, model_complexity=2)

# === Landmark indices (including NOSE for head detection) ===
KEYPOINTS = {
    "NOSE": 0,
    "LEFT_SHOULDER": 11,
    "RIGHT_SHOULDER": 12,
    "LEFT_WRIST": 15,
    "RIGHT_WRIST": 16
}

rep_count = 0
rep_state = "WAITING_DOWN"  # Possible states: WAITING_DOWN, WAITING_UP
hit_bottom = False

# === Utility Functions ===
def get_y(lm, h):
    return lm.y * h

def visible(lm):
    return lm.visibility >= CONFIG["min_visibility"]

def average_y(lm1, lm2, h):
    return (get_y(lm1, h) + get_y(lm2, h)) / 2

# === Pull Up Detection ===
def detect_pullup_status(landmarks, h):
    required = ["NOSE", "LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_WRIST", "RIGHT_WRIST"]
    if not all(visible(landmarks[KEYPOINTS[k]]) for k in required):
        return {"hanging": False, "pullup": False}
    
    # Get vertical positions in pixels
    nose_y = get_y(landmarks[KEYPOINTS["NOSE"]], h)
    shoulder_y = average_y(landmarks[KEYPOINTS["LEFT_SHOULDER"]],
                             landmarks[KEYPOINTS["RIGHT_SHOULDER"]], h)
    wrist_y = average_y(landmarks[KEYPOINTS["LEFT_WRIST"]],
                        landmarks[KEYPOINTS["RIGHT_WRIST"]], h)
    
    # For a proper hanging (pull-up) position, the wrists should be higher than the shoulders.
    proper_hanging = wrist_y < shoulder_y
    
    # Define bottom phase ("hanging"): proper hanging and head is clearly below the hands.
    hanging = proper_hanging and ((nose_y - wrist_y) > CONFIG["vertical_margin"])
    
    # Define top phase ("pullup"): proper hanging and head goes above the hands.
    pullup = proper_hanging and ((wrist_y - nose_y) > CONFIG["vertical_margin"])
    
    return {"hanging": hanging, "pullup": pullup}

# === Webcam Setup ===
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip and process frame
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    if results.pose_landmarks:
        h, w, _ = frame.shape
        landmarks = results.pose_landmarks.landmark

        phase = detect_pullup_status(landmarks, h)

        # === State Machine for Pull Ups ===
        if rep_state == "WAITING_DOWN":
            # Waiting for hanging position
            if phase["hanging"]:
                hit_bottom = True
                rep_state = "WAITING_UP"
        elif rep_state == "WAITING_UP":
            # Waiting for pull-up: head above hands
            if hit_bottom and phase["pullup"]:
                rep_count += 1
                hit_bottom = False
                rep_state = "WAITING_DOWN"

        # === Draw Landmarks ===
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=4),
            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=3)
        )

        # === Display Info ===
        if CONFIG["show_labels"]:
            label = f"Pull Up: {rep_state.replace('_', ' ').title()}"
            if hit_bottom:
                label += " (Hanging ✔)"
            cv2.putText(frame, label, (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

        if CONFIG["show_reps"]:
            cv2.putText(frame, f"Pull Up Reps: {rep_count}", (30, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 100), 2)

    cv2.imshow("Pull Up Tracker", frame)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()
