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
    "show_reps": True,
    "threshold_down": 20,   # minimum diff (elbow below shoulder) to consider a valid bottom
    "threshold_up": -20     # maximum diff (elbow above shoulder) to consider a valid top
}

# === Setup Pose Detection ===
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, model_complexity=2)

# === Landmark indices ===
KEYPOINTS = {
    "LEFT_SHOULDER": 11,
    "LEFT_ELBOW": 13
    # (We use only the left arm for this implementation)
}

# === Global State for Rep Detection (Left Arm) ===
rep_count = 0
rep_state = "WAITING_DOWN"  # Two states: WAITING_DOWN, WAITING_UP
prev_diff = None            # previous frame's (elbow_y - shoulder_y)
max_diff = None             # maximum diff observed in current DOWN state
min_diff = None             # minimum diff observed in current UP state

# === Utility Functions ===
def get_y(lm, h):
    return lm.y * h

def visible(lm):
    return lm.visibility >= CONFIG["min_visibility"]

def process_rep_state(left_shoulder, left_elbow, h):
    """
    Uses the left arm's vertical difference (elbow_y - shoulder_y) to update the rep state.
    
    Start state: waiting for a local maximum. We require that diff > threshold_down.
      - When the diff (current_diff) reaches a peak (i.e. current_diff < previous diff)
        and that peak (max_diff) is above the threshold, we switch to WAITING_UP.
    
    Finish state: in WAITING_UP we track the minimum diff.
      - When the diff starts increasing (current_diff > previous diff) and
        the recorded min_diff is below the finish threshold, a rep is counted.
    
    Returns the current difference.
    """
    global rep_state, rep_count, prev_diff, max_diff, min_diff
    current_diff = get_y(left_elbow, h) - get_y(left_shoulder, h)
    # Note: larger diff means elbow is lower than shoulder.
    # Negative diff means elbow is above shoulder.

    # Process state transitions:
    if rep_state == "WAITING_DOWN":
        # Update max_diff if current_diff is higher.
        if max_diff is None or current_diff > max_diff:
            max_diff = current_diff

        # If we have a previous frame and the diff has started to drop,
        # and we had reached a valid maximum (elbow sufficiently below shoulder),
        # then switch to WAITING_UP.
        if prev_diff is not None and current_diff < prev_diff and max_diff is not None:
            if max_diff >= CONFIG["threshold_down"]:
                rep_state = "WAITING_UP"
                min_diff = current_diff  # start tracking the minimum in the upward phase
    elif rep_state == "WAITING_UP":
        # Update min_diff if current_diff is lower.
        if min_diff is None or current_diff < min_diff:
            min_diff = current_diff

        # When the upward motion reverses (diff starts increasing) and
        # the minimum diff was below the finish threshold, count a rep.
        if prev_diff is not None and current_diff > prev_diff and min_diff is not None:
            if min_diff <= CONFIG["threshold_up"]:
                rep_count += 1
                rep_state = "WAITING_DOWN"
                # Reset for the next rep.
                max_diff = None
                min_diff = None
                sound.play()

    prev_diff = current_diff
    return current_diff

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

        # Ensure the necessary landmarks are visible.
        if visible(landmarks[KEYPOINTS["LEFT_SHOULDER"]]) and visible(landmarks[KEYPOINTS["LEFT_ELBOW"]]):
            left_shoulder = landmarks[KEYPOINTS["LEFT_SHOULDER"]]
            left_elbow = landmarks[KEYPOINTS["LEFT_ELBOW"]]
            diff = process_rep_state(left_shoulder, left_elbow, h)
        else:
            diff = None

        # Draw landmarks for feedback.
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=4),
            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=3)
        )

        # Display rep count, state, and current diff value.
        if CONFIG["show_labels"]:
            label = f"State: {rep_state}"
            cv2.putText(frame, label, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        if CONFIG["show_reps"]:
            cv2.putText(frame, f"Reps: {rep_count}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 100), 2)
        if diff is not None:
            cv2.putText(frame, f"Elbow-Shoulder Diff: {diff:.1f}px", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    cv2.imshow("Bench Press Tracker", frame)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()
