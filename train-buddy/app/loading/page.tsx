"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"

const workoutTips = [
  "Remember to breathe during your exercises.",
  "Stay hydrated throughout your workout.",
  "Proper form is more important than weight or reps.",
  "Rest days are just as important as workout days.",
  "Warm up before and cool down after your workout.",
  "Progressive overload is key to building strength.",
  "Listen to your body and avoid pushing through pain.",
  "Consistency beats intensity for long-term results.",
]

const shakeColors = [
  "bg-red-400", // strawberry
  "bg-amber-800", // chocolate
  "bg-amber-200", // vanilla
]

export default function LoadingPage() {
  const router = useRouter()
  const [progress, setProgress] = useState(0)
  const [tipIndex, setTipIndex] = useState(0)
  const [shakeColor, setShakeColor] = useState(shakeColors[Math.floor(Math.random() * shakeColors.length)])

  useEffect(() => {
    // Clear any previous workout data
    localStorage.removeItem("workoutStartTime")
    localStorage.removeItem("workoutDuration")

    // Rotate through tips
    const tipInterval = setInterval(() => {
      setTipIndex((prev) => (prev + 1) % workoutTips.length)
    }, 3000)

    // Progress the loading
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(progressInterval)
          clearInterval(tipInterval)
          setTimeout(() => router.push("/form"), 500)
          return 100
        }
        return prev + 1
      })
    }, 50)

    return () => {
      clearInterval(tipInterval)
      clearInterval(progressInterval)
    }
  }, [router])

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

        <div className="text-center animate-pulse">
          <p className="text-lg font-medium mb-2">Loading your workout...</p>
          <p className="text-sm text-muted-foreground">{workoutTips[tipIndex]}</p>
        </div>
      </div>
    </div>
  )
}

