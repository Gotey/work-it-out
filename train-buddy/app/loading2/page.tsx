"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { generateWorkoutPlan } from "@/lib/api"; // <-- make sure you have this

const shakeColors = [
  "bg-red-400", // strawberry
  "bg-amber-800", // chocolate
  "bg-amber-200", // vanilla
];

export default function Loading2Page() {
  const router = useRouter();
  const [progress, setProgress] = useState(0);
  const [shakeColor, setShakeColor] = useState(
    shakeColors[Math.floor(Math.random() * shakeColors.length)]
  );

  useEffect(() => {
    const userData = JSON.parse(localStorage.getItem("userData") || "{}");

    // 🟣 Validate user data
    if (!userData || !userData.name || !userData.goal) {
      alert("Missing user data. Please fill out the form first.");
      router.push("/form");
      return;
    }

    // 🟣 Generate the workout plan automatically on mount
    generateWorkoutPlan(userData)
      .then((plan) => {
        localStorage.setItem("workoutPlan", JSON.stringify(plan));
        // Continue progress bar animation normally
        const interval = setInterval(() => {
          setProgress((prev) => {
            if (prev >= 100) {
              clearInterval(interval);
              setTimeout(() => router.push("/week1"), 500);
              return 100;
            }
            return prev + 1;
          });
        }, 30);
      })
      .catch((err) => {
        alert("Error generating plan: " + err.message);
        router.push("/form");
      });
  }, [router]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-4">
      <div className="w-full max-w-md flex flex-col items-center">
        <div className="relative w-40 h-64 mb-8">
          {/* Shaker container */}
          <motion.div
            className="absolute inset-0 bg-gray-200 rounded-md overflow-hidden"
            animate={{
              x: [0, -5, 5, -5, 0],
            }}
            transition={{
              repeat: Number.POSITIVE_INFINITY,
              duration: 0.5,
              repeatDelay: 1.5,
            }}
          >
            {/* Shaker lid */}
            <div className="absolute top-0 left-0 right-0 h-8 bg-gray-400 rounded-t-md"></div>

            {/* Shaker fill */}
            <motion.div
              className={`absolute bottom-0 left-0 right-0 ${shakeColor} transition-all duration-300 ease-in-out`}
              style={{ height: `${progress}%` }}
            ></motion.div>

            {/* Shaker measurement lines */}
            <div className="absolute inset-0 flex flex-col justify-between py-12 px-2">
              <div className="w-full h-px bg-gray-400"></div>
              <div className="w-full h-px bg-gray-400"></div>
              <div className="w-full h-px bg-gray-400"></div>
              <div className="w-full h-px bg-gray-400"></div>
            </div>
          </motion.div>
        </div>

        <p className="text-center">
          Loading and prepping your personalized workout...
        </p>
      </div>
    </div>
  );
}
