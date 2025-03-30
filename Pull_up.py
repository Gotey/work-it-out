import cv2
import mediapipe as mp
import math

# === CONFIGURATION ===
CONFIG = {
    "show_labels": True,
    "min_visibility": 0.5,
    "show_reps": True,
    "vertical_margin": 20,
    "wrist_alignment_tolerance": 10,
    "hold_frames_required": 40  # ~2 seconds if webcam is 20 fps
}

# === Setup Pose Detection ===
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, model_complexity=2)

KEYPOINTS = {
    "NOSE": 0,
    "LEFT_SHOULDER": 11,
    "RIGHT_SHOULDER": 12,
    "LEFT_WRIST": 15,
    "RIGHT_WRIST": 16
}

rep_count = 0
rep_state = "WAITING_DOWN"
hit_bottom = False
hold_counter = 0  # counts frames where angle is within range

# === Utility Functions ===
def get_y(lm, h):
    return lm.y * h

def get_x(lm, w):
    return lm.x * w

def visible(lm):
    return lm.visibility >= CONFIG["min_visibility"]

def calc_angle(a, b, c):
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])
    dot_product = ba[0]*bc[0] + ba[1]*bc[1]
    magnitude_ba = math.sqrt(ba[0]**2 + ba[1]**2)
    magnitude_bc = math.sqrt(bc[0]**2 + bc[1]**2)
    if magnitude_ba * magnitude_bc == 0:
        return 0
    angle = math.acos(dot_product / (magnitude_ba * magnitude_bc))
    return math.degrees(angle)

# === Pull Up Detection + Encouragement ===
def detect_pullup_status(landmarks, h, w):
    required = ["NOSE", "LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_WRIST", "RIGHT_WRIST"]
    if not all(visible(landmarks[KEYPOINTS[k]]) for k in required):
        return {"hanging": False, "pullup": False, "wrists_aligned": True, "avg_angle": 0}
    
    nose_y = get_y(landmarks[KEYPOINTS["NOSE"]], h)
    left_wrist = (get_x(landmarks[KEYPOINTS["LEFT_WRIST"]], w), get_y(landmarks[KEYPOINTS["LEFT_WRIST"]], h))
    right_wrist = (get_x(landmarks[KEYPOINTS["RIGHT_WRIST"]], w), get_y(landmarks[KEYPOINTS["RIGHT_WRIST"]], h))
    left_shoulder = (get_x(landmarks[KEYPOINTS["LEFT_SHOULDER"]], w), get_y(landmarks[KEYPOINTS["LEFT_SHOULDER"]], h))
    right_shoulder = (get_x(landmarks[KEYPOINTS["RIGHT_SHOULDER"]], w), get_y(landmarks[KEYPOINTS["RIGHT_SHOULDER"]], h))

    wrist_y = (left_wrist[1] + right_wrist[1]) / 2
    shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2

    wrists_aligned = abs(left_wrist[1] - right_wrist[1]) <= CONFIG["wrist_alignment_tolerance"]

    # Standard pull-up detection
    proper_hanging = wrist_y < shoulder_y
    hanging = proper_hanging and ((nose_y - wrist_y) > CONFIG["vertical_margin"])
    pullup = proper_hanging and ((wrist_y - nose_y) > CONFIG["vertical_margin"])

    # Angle
    left_angle = calc_angle(right_shoulder, left_shoulder, left_wrist)
    right_angle = calc_angle(left_shoulder, right_shoulder, right_wrist)
    avg_angle = (left_angle + right_angle) / 2

    return {"hanging": hanging, "pullup": pullup, "wrists_aligned": wrists_aligned, "avg_angle": avg_angle}

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

        phase = detect_pullup_status(landmarks, h, w)

        # === Support Message Logic ===
        if 60 <= phase["avg_angle"] <= 120 and rep_state == "WAITING_UP":
            hold_counter += 1
        else:
            hold_counter = 0

        # === State Machine for Pull Ups ===
        if rep_state == "WAITING_DOWN":
            if phase["hanging"]:
                hit_bottom = True
                rep_state = "WAITING_UP"
        elif rep_state == "WAITING_UP":
            if hit_bottom and phase["pullup"] and phase["wrists_aligned"]:
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

            # Encouragement label
            if hold_counter >= CONFIG["hold_frames_required"]:
                msg = "Keep it going!" if hold_counter % 80 < 40 else "You can do it!"
                cv2.putText(frame, msg, (30, 120),
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
