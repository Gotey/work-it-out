import cv2
import mediapipe as mp
import math
from collections import deque

# === CONFIGURATION ===
CONFIG = {
    "show_labels": True,
    "min_visibility": 0.5,
    "pose_smoothing_frames": 5,
    "show_reps": True
}

# === Setup Pose Detection ===
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, model_complexity=2)

# === Landmark indices ===
KEYPOINTS = {
    "LEFT_SHOULDER": 11, "RIGHT_SHOULDER": 12,
    "LEFT_ELBOW": 13, "RIGHT_ELBOW": 14,
    "LEFT_WRIST": 15, "RIGHT_WRIST": 16,
    "LEFT_HIP": 23, "RIGHT_HIP": 24,
    "LEFT_KNEE": 25, "RIGHT_KNEE": 26
}

pose_history = deque(maxlen=CONFIG["pose_smoothing_frames"])
rep_count = 0
last_pose_state = "STANDING"

# === Utility Functions ===
def get_y(lm, h):
    return lm.y * h

def visible(lm):
    return lm.visibility >= CONFIG["min_visibility"]

# === Deadlift Classifier ===
def classify_deadlift(landmarks, h):
    required = ["LEFT_HIP", "RIGHT_HIP", "LEFT_KNEE", "RIGHT_KNEE", "LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_WRIST", "RIGHT_WRIST"]
    if not all(visible(landmarks[KEYPOINTS[k]]) for k in required):
        return "UNKNOWN"

    lh_y = get_y(landmarks[KEYPOINTS["LEFT_HIP"]], h)
    rh_y = get_y(landmarks[KEYPOINTS["RIGHT_HIP"]], h)
    ls_y = get_y(landmarks[KEYPOINTS["LEFT_SHOULDER"]], h)
    rs_y = get_y(landmarks[KEYPOINTS["RIGHT_SHOULDER"]], h)
    lw_y = get_y(landmarks[KEYPOINTS["LEFT_WRIST"]], h)
    rw_y = get_y(landmarks[KEYPOINTS["RIGHT_WRIST"]], h)

    hips_below_shoulders = lh_y > ls_y and rh_y > rs_y
    arms_down = lw_y > lh_y and rw_y > rh_y

    if hips_below_shoulders and arms_down:
        return "DEADLIFT"
    else:
        return "STANDING"

# === Webcam Setup ===

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    if results.pose_landmarks:
        h, w, _ = frame.shape
        landmarks = results.pose_landmarks.landmark

        # === Classify & Smooth Pose ===
        current_class = classify_deadlift(landmarks, h)
        pose_history.append(current_class)
        smoothed_pose = max(set(pose_history), key=pose_history.count)

        # === Rep Count (DEADLIFT → STANDING)
        if smoothed_pose != last_pose_state:
            if last_pose_state == "DEADLIFT" and smoothed_pose == "STANDING":
                rep_count += 1
            last_pose_state = smoothed_pose

        # === Draw Landmarks
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=4),
            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=3)
        )

        if CONFIG["show_labels"]:
            cv2.putText(frame, f"Pose: {smoothed_pose}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)

        if CONFIG["show_reps"]:
            cv2.putText(frame, f"Deadlift Reps: {rep_count}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 100), 2)

    cv2.imshow("Deadlift Tracker", frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()
