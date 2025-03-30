"use client"

import { useEffect, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import Link from "next/link"
import { motion } from "framer-motion"

export default function Week1Page() {
  const [daysPerWeek, setDaysPerWeek] = useState(3)

  useEffect(() => {
    // Get user data from localStorage
    const userData = localStorage.getItem("userData")
    if (userData) {
      const { daysPerWeek } = JSON.parse(userData)
      setDaysPerWeek(daysPerWeek)
    }
  }, [])

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

  return (
    <div className="container max-w-md mx-auto p-4">
      <h1 className="text-2xl font-bold text-center mb-6">Week 1</h1>

      <motion.div className="grid gap-4" variants={container} initial="hidden" animate="show">
        {Array.from({ length: daysPerWeek }).map((_, index) => (
          <motion.div key={index} variants={item}>
            <Link href={`/week1/day${index + 1}`}>
              <Card className="hover:bg-muted/50 transition-colors">
                <CardContent className="p-4 flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-medium">Day {index + 1}</h2>
                    <p className="text-sm text-muted-foreground">
                      {index === 0
                        ? "Upper Body"
                        : index === 1
                          ? "Lower Body"
                          : index === 2
                            ? "Core & Cardio"
                            : index === 3
                              ? "Push Day"
                              : index === 4
                                ? "Pull Day"
                                : index === 5
                                  ? "Leg Day"
                                  : "Full Body"}
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
  )
}

