import cv2
import mediapipe as mp
import math
import os
import pygame

pygame.mixer.init()
sound = pygame.mixer.Sound("exercise_tracking/sfx_point.mp3")  # Use WAV for better compatibility if possible

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Only show errors, no warnings or info
# === CONFIGURATION ===
CONFIG = {
    "show_labels": True,
    "min_visibility": 0.5,
    "show_reps": True,
    "knee_ankle_threshold": 40  # threshold for how far knee can go ahead of ankle (in pixels)
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

# === Lunge Detection with Automatic Front Leg ===
def detect_lunge_phase(landmarks, h, w):
    if not all(visible(landmarks[KEYPOINTS[k]]) for k in ["LEFT_KNEE", "RIGHT_KNEE"]):
        return None

    # Decide which knee is more forward (closer to camera in X)
    left_knee_x = landmarks[KEYPOINTS["LEFT_KNEE"]].x
    right_knee_x = landmarks[KEYPOINTS["RIGHT_KNEE"]].x

    if left_knee_x < right_knee_x:
        # Left leg is leading
        front_knee = get_point(landmarks[KEYPOINTS["LEFT_KNEE"]], h, w)
        front_ankle = get_point(landmarks[KEYPOINTS["LEFT_ANKLE"]], h, w)
        front_hip = get_point(landmarks[KEYPOINTS["LEFT_HIP"]], h, w)
    else:
        # Right leg is leading
        front_knee = get_point(landmarks[KEYPOINTS["RIGHT_KNEE"]], h, w)
        front_ankle = get_point(landmarks[KEYPOINTS["RIGHT_ANKLE"]], h, w)
        front_hip = get_point(landmarks[KEYPOINTS["RIGHT_HIP"]], h, w)

    # === Phase detection ===
    angle = calc_angle(front_hip, front_knee, front_ankle)
    deep_lunge = angle < 100
    recovered = angle > 160

    # === Incorrect form check ===
    knee_ahead = abs(front_knee[0] - front_ankle[0]) > CONFIG["knee_ankle_threshold"]
    incorrect_form = knee_ahead

    return {
        "deep_lunge": deep_lunge,
        "recovered": recovered,
        "knee_angle": int(angle),
        "incorrect_form": incorrect_form
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

        if phase:
            if rep_state == "WAITING_DOWN":
                if phase["deep_lunge"]:
                    hit_bottom = True
                    rep_state = "WAITING_UP"

            elif rep_state == "WAITING_UP":
                if hit_bottom and phase["recovered"]:
                    if not phase["incorrect_form"]:
                        rep_count += 1
                        rep_state = "WAITING_DOWN"
                        sound.play()
                    else:
                        rep_state = "INCORRECT FORM!"
                    hit_bottom = False

            elif rep_state == "INCORRECT FORM!":
                if phase["recovered"]:
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
        if CONFIG["show_labels"] and phase:
            label_color = (0, 0, 255) if phase["incorrect_form"] else (0, 255, 255)
            label = f"Lunge: {rep_state.replace('_', ' ').title()} | Angle: {phase['knee_angle']}"
            correct_label = "Make sure your knee doesn't go too far ahead of your ankle!"
            if hit_bottom:
                label += " (Deep ✔)"
            cv2.putText(frame, label, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, label_color, 2)
            if phase["incorrect_form"]:
                cv2.putText(frame, correct_label, (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        if CONFIG["show_reps"]:
            cv2.putText(frame, f"Lunge Reps: {rep_count}", (30, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 100), 2)

    cv2.imshow("Lunge Tracker", frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()
