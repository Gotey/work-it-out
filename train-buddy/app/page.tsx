import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { ChevronRight } from "lucide-react";
import ExerciseCarousel from "@/components/exercise-carousel";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center">
      <div className="container flex flex-col items-center justify-center px-4 py-8 space-y-8">
        <div className="flex flex-col items-center justify-center space-y-4 text-center">
          <Image
            src="/logo-removebg-preview.png"
            alt="Train Buddy Logo"
            width={300}
            height={300}
            className="animate-pulse"
            priority
          />
          <p className="max-w-[42rem] text-muted-foreground sm:text-xl">
            Your personal workout companion. Get fit, stay motivated, and track
            your progress.
          </p>
          <Link href="/loading" className="w-full sm:w-auto">
            <Button size="lg" className="w-full sm:w-auto animate-pulse">
              Start Workout
            </Button>
          </Link>
        </div>

        <div className="w-full max-w-3xl">
          <h2 className="text-xl font-semibold mb-4 text-center">
            Featured Exercises
          </h2>
          <ExerciseCarousel />
        </div>

        <Link href="/exercises" className="w-full max-w-md">
          <Button
            variant="outline"
            className="w-full flex items-center justify-between"
          >
            <span>Browse all the exercises</span>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </Link>
      </div>
    </main>
  );
}
