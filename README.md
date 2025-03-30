# TrainBuddy

**TrainBuddy** is a personal fitness companion that generates dynamic workout plans and uses real-time pose tracking to monitor your form and count reps — all from your browser.

## 🧠 Overview

TrainBuddy bridges the gap between workout planning and execution. Using AI, it builds a personalized fitness plan. Then, through real-time computer vision, it tracks your form via webcam and counts your reps — offering both guidance and accountability.

---

## 🚀 Features

- AI-Generated Workout Plans – Input your preferences and let GPT create a full week’s routine for push, pull, and core days.
- Exercise Library – Clean UI with GIFs for visual reference across upper, lower, and core categories.
- Dynamic Routing – Each exercise has its own dedicated page based on your plan.
- Real-Time Form Tracking – Uses MediaPipe + OpenCV to detect your pose, track reps, and validate movement.
- Automatic Script Triggering – Pressing the camera icon launches the correct Python tracking script for that exercise.
- Feedback Pop-up – Clear notification that pose tracking has started.
- Rep Counting Logic – Custom thresholds and state machines to detect complete reps based on keypoint motion.

---

## 🎯 How It Works

1. **Frontend** (React/Next.js):
   - Collects user input for workout goals.
   - Displays the exercise plan with individual pages for each activity.
   - Camera icon on each exercise page sends a request to the Flask backend.

2. **Backend** (Flask):
   - Receives requests from frontend.
   - Matches the exercise name with the appropriate Python tracking script using a lookup table.
   - Runs the script in a separate process and opens a webcam window for pose tracking.

3. **Tracking Scripts** (Python + MediaPipe):
   - Detects human pose from the webcam feed.
   - Monitors specific joints (like shoulder and elbow) for movement.
   - Counts reps based on motion thresholds and timing logic.

---

## 🧰 Built With

- Next.js / React
- Python + Flask
- MediaPipe (Pose Detection)
- TensorFlow
- Framer Motion (UI animations)
- OpenCV
- Vercel (Frontend deployment)
- Ngrok (for local Flask tunneling)
- JSON-based GPT output
- Windows Subprocess Handling

---

## 📸 Demo

Coming soon...

---

## 📂 Project Structure

```
work-it-out/
├── app/                  # Next.js frontend app
│   ├── exercise/[name]/  # Dynamic route for each exercise page
│   └── week1/            # Workout days structure
├── exercise_tracking/    # Python pose tracking scripts (one per exercise)
├── workout_generation/   # Flask backend with app.py and GPT logic
```

---

## 🙌 Credits

Built during HackPSU by Javier Pozo Miranda.
