import cv2
import mediapipe as mp
import math

# === CONFIGURATION ===
CONFIG = {
    "show_labels": True,
    "show_reps": True,
    "min_visibility": 0.5
}

# === Setup Pose ===
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, model_complexity=2)

# === Landmark indices ===
KEYPOINTS = {
    "LEFT_SHOULDER": 11,
    "LEFT_HIP": 23,
    "LEFT_ANKLE": 27
}

rep_count = 0
rep_state = "WAITING_UP"
hit_top = False

# === Utility Functions ===
def visible(lm):
    return lm.visibility >= CONFIG["min_visibility"]

def get_point(lm, h, w):
    return int(lm.x * w), int(lm.y * h)

def calc_angle(a, b, c):
    # angle at point b
    ba = [a[0] - b[0], a[1] - b[1]]
    bc = [c[0] - b[0], c[1] - b[1]]
    dot = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.sqrt(ba[0]**2 + ba[1]**2)
    mag_bc = math.sqrt(bc[0]**2 + bc[1]**2)
    return math.degrees(math.acos(dot / (mag_ba * mag_bc + 1e-6)))

# === Detection ===
def detect_leg_raise(landmarks, h, w):
    required = ["LEFT_SHOULDER", "LEFT_HIP", "LEFT_ANKLE"]
    if not all(visible(landmarks[KEYPOINTS[k]]) for k in required):
        return {
            "legs_up": False,
            "legs_down": False,
            "angle": None
        }

    shoulder = get_point(landmarks[KEYPOINTS["LEFT_SHOULDER"]], h, w)
    hip = get_point(landmarks[KEYPOINTS["LEFT_HIP"]], h, w)
    ankle = get_point(landmarks[KEYPOINTS["LEFT_ANKLE"]], h, w)

    angle = calc_angle(shoulder, hip, ankle)

    return {
        "legs_up": angle < 100,
        "legs_down": angle > 160,
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

        phase = detect_leg_raise(landmarks, h, w)

        if rep_state == "WAITING_UP":
            if phase["legs_up"]:
                hit_top = True
                rep_state = "WAITING_DOWN"

        elif rep_state == "WAITING_DOWN":
            if hit_top and phase["legs_down"]:
                rep_count += 1
                hit_top = False
                rep_state = "WAITING_UP"

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
            label = f"Leg Raise: {rep_state.replace('_', ' ').title()} | Angle: {phase['angle']}°"
            if hit_top:
                label += " (Up ✔)"
            cv2.putText(frame, label, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        if CONFIG["show_reps"]:
            cv2.putText(frame, f"Leg Raise Reps: {rep_count}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 100), 2)

    cv2.imshow("Leg Raise Tracker (Angle-Based)", frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()
