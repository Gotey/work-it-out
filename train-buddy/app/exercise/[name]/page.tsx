"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import Image from "next/image";

export default function ExercisePage() {
  const params = useParams();
  const exerciseName = decodeURIComponent(params.name as string);

  const [exercise, setExercise] = useState<any | null>(null);

  useEffect(() => {
    const plan = JSON.parse(localStorage.getItem("workoutPlan") || "{}");
    const found = plan.workouts
      ?.flatMap((w: any) => w.exercises)
      ?.find((e: any) => e.name === exerciseName);
    if (found) setExercise(found);
  }, [exerciseName]);

  const [currentSet, setCurrentSet] = useState(1);
  const [currentRep, setCurrentRep] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (exercise) {
      const totalReps = exercise.sets * exercise.reps;
      const completedReps = (currentSet - 1) * exercise.reps + currentRep;
      setProgress((completedReps / totalReps) * 100);
    }
  }, [currentSet, currentRep, exercise]);

  if (!exercise) return <div>Exercise not found</div>;

  return (
    <div className="container max-w-md mx-auto p-4">
      <Link href="/week1">
        <Button variant="outline" className="mb-4">
          ← Back to Day View
        </Button>
      </Link>
      <Card className="relative overflow-hidden">
        {/* Exercise GIF */}
        <div className="relative aspect-video w-full">
          <Image
            src={
              exercise.gif ? `/exercises/${exercise.gif}` : "/placeholder.svg"
            }
            alt={exercise.name}
            fill
            className="object-cover rounded-t-md"
          />
        </div>

        <CardContent className="p-4">
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
                  if (currentRep < exercise.reps) setCurrentRep(currentRep + 1);
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
            {currentSet === exercise.sets && currentRep === exercise.reps && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <Button
                  className="w-full"
                  size="lg"
                  onClick={() => alert("Exercise completed!")}
                >
                  Exercise Completed
                </Button>
              </motion.div>
            )}
          </AnimatePresence>
        </CardContent>
      </Card>
    </div>
  );
}
