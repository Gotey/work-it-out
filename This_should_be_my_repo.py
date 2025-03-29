import cv2
import mediapipe as mp
import math

# === CONFIGURABLE OPTIONS ===
CONFIG = {
    "show_distances": True,
    "show_rotation": True,
    "show_z_depth": False,
    "show_visibility": False
}

# === Setup Pose ===
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, model_complexity=2)

# === Keypoint indices ===
LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12
LEFT_ELBOW = 13
RIGHT_ELBOW = 14
LEFT_HIP = 23
RIGHT_HIP = 24
LEFT_KNEE = 25
RIGHT_KNEE = 26

# === Utility Functions ===

def to_pixel(lm, w, h):
    return int(lm.x * w), int(lm.y * h)

def calc_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def calc_angle(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    angle = math.degrees(math.atan2(dy, dx))
    return angle

# === Pose Classifier ===

def classify_pose(landmarks, h, w):
    ls = to_pixel(landmarks[LEFT_SHOULDER], w, h)
    rs = to_pixel(landmarks[RIGHT_SHOULDER], w, h)
    le = to_pixel(landmarks[LEFT_ELBOW], w, h)
    re = to_pixel(landmarks[RIGHT_ELBOW], w, h)
    lh = to_pixel(landmarks[LEFT_HIP], w, h)
    rh = to_pixel(landmarks[RIGHT_HIP], w, h)
    lk = to_pixel(landmarks[LEFT_KNEE], w, h)
    rk = to_pixel(landmarks[RIGHT_KNEE], w, h)

    arms_horizontal = abs(ls[1] - le[1]) < 40 and abs(rs[1] - re[1]) < 40
    knees_near_hips = abs(lk[1] - lh[1]) < 60 and abs(rk[1] - rh[1]) < 60

    if arms_horizontal:
        return "T-POSE"
    elif knees_near_hips:
        return "SITTING"
    else:
        return "UNKNOWN"


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

        # === Draw Skeleton ===
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 0), thickness=2, circle_radius=6),
            connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=4, circle_radius=2)
        )

        # === Classify Pose ===
        label = classify_pose(landmarks, h, w)
        cv2.putText(frame, f"Pose: {label}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

        # === Optional Overlays ===
        ls_pixel = to_pixel(landmarks[LEFT_SHOULDER], w, h)
        rs_pixel = to_pixel(landmarks[RIGHT_SHOULDER], w, h)

        if CONFIG["show_distances"]:
            distance = calc_distance(ls_pixel, rs_pixel)
            cv2.putText(frame, f"Shoulder Dist: {int(distance)}px", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        if CONFIG["show_rotation"]:
            angle = calc_angle(rs_pixel, ls_pixel)
            cv2.putText(frame, f"Rotation Angle: {int(angle)}°", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)

        if CONFIG["show_z_depth"]:
            z_ls = landmarks[LEFT_SHOULDER].z
            z_rs = landmarks[RIGHT_SHOULDER].z
            cv2.putText(frame, f"Z-LS: {z_ls:.2f}  Z-RS: {z_rs:.2f}", (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 100, 255), 2)

        if CONFIG["show_visibility"]:
            vis_ls = landmarks[LEFT_SHOULDER].visibility
            vis_rs = landmarks[RIGHT_SHOULDER].visibility
            cv2.putText(frame, f"Vis-LS: {vis_ls:.2f}  Vis-RS: {vis_rs:.2f}", (30, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.imshow("Pose Classification", frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()
