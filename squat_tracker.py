import cv2
import mediapipe as mp

# === CONFIGURATION ===
CONFIG = {
    "show_labels": True,
    "min_visibility": 0.5,
    "show_reps": True,
    "rise_threshold": 50  # minimum pixels the hip must rise from bottom
}

# === Setup Pose Detection ===
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, model_complexity=2)

# === Landmark indices ===
KEYPOINTS = {
    "LEFT_HIP": 23, "RIGHT_HIP": 24,
    "LEFT_KNEE": 25, "RIGHT_KNEE": 26,
    "LEFT_ANKLE": 27, "RIGHT_ANKLE": 28,
    "LEFT_WRIST": 15, "RIGHT_WRIST": 16,
    "LEFT_SHOULDER": 11, "RIGHT_SHOULDER": 12
}

# === Tracking State ===
rep_count = 0
rep_state = "WAITING_DOWN"  # Possible: WAITING_DOWN, WAITING_UP, INCORRECT FORM!
hit_bottom = False
bottom_hip_y = None  # will record the hip_y at the squat bottom

# === Utility Functions ===
def get_y(lm, h):
    return lm.y * h

def get_x(lm, w):
    return lm.x * w

def visible(lm):
    return lm.visibility >= CONFIG["min_visibility"]

def average_y(lm1, lm2, h):
    return (get_y(lm1, h) + get_y(lm2, h)) / 2

# === Squat Detection ===
def detect_squat_status(landmarks, h, w):
    # Check visibility for hips, knees, and ankles (we need at least one of each)
    left_hip_visible = visible(landmarks[KEYPOINTS["LEFT_HIP"]])
    right_hip_visible = visible(landmarks[KEYPOINTS["RIGHT_HIP"]])
    left_knee_visible = visible(landmarks[KEYPOINTS["LEFT_KNEE"]])
    right_knee_visible = visible(landmarks[KEYPOINTS["RIGHT_KNEE"]])
    left_ankle_visible = visible(landmarks[KEYPOINTS["LEFT_ANKLE"]])
    right_ankle_visible = visible(landmarks[KEYPOINTS["RIGHT_ANKLE"]])
    correct_form = True
    
    if not ((left_hip_visible or right_hip_visible) and (left_knee_visible or right_knee_visible)):
        return None

    # Use available hips to compute the average vertical position
    if left_hip_visible and right_hip_visible:
        hip_y = average_y(landmarks[KEYPOINTS["LEFT_HIP"]], landmarks[KEYPOINTS["RIGHT_HIP"]], h)
    elif left_hip_visible:
        hip_y = get_y(landmarks[KEYPOINTS["LEFT_HIP"]], h)
    else:
        hip_y = get_y(landmarks[KEYPOINTS["RIGHT_HIP"]], h)

    # Use available knees to compute the average vertical position
    if left_knee_visible and right_knee_visible:
        knee_y = average_y(landmarks[KEYPOINTS["LEFT_KNEE"]], landmarks[KEYPOINTS["RIGHT_KNEE"]], h)
    elif left_knee_visible:
        knee_y = get_y(landmarks[KEYPOINTS["LEFT_KNEE"]], h)
    else:
        knee_y = get_y(landmarks[KEYPOINTS["RIGHT_KNEE"]], h)

    # At squat bottom, the crease at the hips should be below the top of the knee cap.
    # Adding a small margin of 10 pixels.
    hips_below_knees = hip_y + 10 > knee_y
    # Standing (rising) is when hips are near or above the knees.
    hips_above_knees = hip_y - 10 < knee_y

    # Determine correct form based on horizontal alignment between knee and ankle.
    threshold = 50  # pixels; adjust as needed
    left_correct = True
    right_correct = True

    if left_knee_visible and left_ankle_visible:
        diff_left = abs(get_x(landmarks[KEYPOINTS["LEFT_KNEE"]], w) - get_x(landmarks[KEYPOINTS["LEFT_ANKLE"]], w))
        left_correct = (diff_left < threshold)
    if right_knee_visible and right_ankle_visible:
        diff_right = abs(get_x(landmarks[KEYPOINTS["RIGHT_KNEE"]], w) - get_x(landmarks[KEYPOINTS["RIGHT_ANKLE"]], w))
        right_correct = (diff_right < threshold)

    if left_knee_visible and left_ankle_visible and right_knee_visible and right_ankle_visible:
        correct_form = left_correct and right_correct
    elif left_knee_visible and left_ankle_visible:
        correct_form = left_correct
    elif right_knee_visible and right_ankle_visible:
        correct_form = right_correct

    # Return hip_y so we can compare changes over time.
    return {"hips_below_knees": hips_below_knees, 
            "correct_form": correct_form, 
            "hips_above_knees": hips_above_knees,
            "hip_y": hip_y}

# === Webcam Setup ===
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip frame so it acts like a mirror.
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    if results.pose_landmarks:
        h, w, _ = frame.shape
        landmarks = results.pose_landmarks.landmark
        status = detect_squat_status(landmarks, h, w)

        if status:
            # State machine for squat counting:
            if rep_state == "WAITING_DOWN":
                if not status["correct_form"]:
                    rep_state = "INCORRECT FORM!"
                if status["hips_below_knees"]:
                    hit_bottom = True
                    bottom_hip_y = status["hip_y"]  # record bottom position
                    rep_state = "WAITING_UP"

            elif rep_state == "WAITING_UP" and hit_bottom:
                # Only count a rep if the hips have risen sufficiently above the bottom position.
                if status["hip_y"] < bottom_hip_y - CONFIG["rise_threshold"]:
                    rep_count += 1
                    hit_bottom = False
                    rep_state = "WAITING_DOWN"

            elif rep_state == "INCORRECT FORM!":
                if status["hips_above_knees"] and status["correct_form"]:
                    rep_state = "WAITING_DOWN"
                    hit_bottom = False
                elif status["hips_below_knees"] and status["correct_form"]:
                    hit_bottom = True
                    bottom_hip_y = status["hip_y"]
                    rep_state = "WAITING_UP"

        # Draw skeleton and info.
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=4),
            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=3)
        )

        if CONFIG["show_labels"]:
            if rep_state == "INCORRECT FORM!":
                label_color = (0, 0, 255)  # Red
            else:
                label_color = (0, 180, 255)  # Default
            label = f"Squat: {rep_state} {'✔' if hit_bottom else ''}"
            correct_label = "Make sure to keep your knees aligned with your ankles!"
            cv2.putText(frame, label, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, label_color, 2)
            if status and not status["correct_form"]:
                cv2.putText(frame, correct_label, (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        if CONFIG["show_reps"]:
            cv2.putText(frame, f"Squat Reps: {rep_count}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 100), 2)

    cv2.imshow("Squat Tracker", frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()
