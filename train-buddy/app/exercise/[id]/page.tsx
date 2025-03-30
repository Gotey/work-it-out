"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { motion, AnimatePresence } from "framer-motion"

const exercises = [
  { id: 1, name: "Push-ups", sets: 3, reps: 10, gif: "/exercises/pushup.gif" },
  { id: 2, name: "Dumbbell Bench Press", sets: 3, reps: 12, gif: "/exercises/bench-press.gif" },
  { id: 3, name: "Shoulder Press", sets: 3, reps: 10, gif: "/exercises/shoulder-press.gif" },
  { id: 4, name: "Tricep Dips", sets: 3, reps: 12, gif: "/exercises/tricep-dips.gif" },
  { id: 5, name: "Lateral Raises", sets: 3, reps: 15, gif: "/exercises/lateral-raises.gif" },
]

export default function ExercisePage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const id = Number.parseInt(params.id)
  const exercise = exercises.find((ex) => ex.id === id)

  const [currentSet, setCurrentSet] = useState(1)
  const [currentRep, setCurrentRep] = useState(0)
  const [progress, setProgress] = useState(0)

  const resetCounters = () => {
    setCurrentSet(1)
    setCurrentRep(0)
  }

  useEffect(() => {
    // Reset counters when navigating to a new exercise
    resetCounters()

    // Start workout timer if this is the first exercise
    if (id === 1) {
      localStorage.setItem("workoutStartTime", new Date().toString())
    }
  }, [id])

  useEffect(() => {
    // Calculate progress percentage
    if (exercise) {
      const totalReps = exercise.sets * exercise.reps
      const completedReps = (currentSet - 1) * exercise.reps + currentRep
      setProgress((completedReps / totalReps) * 100)
    }
  }, [currentSet, currentRep, exercise])

  const incrementRep = () => {
    if (!exercise) return

    if (currentRep < exercise.reps) {
      setCurrentRep(currentRep + 1)
    } else {
      if (currentSet < exercise.sets) {
        setCurrentSet(currentSet + 1)
        setCurrentRep(1)
      }
    }
  }

  const decrementRep = () => {
    if (currentRep > 0) {
      setCurrentRep(currentRep - 1)
    } else {
      if (currentSet > 1) {
        setCurrentSet(currentSet - 1)
        setCurrentRep(exercise?.reps || 0)
      }
    }
  }

  const handleComplete = () => {
    // In a real app, you would save the progress
    const nextExerciseId = id + 1

    // Reset counters before navigating
    resetCounters()

    if (exercises.find((ex) => ex.id === nextExerciseId)) {
      router.push(`/exercise/${nextExerciseId}`)
    } else {
      // Save workout duration before navigating to success page
      const endTime = new Date()
      const startTime = new Date(localStorage.getItem("workoutStartTime") || endTime)
      const duration = Math.floor((endTime.getTime() - startTime.getTime()) / 1000) // in seconds

      localStorage.setItem("workoutDuration", duration.toString())
      router.push("/success")
    }
  }

  if (!exercise) {
    return <div className="container p-4">Exercise not found</div>
  }

  return (
    <div className="container max-w-md mx-auto p-4">
      <Card className="relative overflow-hidden">
        <div
          className="absolute bottom-0 left-0 h-1 bg-green-500 transition-all duration-300 ease-in-out"
          style={{ width: `${progress}%` }}
        ></div>

        <CardContent className="p-0">
          <div className="relative aspect-video w-full">
            <Image src={exercise.gif || "/placeholder.svg"} alt={exercise.name} fill className="object-cover" />
          </div>

          <div className="p-4">
            <h1 className="text-xl font-bold mb-2">{exercise.name}</h1>

            <div className="flex justify-between items-center mb-4">
              <div>
                <span className="text-xs text-muted-foreground">Sets</span>
                <div className="text-lg font-medium">
                  {currentSet} / {exercise.sets}
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={decrementRep}
                  disabled={currentSet === 1 && currentRep === 0}
                >
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
                    className="lucide lucide-minus"
                  >
                    <path d="M5 12h14" />
                  </svg>
                  <span className="sr-only">Decrease</span>
                </Button>

                <div className="text-center">
                  <span className="text-xs text-muted-foreground">Rep</span>
                  <div className="text-lg font-medium">
                    {currentRep} / {exercise.reps}
                  </div>
                </div>

                <Button
                  variant="outline"
                  size="icon"
                  onClick={incrementRep}
                  disabled={currentSet === exercise.sets && currentRep === exercise.reps}
                >
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
                    className="lucide lucide-plus"
                  >
                    <path d="M5 12h14" />
                    <path d="M12 5v14" />
                  </svg>
                  <span className="sr-only">Increase</span>
                </Button>
              </div>
            </div>

            <AnimatePresence>
              {currentSet === exercise.sets && currentRep === exercise.reps && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                >
                  <Button className="w-full" size="lg" onClick={handleComplete}>
                    Exercise Completed
                  </Button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

