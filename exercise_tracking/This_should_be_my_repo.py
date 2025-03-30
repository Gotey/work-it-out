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
    "LEFT_ELBOW": 13, "RIGHT_ELBOW": 14,
    "LEFT_WRIST": 15, "RIGHT_WRIST": 16,
    "LEFT_HIP": 23, "RIGHT_HIP": 24,
    "LEFT_KNEE": 25, "RIGHT_KNEE": 26,
    "LEFT_ANKLE": 27, "RIGHT_ANKLE": 28
}

# === Tracking State ===
rep_count = {"DEADLIFT": 0, "SQUAT": 0}
rep_state = {"DEADLIFT": "WAITING_DOWN", "SQUAT": "WAITING_DOWN"}
hit_bottom = {"DEADLIFT": False, "SQUAT": False}

# === Utility Functions ===
def get_y(lm, h):
    return lm.y * h

def visible(lm):
    return lm.visibility >= CONFIG["min_visibility"]

def average_y(lm1, lm2, h):
    return (get_y(lm1, h) + get_y(lm2, h)) / 2

# === Movement Logic ===
def get_pose_status(landmarks, h):
    required = [
        "LEFT_HIP", "RIGHT_HIP", "LEFT_WRIST", "RIGHT_WRIST",
        "LEFT_KNEE", "RIGHT_KNEE", "LEFT_ANKLE", "RIGHT_ANKLE"
    ]
    if not all(visible(landmarks[KEYPOINTS[k]]) for k in required):
        return None

    # Y positions
    hip_y = average_y(landmarks[KEYPOINTS["LEFT_HIP"]], landmarks[KEYPOINTS["RIGHT_HIP"]], h)
    knee_y = average_y(landmarks[KEYPOINTS["LEFT_KNEE"]], landmarks[KEYPOINTS["RIGHT_KNEE"]], h)
    wrist_y = average_y(landmarks[KEYPOINTS["LEFT_WRIST"]], landmarks[KEYPOINTS["RIGHT_WRIST"]], h)
    ankle_y = average_y(landmarks[KEYPOINTS["LEFT_ANKLE"]], landmarks[KEYPOINTS["RIGHT_ANKLE"]], h)

    # Status flags
    hips_below_knees = hip_y > knee_y
    hands_near_ankles = abs(wrist_y - ankle_y) < 80
    hands_near_hips = abs(wrist_y - hip_y) < 60
    arms_up = wrist_y < knee_y  # for squat

    return {
        "hips_below_knees": hips_below_knees,
        "hands_near_ankles": hands_near_ankles,
        "hands_near_hips": hands_near_hips,
        "arms_up": arms_up
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
        status = get_pose_status(landmarks, h)

        if status:
            # === DEADLIFT STATE MACHINE ===
            if rep_state["DEADLIFT"] == "WAITING_DOWN":
                if status["hands_near_ankles"] and status["hips_below_knees"]:
                    hit_bottom["DEADLIFT"] = True
                    rep_state["DEADLIFT"] = "WAITING_UP"

            elif rep_state["DEADLIFT"] == "WAITING_UP":
                if hit_bottom["DEADLIFT"] and status["hands_near_hips"]:
                    rep_count["DEADLIFT"] += 1
                    hit_bottom["DEADLIFT"] = False
                    rep_state["DEADLIFT"] = "WAITING_DOWN"

            # === SQUAT STATE MACHINE ===
            if rep_state["SQUAT"] == "WAITING_DOWN":
                if status["hips_below_knees"] and status["arms_up"]:
                    hit_bottom["SQUAT"] = True
                    rep_state["SQUAT"] = "WAITING_UP"

            elif rep_state["SQUAT"] == "WAITING_UP":
                if hit_bottom["SQUAT"] and not status["hips_below_knees"]:
                    rep_count["SQUAT"] += 1
                    hit_bottom["SQUAT"] = False
                    rep_state["SQUAT"] = "WAITING_DOWN"

        # === Draw Skeleton and Info ===
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=4),
            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=3)
        )

        if CONFIG["show_labels"]:
            label_dl = f"Deadlift: {rep_state['DEADLIFT']} {'✔' if hit_bottom['DEADLIFT'] else ''}"
            label_sq = f"Squat: {rep_state['SQUAT']} {'✔' if hit_bottom['SQUAT'] else ''}"
            cv2.putText(frame, label_dl, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.putText(frame, label_sq, (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 180, 255), 2)

        if CONFIG["show_reps"]:
            cv2.putText(frame, f"Deadlift Reps: {rep_count['DEADLIFT']}", (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 100), 2)
            cv2.putText(frame, f"Squat Reps: {rep_count['SQUAT']}", (30, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 100), 2)

    cv2.imshow("Deadlift + Squat Tracker", frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()
