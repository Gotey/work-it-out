import cv2
import mediapipe as mp
import math

# === CONFIGURATION ===
CONFIG = {
    "show_labels": True,
    "min_visibility": 0.5,
    "show_reps": True,
    "wrist_alignment_tolerance": 10,   # wrists must be within 10 pixels of each other
    "shoulder_press_margin": 120,      # how much higher the wrist must go to count as 'pressed'
    "max_arm_angle": 125               # max angle allowed when arms are extended (in degrees)
}

# === Setup Pose Detection ===
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, model_complexity=2)

# === Landmark indices ===
KEYPOINTS = {
    "LEFT_SHOULDER": 11,
    "RIGHT_SHOULDER": 12,
    "LEFT_WRIST": 15,
    "RIGHT_WRIST": 16
}

rep_count = 0
rep_state = "WAITING_DOWN"
hit_bottom = False

# === Utility Functions ===
def get_y(lm, h):
    return lm.y * h

def get_x(lm, w):
    return lm.x * w

def visible(lm):
    return lm.visibility >= CONFIG["min_visibility"]

def average_y(lm1, lm2, h):
    return (get_y(lm1, h) + get_y(lm2, h)) / 2

def calc_angle(a, b, c):
    """
    Returns angle ABC in degrees
    """
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])
    dot_product = ba[0]*bc[0] + ba[1]*bc[1]
    magnitude_ba = math.sqrt(ba[0]**2 + ba[1]**2)
    magnitude_bc = math.sqrt(bc[0]**2 + bc[1]**2)
    if magnitude_ba * magnitude_bc == 0:
        return 0
    angle = math.acos(dot_product / (magnitude_ba * magnitude_bc))
    return math.degrees(angle)

# === Shoulder Press Detection ===
def detect_shoulder_press_status(landmarks, h, w):
    required = ["LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_WRIST", "RIGHT_WRIST"]
    # error prevention when calculating angles :3
    if not all(visible(landmarks[KEYPOINTS[k]]) for k in required):
        return {"at_shoulder": False, 
                "pressed": False, 
                "wrists_aligned": True, 
                "correct_form": True,
                "avg_angle": 0
                }

    # Wrist alignment check
    left_wrist_y = get_y(landmarks[KEYPOINTS["LEFT_WRIST"]], h)
    right_wrist_y = get_y(landmarks[KEYPOINTS["RIGHT_WRIST"]], h)
    wrists_aligned = abs(left_wrist_y - right_wrist_y) <= CONFIG["wrist_alignment_tolerance"]

    # Shoulder and wrist positions
    left_shoulder = (get_x(landmarks[KEYPOINTS["LEFT_SHOULDER"]], w), get_y(landmarks[KEYPOINTS["LEFT_SHOULDER"]], h))
    right_shoulder = (get_x(landmarks[KEYPOINTS["RIGHT_SHOULDER"]], w), get_y(landmarks[KEYPOINTS["RIGHT_SHOULDER"]], h))
    left_wrist = (get_x(landmarks[KEYPOINTS["LEFT_WRIST"]], w), get_y(landmarks[KEYPOINTS["LEFT_WRIST"]], h))
    right_wrist = (get_x(landmarks[KEYPOINTS["RIGHT_WRIST"]], w), get_y(landmarks[KEYPOINTS["RIGHT_WRIST"]], h))

    shoulder_y = average_y(landmarks[KEYPOINTS["LEFT_SHOULDER"]], landmarks[KEYPOINTS["RIGHT_SHOULDER"]], h)
    wrist_y = average_y(landmarks[KEYPOINTS["LEFT_WRIST"]], landmarks[KEYPOINTS["RIGHT_WRIST"]], h)

    at_shoulder = abs(wrist_y - shoulder_y) < 40
    pressed = wrist_y < shoulder_y - CONFIG["shoulder_press_margin"]

    # Compute angles
    left_angle = calc_angle(right_shoulder, left_shoulder, left_wrist)
    right_angle = calc_angle(left_shoulder, right_shoulder, right_wrist)
    avg_angle = (left_angle + right_angle) / 2

    correct_form = avg_angle <= CONFIG["max_arm_angle"]

    return {
        "at_shoulder": at_shoulder,
        "pressed": pressed,
        "wrists_aligned": wrists_aligned,
        "correct_form": correct_form,
        "avg_angle": avg_angle
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

        phase = detect_shoulder_press_status(landmarks, h, w)

        # === State Machine ===
        if rep_state == "WAITING_DOWN":
            if phase["at_shoulder"]:
                hit_bottom = True
                rep_state = "WAITING_UP"
        elif rep_state == "WAITING_UP":
            if hit_bottom and phase["pressed"] and phase["wrists_aligned"]:
                if phase["correct_form"]:
                    rep_count += 1
                    rep_state = "WAITING_DOWN"
                else:
                    rep_state = "INCORRECT FORM!"
                hit_bottom = False
        elif rep_state == "INCORRECT FORM!":
            if phase["pressed"] and phase["wrists_aligned"] and phase["correct_form"]:
                    rep_count += 1
                    rep_state = "WAITING_DOWN"
            elif phase["at_shoulder"]:
                hit_bottom = True
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
            label_color = (0, 0, 255) if rep_state == "INCORRECT FORM!" else (0, 255, 255)
            label = f"Shoulder Press: {rep_state} | Angle: {int(phase['avg_angle'])}°"
            correct_label = "Make sure your Arms are DIRECTLY extended up, not outwards!"
            cv2.putText(frame, label, (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, label_color, 2)
            if phase["incorrect_form"]:
                cv2.putText(frame, correct_label, (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        if CONFIG["show_reps"]:
            cv2.putText(frame, f"Shoulder Press Reps: {rep_count}", (30, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 100), 2)

    cv2.imshow("Shoulder Press Tracker", frame)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()
