"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { Card, CardContent } from "@/components/ui/card"
import { useEffect } from "react"

const exercises = [
  { id: 1, name: "Push-ups", sets: 3, reps: 10 },
  { id: 2, name: "Dumbbell Bench Press", sets: 3, reps: 12 },
  { id: 3, name: "Shoulder Press", sets: 3, reps: 10 },
  { id: 4, name: "Tricep Dips", sets: 3, reps: 12 },
  { id: 5, name: "Lateral Raises", sets: 3, reps: 15 },
]

export default function Day1Page() {
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 },
  }

  useEffect(() => {
    // Reset workout timer when starting a new workout day
    localStorage.removeItem("workoutStartTime")
    localStorage.removeItem("workoutDuration")
  }, [])

  return (
    <div className="container max-w-md mx-auto p-4">
      <motion.div className="grid gap-4" variants={container} initial="hidden" animate="show">
        {exercises.map((exercise) => (
          <motion.div key={exercise.id} variants={item}>
            <Link href={`/exercise/${exercise.id}`}>
              <Card className="hover:bg-muted/50 transition-colors">
                <CardContent className="p-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-medium">{exercise.name}</h3>
                      <p className="text-sm text-muted-foreground">
                        {exercise.sets} sets × {exercise.reps} reps
                      </p>
                    </div>
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="lucide lucide-chevron-right"
                    >
                      <path d="m9 18 6-6-6-6" />
                    </svg>
                  </div>
                </CardContent>
              </Card>
            </Link>
          </motion.div>
        ))}
      </motion.div>
    </div>
  )
}

