"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { isDayCompleted } from "@/lib/progress";

export default function WeekPage() {
  const [workouts, setWorkouts] = useState<any[]>([]);

  useEffect(() => {
    const plan = JSON.parse(localStorage.getItem("workoutPlan") || "{}");
    if (plan?.workouts) setWorkouts(plan.workouts);
  }, []);

  return (
    <div className="container max-w-md mx-auto p-4">
      <h1 className="text-2xl font-bold text-center mb-6">Week 1</h1>

      <motion.div className="grid gap-4" initial="hidden" animate="show">
        {workouts.map((workout, index) => {
          const completed = isDayCompleted(index + 1);

          return (
            <motion.div key={index}>
              <Link href={`/week1/${index + 1}`}>
                <Card
                  className={`transition-colors ${
                    completed ? "bg-green-100" : "bg-white"
                  } hover:bg-muted/50`}
                >
                  <CardContent className="p-4 flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-medium">Day {index + 1}</h2>
                      <p className="text-sm text-muted-foreground">
                        {workout.day_name}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          );
        })}
      </motion.div>
    </div>
  );
}
