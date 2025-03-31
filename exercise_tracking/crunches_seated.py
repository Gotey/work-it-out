import cv2
import mediapipe as mp
import os
import pygame

pygame.mixer.init()
sound = pygame.mixer.Sound("exercise_tracking/sfx_point.mp3")  # Use WAV for better compatibility if possible

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Only show errors, no warnings or info

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
    "LEFT_HIP": 23, "RIGHT_HIP": 24
}

rep_count = 0
rep_state = "WAITING_UP"
hit_top = False

# === Utility Functions ===
def get_y(lm, h):
    return lm.y * h

def visible(lm):
    return lm.visibility >= CONFIG["min_visibility"]

def average_y(lm1, lm2, h):
    return (get_y(lm1, h) + get_y(lm2, h)) / 2

def detect_crunch_phase(landmarks, h):
    required = ["LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_HIP", "RIGHT_HIP"]
    if not all(visible(landmarks[KEYPOINTS[k]]) for k in required):
        return {
            "shoulders_up": False,
            "shoulders_down": False
        }

    shoulder_y = average_y(landmarks[KEYPOINTS["LEFT_SHOULDER"]], landmarks[KEYPOINTS["RIGHT_SHOULDER"]], h)
    hip_y = average_y(landmarks[KEYPOINTS["LEFT_HIP"]], landmarks[KEYPOINTS["RIGHT_HIP"]], h)

    # Distance between shoulders and hips
    shoulder_hip_dist = abs(shoulder_y - hip_y)

    return {
        "shoulders_up": shoulder_hip_dist < 80,
        "shoulders_down": shoulder_hip_dist > 130
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

        phase = detect_crunch_phase(landmarks, h)

        # === Crunch State Machine ===
        if rep_state == "WAITING_UP":
            if phase["shoulders_up"]:
                hit_top = True
                rep_state = "WAITING_DOWN"

        elif rep_state == "WAITING_DOWN":
            if hit_top and phase["shoulders_down"]:
                rep_count += 1
                hit_top = False
                rep_state = "WAITING_UP"
                sound.play()

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
            label = f"Crunch: {rep_state.replace('_', ' ').title()}"
            if hit_top:
                label += " (Top ✔)"
            cv2.putText(frame, label, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

        if CONFIG["show_reps"]:
            cv2.putText(frame, f"Crunch Reps: {rep_count}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 100), 2)

    cv2.imshow("Crunch Tracker", frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()
