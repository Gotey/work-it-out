export function isDayCompleted(day: number) {
    const plan = JSON.parse(localStorage.getItem("workoutPlan") || "{}");
    const completed = JSON.parse(localStorage.getItem("completedExercises") || "{}");
  
    const exercises = plan.workouts?.[day - 1]?.exercises || [];
    const completedList = completed[day] || [];
  
    return exercises.length > 0 && completedList.length === exercises.length;
}
  
export function isWeekCompleted() {
    const plan = JSON.parse(localStorage.getItem("workoutPlan") || "{}") || {};
    const totalDays = plan.workouts?.length || 0;
  
    for (let day = 1; day <= totalDays; day++) {
      if (!isDayCompleted(day)) return false;
    }
    return true;
  }

  // Add this at the top with the existing code
export function isExerciseCompleted(day: string | number, exerciseName: string) {
  const completed = JSON.parse(localStorage.getItem("completedExercises") || "{}");
  return completed[day]?.includes(exerciseName) || false;
}

export function markExerciseCompleted(day: string | number, exerciseName: string) {
  const completed = JSON.parse(localStorage.getItem("completedExercises") || "{}");
  if (!completed[day]) completed[day] = [];
  if (!completed[day].includes(exerciseName)) completed[day].push(exerciseName);
  localStorage.setItem("completedExercises", JSON.stringify(completed));
}
