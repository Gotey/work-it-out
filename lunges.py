import cv2
import mediapipe as mp
import math

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
    "LEFT_HIP": 23, "RIGHT_HIP": 24,
    "LEFT_KNEE": 25, "RIGHT_KNEE": 26,
    "LEFT_ANKLE": 27, "RIGHT_ANKLE": 28
}

rep_count = 0
rep_state = "WAITING_DOWN"
hit_bottom = False

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

# === Lunge Detection ===
def detect_lunge_phase(landmarks, h, w):
    required = ["LEFT_HIP", "LEFT_KNEE", "LEFT_ANKLE"]
    if not all(visible(landmarks[KEYPOINTS[k]]) for k in required):
        return {
            "deep_lunge": False,
            "recovered": False,
            "knee_angle": None
        }

    hip = get_point(landmarks[KEYPOINTS["LEFT_HIP"]], h, w)
    knee = get_point(landmarks[KEYPOINTS["LEFT_KNEE"]], h, w)
    ankle = get_point(landmarks[KEYPOINTS["LEFT_ANKLE"]], h, w)

    angle = calc_angle(hip, knee, ankle)

    deep_lunge = angle < 100
    recovered = angle > 160

    return {
        "deep_lunge": deep_lunge,
        "recovered": recovered,
        "knee_angle": int(angle)
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

        phase = detect_lunge_phase(landmarks, h, w)

        if rep_state == "WAITING_DOWN":
            if phase["deep_lunge"]:
                hit_bottom = True
                rep_state = "WAITING_UP"

        elif rep_state == "WAITING_UP":
            if hit_bottom and phase["recovered"]:
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
            label = f"Lunge: {rep_state.replace('_', ' ').title()} | Angle: {phase['knee_angle']}"
            if hit_bottom:
                label += " (Deep ✔)"
            cv2.putText(frame, label, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        if CONFIG["show_reps"]:
            cv2.putText(frame, f"Lunge Reps: {rep_count}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 100), 2)

    cv2.imshow("Lunge Tracker", frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()
