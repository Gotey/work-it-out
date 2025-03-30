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
    "LEFT_SHOULDER": 11, "RIGHT_SHOULDER": 12,
    "LEFT_ELBOW": 13, "RIGHT_ELBOW": 14,
    "LEFT_WRIST": 15, "RIGHT_WRIST": 16
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
    ba = [a[0] - b[0], a[1] - b[1]]
    bc = [c[0] - b[0], c[1] - b[1]]
    dot = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.sqrt(ba[0]**2 + ba[1]**2)
    mag_bc = math.sqrt(bc[0]**2 + bc[1]**2)
    return math.degrees(math.acos(dot / (mag_ba * mag_bc + 1e-6)))

# === Double Arm Curl Detection ===
def detect_both_bicep_curls(landmarks, h, w):
    required = [
        "LEFT_SHOULDER", "LEFT_ELBOW", "LEFT_WRIST",
        "RIGHT_SHOULDER", "RIGHT_ELBOW", "RIGHT_WRIST"
    ]
    if not all(visible(landmarks[KEYPOINTS[k]]) for k in required):
        return {
            "both_up": False,
            "both_down": False,
            "left_angle": None,
            "right_angle": None
        }

    # Points
    l_shoulder = get_point(landmarks[KEYPOINTS["LEFT_SHOULDER"]], h, w)
    l_elbow = get_point(landmarks[KEYPOINTS["LEFT_ELBOW"]], h, w)
    l_wrist = get_point(landmarks[KEYPOINTS["LEFT_WRIST"]], h, w)

    r_shoulder = get_point(landmarks[KEYPOINTS["RIGHT_SHOULDER"]], h, w)
    r_elbow = get_point(landmarks[KEYPOINTS["RIGHT_ELBOW"]], h, w)
    r_wrist = get_point(landmarks[KEYPOINTS["RIGHT_WRIST"]], h, w)

    # Angles
    left_angle = calc_angle(l_shoulder, l_elbow, l_wrist)
    right_angle = calc_angle(r_shoulder, r_elbow, r_wrist)

    both_up = left_angle < 50 and right_angle < 50
    both_down = left_angle > 160 and right_angle > 160

    return {
        "both_up": both_up,
        "both_down": both_down,
        "left_angle": int(left_angle),
        "right_angle": int(right_angle)
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

        phase = detect_both_bicep_curls(landmarks, h, w)

        if rep_state == "WAITING_UP":
            if phase["both_up"]:
                hit_top = True
                rep_state = "WAITING_DOWN"

        elif rep_state == "WAITING_DOWN":
            if hit_top and phase["both_down"]:
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
            label = (
                f"Curl State: {rep_state.replace('_', ' ').title()} | "
                f"L: {phase['left_angle']}°  R: {phase['right_angle']}°"
            )
            if hit_top:
                label += " (Both Up ✔)"
            cv2.putText(frame, label, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)

        if CONFIG["show_reps"]:
            cv2.putText(frame, f"Double Curl Reps: {rep_count}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 100), 2)

    cv2.imshow("Double Bicep Curl Tracker", frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()
