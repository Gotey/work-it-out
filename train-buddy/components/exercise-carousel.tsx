"use client"

import { useState, useEffect } from "react"
import Image from "next/image"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"

const exercises = [
  { id: 1, name: "Push-ups", gif: "/exercises/pushup.gif" },
  { id: 2, name: "Squats", gif: "/exercises/squat.gif" },
  { id: 3, name: "Lunges", gif: "/exercises/lunge.gif" },
  { id: 4, name: "Plank", gif: "/exercises/plank.gif" },
]

export default function ExerciseCarousel() {
  const [current, setCurrent] = useState(0)

  const next = () => setCurrent((current + 1) % exercises.length)
  const prev = () => setCurrent((current - 1 + exercises.length) % exercises.length)

  // Auto-advance carousel
  useEffect(() => {
    const timer = setTimeout(next, 5000)
    return () => clearTimeout(timer)
  }, [current])

  return (
    <div className="relative w-full">
      <div className="overflow-hidden rounded-lg">
        <div
          className="flex transition-transform duration-500 ease-in-out"
          style={{ transform: `translateX(-${current * 100}%)` }}
        >
          {exercises.map((exercise) => (
            <Card key={exercise.id} className="w-full flex-shrink-0">
              <CardContent className="p-0">
                <div className="relative aspect-video w-full overflow-hidden rounded-t-lg">
                  <Image src={exercise.gif || "/placeholder.svg"} alt={exercise.name} fill className="object-cover" />
                </div>
                <div className="p-4 text-center">
                  <h3 className="font-medium">{exercise.name}</h3>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <Button
        variant="outline"
        size="icon"
        className="absolute left-2 top-1/2 z-10 -translate-y-1/2 rounded-full bg-background/80 backdrop-blur"
        onClick={prev}
      >
        <ChevronLeft className="h-4 w-4" />
        <span className="sr-only">Previous slide</span>
      </Button>

      <Button
        variant="outline"
        size="icon"
        className="absolute right-2 top-1/2 z-10 -translate-y-1/2 rounded-full bg-background/80 backdrop-blur"
        onClick={next}
      >
        <ChevronRight className="h-4 w-4" />
        <span className="sr-only">Next slide</span>
      </Button>

      <div className="mt-2 flex justify-center gap-1">
        {exercises.map((_, index) => (
          <Button
            key={index}
            variant="ghost"
            size="icon"
            className={`h-2 w-2 rounded-full p-0 ${index === current ? "bg-primary" : "bg-muted"}`}
            onClick={() => setCurrent(index)}
          >
            <span className="sr-only">Go to slide {index + 1}</span>
          </Button>
        ))}
      </div>
    </div>
  )
}

