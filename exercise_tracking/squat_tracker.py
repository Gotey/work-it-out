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
    "LEFT_HIP": 23, "RIGHT_HIP": 24,
    "LEFT_KNEE": 25, "RIGHT_KNEE": 26,
    "LEFT_ANKLE": 27, "RIGHT_ANKLE": 28,
    "LEFT_WRIST": 15, "RIGHT_WRIST": 16
}

# === Tracking State ===
rep_count = 0
rep_state = "WAITING_DOWN"
hit_bottom = False

# === Utility Functions ===
def get_y(lm, h):
    return lm.y * h

def visible(lm):
    return lm.visibility >= CONFIG["min_visibility"]

def average_y(lm1, lm2, h):
    return (get_y(lm1, h) + get_y(lm2, h)) / 2

# === Squat Detection ===
def detect_squat_status(landmarks, h):
    if not all(visible(landmarks[KEYPOINTS[k]]) for k in ["LEFT_HIP", "RIGHT_HIP", "LEFT_KNEE", "RIGHT_KNEE", "LEFT_ANKLE", "RIGHT_ANKLE", "LEFT_WRIST", "RIGHT_WRIST"]):
        return None

    hip_y = average_y(landmarks[KEYPOINTS["LEFT_HIP"]], landmarks[KEYPOINTS["RIGHT_HIP"]], h)
    knee_y = average_y(landmarks[KEYPOINTS["LEFT_KNEE"]], landmarks[KEYPOINTS["RIGHT_KNEE"]], h)
    wrist_y = average_y(landmarks[KEYPOINTS["LEFT_WRIST"]], landmarks[KEYPOINTS["RIGHT_WRIST"]], h)

    hips_below_knees = hip_y > knee_y
    arms_up = wrist_y < knee_y

    return {"hips_below_knees": hips_below_knees, "arms_up": arms_up}

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
        status = detect_squat_status(landmarks, h)

        if status:
            if rep_state == "WAITING_DOWN":
                if status["hips_below_knees"] and status["arms_up"]:
                    hit_bottom = True
                    rep_state = "WAITING_UP"
            elif rep_state == "WAITING_UP":
                if hit_bottom and not status["hips_below_knees"]:
                    rep_count += 1
                    hit_bottom = False
                    rep_state = "WAITING_DOWN"

        # === Draw Skeleton and Info ===
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=4),
            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=3)
        )

        if CONFIG["show_labels"]:
            label = f"Squat: {rep_state} {'✔' if hit_bottom else ''}"
            cv2.putText(frame, label, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 180, 255), 2)

        if CONFIG["show_reps"]:
            cv2.putText(frame, f"Squat Reps: {rep_count}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 100), 2)

    cv2.imshow("Squat Tracker", frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()
