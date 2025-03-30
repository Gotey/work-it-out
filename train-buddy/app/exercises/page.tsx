"use client"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import Image from "next/image"
import Link from "next/link"

const allExercises = [
  { id: 1, name: "Push-ups", category: "upper", equipment: "bodyweight", gif: "/exercises/pushup.gif" },
  { id: 2, name: "Dumbbell Bench Press", category: "upper", equipment: "dumbbell", gif: "/exercises/bench-press.gif" },
  { id: 3, name: "Shoulder Press", category: "upper", equipment: "dumbbell", gif: "/exercises/shoulder-press.gif" },
  { id: 4, name: "Tricep Dips", category: "upper", equipment: "bodyweight", gif: "/exercises/tricep-dips.gif" },
  { id: 5, name: "Lateral Raises", category: "upper", equipment: "dumbbell", gif: "/exercises/lateral-raises.gif" },
  { id: 6, name: "Squats", category: "lower", equipment: "bodyweight", gif: "/exercises/squat.gif" },
  { id: 7, name: "Lunges", category: "lower", equipment: "bodyweight", gif: "/exercises/lunge.gif" },
  { id: 8, name: "Plank", category: "core", equipment: "bodyweight", gif: "/exercises/plank.gif" },
]

export default function ExercisesPage() {
  const [searchTerm, setSearchTerm] = useState("")

  const filteredExercises = allExercises.filter((exercise) =>
    exercise.name.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  return (
    <div className="container max-w-md mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Exercise Library</h1>

      <div className="mb-4">
        <Input
          placeholder="Search exercises..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full"
        />
      </div>

      <Tabs defaultValue="all">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="upper">Upper</TabsTrigger>
          <TabsTrigger value="lower">Lower</TabsTrigger>
          <TabsTrigger value="core">Core</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="mt-4">
          <div className="grid gap-4">
            {filteredExercises.map((exercise) => (
              <ExerciseCard key={exercise.id} exercise={exercise} />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="upper" className="mt-4">
          <div className="grid gap-4">
            {filteredExercises
              .filter((exercise) => exercise.category === "upper")
              .map((exercise) => (
                <ExerciseCard key={exercise.id} exercise={exercise} />
              ))}
          </div>
        </TabsContent>

        <TabsContent value="lower" className="mt-4">
          <div className="grid gap-4">
            {filteredExercises
              .filter((exercise) => exercise.category === "lower")
              .map((exercise) => (
                <ExerciseCard key={exercise.id} exercise={exercise} />
              ))}
          </div>
        </TabsContent>

        <TabsContent value="core" className="mt-4">
          <div className="grid gap-4">
            {filteredExercises
              .filter((exercise) => exercise.category === "core")
              .map((exercise) => (
                <ExerciseCard key={exercise.id} exercise={exercise} />
              ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

function ExerciseCard({ exercise }: { exercise: any }) {
  return (
    <Link href={`/exercise/${exercise.id}`}>
      <Card className="overflow-hidden hover:bg-muted/50 transition-colors">
        <CardContent className="p-0">
          <div className="relative h-40 w-full">
            <Image src={exercise.gif || "/placeholder.svg"} alt={exercise.name} fill className="object-cover" />
          </div>
          <div className="p-4">
            <h3 className="font-medium">{exercise.name}</h3>
            <div className="flex gap-2 mt-1">
              <span className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
                {exercise.category}
              </span>
              <span className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
                {exercise.equipment}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}

