"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"
import { motion } from "framer-motion"
import confetti from "canvas-confetti"

export default function SuccessPage() {
  const [timeSpent, setTimeSpent] = useState("00:00")
  const [accuracy, setAccuracy] = useState(92)
  const [caloriesBurned, setCaloriesBurned] = useState(187)

  useEffect(() => {
    // Trigger confetti on load
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
    })

    // Calculate workout duration
    const durationInSeconds = Number.parseInt(localStorage.getItem("workoutDuration") || "0")
    if (durationInSeconds > 0) {
      const minutes = Math.floor(durationInSeconds / 60)
      const seconds = durationInSeconds % 60
      setTimeSpent(`${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`)
    }

    // Calculate calories based on user data and workout duration
    const userData = JSON.parse(localStorage.getItem("userData") || "{}")
    if (userData.weight && durationInSeconds) {
      // Simple calorie calculation based on weight and duration
      // This is a very simplified formula - real calorie burn depends on many factors
      const weight = Number.parseFloat(userData.weight)
      const weightInKg = userData.weightUnit === "lbs" ? weight * 0.453592 : weight
      const estimatedCalories = Math.round(((durationInSeconds / 60) * 5 * weightInKg) / 60)
      setCaloriesBurned(estimatedCalories)
    }
  }, [])

  return (
    <div className="container max-w-md mx-auto p-4 flex flex-col items-center justify-center min-h-[80vh]">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: "spring", stiffness: 300, damping: 20 }}
        className="w-full"
      >
        <Card>
          <CardHeader className="text-center">
            <motion.div initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.3 }}>
              <CardTitle className="text-3xl">Success!!!</CardTitle>
            </motion.div>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <motion.div initial={{ x: -20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: 0.5 }}>
                <div className="flex justify-between items-center border-b pb-2">
                  <span className="text-muted-foreground">Time Spent</span>
                  <span className="font-medium">{timeSpent}</span>
                </div>
              </motion.div>

              <motion.div initial={{ x: -20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: 0.7 }}>
                <div className="flex justify-between items-center border-b pb-2">
                  <span className="text-muted-foreground">Accuracy</span>
                  <span className="font-medium">{accuracy}%</span>
                </div>
              </motion.div>

              <motion.div initial={{ x: -20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: 0.9 }}>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Calories Burned</span>
                  <span className="font-medium">{caloriesBurned}</span>
                </div>
              </motion.div>

              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 1.1 }}
                className="pt-4"
              >
                <Link href="/hub">
                  <Button className="w-full">Return to Hub</Button>
                </Link>
              </motion.div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

