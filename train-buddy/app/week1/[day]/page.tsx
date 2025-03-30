"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { slugify } from "@/lib/slugify";

export default function DayPage() {
  const params = useParams();
  const dayIndex = Number(params.day) - 1;

  const [workout, setWorkout] = useState<any | null>(null);

  useEffect(() => {
    const plan = JSON.parse(localStorage.getItem("workoutPlan") || "{}");
    if (plan?.workouts?.[dayIndex]) {
      setWorkout(plan.workouts[dayIndex]);
    }
  }, [dayIndex]);

  if (!workout) return <div>Workout not found</div>;

  return (
    <div className="container max-w-md mx-auto p-4">
      <Link href="/week1">
        <Button variant="outline" className="mb-4">
          ← Back to Week Overview
        </Button>
      </Link>
      <h1 className="text-xl font-bold mb-4">{workout.day_name}</h1>

      <motion.div className="grid gap-4" initial="hidden" animate="show">
        {workout.exercises.map((exercise: any, i: number) => (
          <motion.div key={i}>
            <Link href={`/week1/${params.day}/${slugify(exercise.name)}`}>
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
