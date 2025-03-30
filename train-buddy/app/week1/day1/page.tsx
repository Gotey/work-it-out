"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";

export default function DayPage() {
  const params = useParams();
  const dayIndex = Number(params.id) - 1; // <-- you will route like /week1/day1, /week1/day2

  const [workout, setWorkout] = useState<any | null>(null);

  useEffect(() => {
    const plan = JSON.parse(localStorage.getItem("workoutPlan") || "{}");
    if (plan && plan.workouts && plan.workouts[dayIndex]) {
      setWorkout(plan.workouts[dayIndex]);
    }
  }, [dayIndex]);

  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } },
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 },
  };

  if (!workout) return <div className="p-4">Workout not found</div>;

  return (
    <div className="container max-w-md mx-auto p-4">
      <h1 className="text-xl font-bold mb-4">{workout.name}</h1>

      <motion.div
        className="grid gap-4"
        variants={container}
        initial="hidden"
        animate="show"
      >
        {workout.exercises.map((exercise: any, index: number) => (
          <motion.div key={index} variants={item}>
            <Link href={`/exercise/${exercise.name}`}>
              <Card className="hover:bg-muted/50 transition-colors">
                <CardContent className="p-4 flex justify-between items-center">
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
                </CardContent>
              </Card>
            </Link>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
