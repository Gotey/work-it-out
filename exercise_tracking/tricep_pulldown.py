import cv2
import mediapipe as mp
import math
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Only show errors, no warnings or info
# === CONFIGURATION ===
CONFIG = {
    "show_labels": True,
    "min_visibility": 0.5,
    "show_reps": True,
    "show_form_warnings": True
}

# === Setup Pose Detection ===
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, model_complexity=2)

# === Landmark indices ===
KEYPOINTS = {
    "RIGHT_SHOULDER": 12,
    "RIGHT_ELBOW": 14,
    "RIGHT_WRIST": 16,
    "RIGHT_HIP": 24
}

rep_count = 0
rep_state = "WAITING_DOWN"
hit_top = False
bad_form = False

# === Utility Functions ===
def visible(lm):
    return lm.visibility >= CONFIG["min_visibility"]

def get_point(lm, h, w):
    return (int(lm.x * w), int(lm.y * h))

def calc_angle(a, b, c):
    ba = [a[0] - b[0], a[1] - b[1]]
    bc = [c[0] - b[0], c[1] - b[1]]
    dot = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.sqrt(ba[0]**2 + ba[1]**2)
    mag_bc = math.sqrt(bc[0]**2 + bc[1]**2)
    angle = math.acos(dot / (mag_ba * mag_bc + 1e-6))
    return math.degrees(angle)

# === Tricep Pulldown Detection ===
def detect_pulldown(landmarks, h, w):
    required = ["RIGHT_SHOULDER", "RIGHT_ELBOW", "RIGHT_WRIST", "RIGHT_HIP"]
    if not all(visible(landmarks[KEYPOINTS[k]]) for k in required):
        return {
            "pull_down": False,
            "arm_reset": False,
            "form_ok": True,
            "angle": None
        }

    shoulder = get_point(landmarks[KEYPOINTS["RIGHT_SHOULDER"]], h, w)
    elbow = get_point(landmarks[KEYPOINTS["RIGHT_ELBOW"]], h, w)
    wrist = get_point(landmarks[KEYPOINTS["RIGHT_WRIST"]], h, w)
    hip = get_point(landmarks[KEYPOINTS["RIGHT_HIP"]], h, w)

    # Elbow angle
    angle = calc_angle(shoulder, elbow, wrist)

    # Posture check (back arch)
    vertical_line_diff = abs(shoulder[0] - hip[0])
    form_ok = vertical_line_diff < 40  # if back is aligned well from the side

    return {
        "pull_down": angle > 160,
        "arm_reset": angle < 60,
        "form_ok": form_ok,
        "angle": int(angle)
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

        phase = detect_pulldown(landmarks, h, w)
        bad_form = not phase["form_ok"]

        if rep_state == "WAITING_DOWN":
            if phase["arm_reset"]:
                hit_top = True
                rep_state = "WAITING_UP"

        elif rep_state == "WAITING_UP":
            if hit_top and phase["pull_down"]:
                if not bad_form:
                    rep_count += 1
                hit_top = False
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
            label = f"Pulldown: {rep_state.replace('_', ' ').title()} | Angle: {phase['angle']}"
            if hit_top:
                label += " (Ready ✔)"
            cv2.putText(frame, label, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        if CONFIG["show_reps"]:
            cv2.putText(frame, f"Pulldown Reps: {rep_count}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 100), 2)

        if CONFIG["show_form_warnings"] and bad_form:
            cv2.putText(frame, "⚠️ Keep Back Upright!", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 100, 255), 2)

    cv2.imshow("Tricep Pulldown Tracker (Form + Reps)", frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()
