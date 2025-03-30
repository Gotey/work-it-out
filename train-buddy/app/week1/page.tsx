"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";

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
        {workouts.map((workout, index) => (
          <motion.div key={index}>
            <Link href={`/week1/${index + 1}`}>
              <Card className="hover:bg-muted/50 transition-colors">
                <CardContent className="p-4 flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-medium">Day {index + 1}</h2>
                    <p className="text-sm text-muted-foreground">
                      {workout.day_name}
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
