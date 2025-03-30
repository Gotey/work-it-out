"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import Image from "next/image";
import {
  markExerciseCompleted,
  isExerciseCompleted,
  isDayCompleted,
} from "@/lib/progress";
import { slugify } from "@/lib/slugify";

export default function ExercisePage() {
  const { day, name } = useParams() as { day: string; name: string };
  const router = useRouter();

  const [exercise, setExercise] = useState<any | null>(null);
  const [currentSet, setCurrentSet] = useState(1);
  const [currentRep, setCurrentRep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);
  const [started, setStarted] = useState(false);

  useEffect(() => {
    const plan = JSON.parse(localStorage.getItem("workoutPlan") || "{}");
    const found = plan.workouts?.[parseInt(day) - 1]?.exercises?.find(
      (e: any) => slugify(e.name) === decodeURIComponent(name)
    );
    if (found) setExercise(found);

    setIsCompleted(isExerciseCompleted(Number(day), name));
  }, [day, name]);

  useEffect(() => {
    if (exercise) {
      const totalReps = exercise.sets * exercise.reps;
      const completedReps = (currentSet - 1) * exercise.reps + currentRep;
      setProgress((completedReps / totalReps) * 100);
    }
  }, [currentSet, currentRep, exercise]);

  const handleComplete = () => {
    const dayIndex = Number(day);
    markExerciseCompleted(dayIndex, name);
    if (isDayCompleted(dayIndex)) {
      router.push("/success");
    } else {
      router.push(`/week1/${day}`);
    }
  };

  const startExercise = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/start-exercise", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ exercise: exercise?.name }),
      });
      await res.json();
      setStarted(true);
      setTimeout(() => setStarted(false), 3000);
    } catch (err) {
      console.error("Error starting exercise:", err);
    }
  };

  if (!exercise) return <div>Exercise not found</div>;

  return (
    <div className="container max-w-md mx-auto p-4">
      <Link href={`/week1/${day}`}>
        <Button variant="outline" className="mb-4">
          ← Back to Day
        </Button>
      </Link>

      <Card className="relative overflow-hidden">
        {/* Enlarged Exercise Container */}
        <div className="exercise-card relative aspect-[16/9] w-full min-h-[250px]">
          <Image
            src={
              exercise.gif ? `/exercises/${exercise.gif}` : "/placeholder.svg"
            }
            alt={exercise.name}
            fill
            className="object-cover rounded-t-md"
          />
        </div>

        {/* Camera Popup */}
        <AnimatePresence>
          {started && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute bottom-2 left-1/2 -translate-x-1/2 bg-green-500 text-white text-sm px-4 py-2 rounded shadow"
            >
              Exercise script started via Flask!
            </motion.div>
          )}
        </AnimatePresence>

        <CardContent className="p-4">
          {/* Exercise Title + Camera */}
          <div className="flex justify-between items-center mb-2">
            <h1 className="text-xl font-bold">{exercise.name}</h1>
            {/* Camera Button */}
            <Button
              variant="outline"
              size="icon"
              onClick={startExercise}
              className="camera-button"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="lucide lucide-camera"
              >
                <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z" />
                <circle cx="12" cy="13" r="3" />
              </svg>
              <span className="sr-only">Start Camera</span>
            </Button>

            {/* Popup */}
            <AnimatePresence>
              {started && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="camera-toast absolute bottom-4 left-1/2 -translate-x-1/2"
                >
                  Exercise script started via Flask!
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {isCompleted ? (
            <p className="text-green-500 font-semibold">Completed ✅</p>
          ) : (
            <>
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
                    onClick={() => setCurrentRep(Math.max(0, currentRep - 1))}
                    disabled={currentSet === 1 && currentRep === 0}
                  >
                    -
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
                    onClick={() => {
                      if (currentRep < exercise.reps)
                        setCurrentRep(currentRep + 1);
                      else if (currentSet < exercise.sets) {
                        setCurrentSet(currentSet + 1);
                        setCurrentRep(1);
                      }
                    }}
                  >
                    +
                  </Button>
                </div>
              </div>
              <AnimatePresence>
                {currentSet === exercise.sets &&
                  currentRep === exercise.reps && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                    >
                      <Button
                        className="w-full"
                        size="lg"
                        onClick={handleComplete}
                      >
                        Exercise Completed
                      </Button>
                    </motion.div>
                  )}
              </AnimatePresence>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
