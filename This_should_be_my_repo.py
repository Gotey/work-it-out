import cv2
import mediapipe as mp
from collections import deque

# === CONFIGURATION ===
CONFIG = {
    "show_labels": True,
    "min_visibility": 0.5,
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
    "LEFT_KNEE": 25, "RIGHT_KNEE": 26,
    "LEFT_ANKLE": 27, "RIGHT_ANKLE": 28
}

rep_count = 0
rep_state = "WAITING_DOWN"  # Possible values: WAITING_DOWN, WAITING_UP
hit_bottom = False

# === Utility Functions ===
def get_y(lm, h):
    return lm.y * h

def visible(lm):
    return lm.visibility >= CONFIG["min_visibility"]

def average_y(lm1, lm2, h):
    return (get_y(lm1, h) + get_y(lm2, h)) / 2

# === Deadlift Phase Detection ===
def detect_deadlift_status(landmarks, h):
    required = [
        "LEFT_HIP", "RIGHT_HIP", "LEFT_WRIST", "RIGHT_WRIST",
        "LEFT_ANKLE", "RIGHT_ANKLE", "LEFT_KNEE", "RIGHT_KNEE"
    ]
    if not all(visible(landmarks[KEYPOINTS[k]]) for k in required):
        return {
            "near_ankles": False,
            "near_hips": False,
            "hips_below_knees": False
        }

    # Averages
    avg_hand_y = average_y(landmarks[KEYPOINTS["LEFT_WRIST"]], landmarks[KEYPOINTS["RIGHT_WRIST"]], h)
    avg_hip_y = average_y(landmarks[KEYPOINTS["LEFT_HIP"]], landmarks[KEYPOINTS["RIGHT_HIP"]], h)
    avg_ankle_y = average_y(landmarks[KEYPOINTS["LEFT_ANKLE"]], landmarks[KEYPOINTS["RIGHT_ANKLE"]], h)
    avg_knee_y = average_y(landmarks[KEYPOINTS["LEFT_KNEE"]], landmarks[KEYPOINTS["RIGHT_KNEE"]], h)

    # Criteria
    hand_near_ankles = abs(avg_hand_y - avg_ankle_y) < 80
    hand_near_hips = abs(avg_hand_y - avg_hip_y) < 60
    hips_lower_than_knees = avg_hip_y > avg_knee_y  # you bent over enough

    return {
        "near_ankles": hand_near_ankles,
        "near_hips": hand_near_hips,
        "hips_below_knees": hips_lower_than_knees
    }

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

        # === Deadlift Logic ===
        phase = detect_deadlift_status(landmarks, h)

        # State machine with bottom-out check
        if rep_state == "WAITING_DOWN":
            if phase["near_ankles"] and phase["hips_below_knees"]:
                hit_bottom = True
                rep_state = "WAITING_UP"

        elif rep_state == "WAITING_UP":
            if hit_bottom and phase["near_hips"]:
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

        if CONFIG["show_labels"]:
            label = f"State: {rep_state.replace('_', ' ').title()}"
            if hit_bottom:
                label += " (Bottom ✔)"
            cv2.putText(frame, label, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

        if CONFIG["show_reps"]:
            cv2.putText(frame, f"Deadlift Reps: {rep_count}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 100), 2)

    cv2.imshow("Deadlift Tracker (Stable & Accurate)", frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()
