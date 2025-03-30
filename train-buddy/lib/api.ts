// lib/api.ts

import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:5000"; // Replace when deploying

export async function generateWorkoutPlan(userData: any) {
    try {
        const response = await axios.post(`${API_BASE_URL}/generate-plan`, userData);
        return response.data; // { schedule, workouts }
    } catch (error: any) {
        console.error("API Error:", error);
        throw new Error("Failed to generate workout plan. Please try again later.");
    }
}
