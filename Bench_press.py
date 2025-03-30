import cv2
import mediapipe as mp

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
    "LEFT_WRIST": 15, "RIGHT_WRIST": 16
}

rep_count = 0
rep_state = "WAITING_DOWN"  # Possible: WAITING_DOWN, WAITING_UP
hit_bottom = False

# === Utility Functions ===
def get_y(lm, h):
    return lm.y * h

def visible(lm):
    return lm.visibility >= CONFIG["min_visibility"]

def average_y(lm1, lm2, h):
    return (get_y(lm1, h) + get_y(lm2, h)) / 2

# === Bench Press Detection ===
def detect_bench_press_status(landmarks, h):
    required = ["LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_WRIST", "RIGHT_WRIST"]
    if not all(visible(landmarks[KEYPOINTS[k]]) for k in required):
        return {
            "hands_near_chest": False,
            "hands_extended_up": False
        }

    shoulder_y = average_y(landmarks[KEYPOINTS["LEFT_SHOULDER"]], landmarks[KEYPOINTS["RIGHT_SHOULDER"]], h)
    wrist_y = average_y(landmarks[KEYPOINTS["LEFT_WRIST"]], landmarks[KEYPOINTS["RIGHT_WRIST"]], h)

    hands_near_chest = abs(wrist_y - shoulder_y) < 40
    hands_extended_up = wrist_y < shoulder_y - 60  # higher than shoulders (remember: y = 0 is top of image)

    return {
        "hands_near_chest": hands_near_chest,
        "hands_extended_up": hands_extended_up
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

        phase = detect_bench_press_status(landmarks, h)

        # === State Machine for Bench Press ===
        if rep_state == "WAITING_DOWN":
            if phase["hands_near_chest"]:
                hit_bottom = True
                rep_state = "WAITING_UP"

        elif rep_state == "WAITING_UP":
            if hit_bottom and phase["hands_extended_up"]:
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
            label = f"Bench Press: {rep_state.replace('_', ' ').title()}"
            if hit_bottom:
                label += " (Chest ✔)"
            cv2.putText(frame, label, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

        if CONFIG["show_reps"]:
            cv2.putText(frame, f"Bench Press Reps: {rep_count}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 100), 2)

    cv2.imshow("Bench Press Tracker", frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()
