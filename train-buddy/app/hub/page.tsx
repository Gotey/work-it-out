"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Calendar, BarChart3, Settings, User } from "lucide-react"
import Link from "next/link"
import { useTheme } from "next-themes"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"

export default function HubPage() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)
  const [userData, setUserData] = useState<any>(null)

  useEffect(() => {
    setMounted(true)
    const data = localStorage.getItem("userData")
    if (data) {
      setUserData(JSON.parse(data))
    }
  }, [])

  if (!mounted) return null

  return (
    <div className="container max-w-md mx-auto p-4">
      <div className="flex flex-col items-center mb-6">
        <div className="w-24 h-24 rounded-full bg-muted flex items-center justify-center mb-2">
          <User className="h-12 w-12 text-muted-foreground" />
        </div>
        <h2 className="text-xl font-bold">{userData?.name || "User"}</h2>
        <p className="text-sm text-muted-foreground">
          {userData?.goal === "strength"
            ? "Strength Training"
            : userData?.goal === "muscle"
              ? "Muscle Building"
              : userData?.goal === "health"
                ? "Health & Fitness"
                : userData?.goal === "endurance"
                  ? "Endurance Training"
                  : "Custom Program"}
        </p>
      </div>

      <Tabs defaultValue="calendar" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="calendar">
            <Calendar className="h-4 w-4 mr-2" />
            Calendar
          </TabsTrigger>
          <TabsTrigger value="stats">
            <BarChart3 className="h-4 w-4 mr-2" />
            Stats
          </TabsTrigger>
          <TabsTrigger value="settings">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </TabsTrigger>
        </TabsList>

        <TabsContent value="calendar" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Your Workout Plan</CardTitle>
            </CardHeader>
            <CardContent>
              <Link href="/week1">
                <Button className="w-full">Continue Week 1</Button>
              </Link>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="stats" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Your Progress</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Workouts Completed</span>
                    <span className="font-medium">2/7</span>
                  </div>
                  <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                    <div className="bg-primary h-full" style={{ width: "28.5%" }}></div>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Weekly Goal</span>
                    <span className="font-medium">{userData?.daysPerWeek || 3} days</span>
                  </div>
                  <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                    <div className="bg-primary h-full" style={{ width: "28.5%" }}></div>
                  </div>
                </div>

                <div className="pt-4">
                  <p className="text-sm text-muted-foreground text-center">
                    Complete more workouts to see detailed statistics
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Settings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="theme-mode">Dark Mode</Label>
                  <Switch
                    id="theme-mode"
                    checked={theme === "dark"}
                    onCheckedChange={(checked) => setTheme(checked ? "dark" : "light")}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <Label htmlFor="notifications">Notifications</Label>
                  <Switch id="notifications" />
                </div>

                <div className="flex items-center justify-between">
                  <Label htmlFor="sound">Sound Effects</Label>
                  <Switch id="sound" />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

