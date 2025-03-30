"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Slider } from "@/components/ui/slider"
import { Card, CardContent } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

type FormData = {
  name: string
  dob: string
  sex: "male" | "female"
  weight: string
  weightUnit: "kg" | "lbs"
  daysPerWeek: number
  goal: string
}

const validateAge = (dob: string): boolean => {
  if (!dob) return false

  const birthDate = new Date(dob)
  const today = new Date()

  let age = today.getFullYear() - birthDate.getFullYear()
  const monthDiff = today.getMonth() - birthDate.getMonth()

  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--
  }

  return age >= 18
}

export default function FormPage() {
  const router = useRouter()
  const [step, setStep] = useState(0)
  const [formData, setFormData] = useState<FormData>({
    name: "",
    dob: "",
    sex: "male",
    weight: "",
    weightUnit: "kg",
    daysPerWeek: 3,
    goal: "",
  })

  const [dobError, setDobError] = useState<string | null>(null)

  const totalSteps = 6
  const progress = ((step + 1) / totalSteps) * 100

  const handleNext = () => {
    if (step === 1) {
      // Validate age when on the DOB step
      if (!validateAge(formData.dob)) {
        setDobError("You must be at least 18 years old to use this app")
        return
      } else {
        setDobError(null)
      }
    }

    if (step < totalSteps - 1) {
      setStep(step + 1)
    } else {
      // Save form data to localStorage
      localStorage.setItem("userData", JSON.stringify(formData))
      router.push("/loading2")
    }
  }

  const updateFormData = (field: keyof FormData, value: any) => {
    setFormData({ ...formData, [field]: value })
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardContent className="pt-6">
          {/* Progress bar */}
          <div className="w-full h-2 bg-muted rounded-full mb-8 overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-300 ease-in-out"
              style={{ width: `${progress}%` }}
            ></div>
          </div>

          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="min-h-[300px] flex flex-col"
            >
              {step === 0 && (
                <div className="space-y-4 flex-1">
                  <h2 className="text-xl font-semibold">What's your name?</h2>
                  <div className="space-y-2">
                    <Label htmlFor="name">Name</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => updateFormData("name", e.target.value)}
                      placeholder="Enter your name"
                    />
                  </div>
                </div>
              )}

              {step === 1 && (
                <div className="space-y-4 flex-1">
                  <h2 className="text-xl font-semibold">When were you born?</h2>
                  <div className="space-y-2">
                    <Label htmlFor="dob">Date of Birth</Label>
                    <Input
                      id="dob"
                      type="date"
                      value={formData.dob}
                      onChange={(e) => {
                        updateFormData("dob", e.target.value)
                        if (dobError) setDobError(null)
                      }}
                      className={dobError ? "border-red-500" : ""}
                    />
                    {dobError && <p className="text-sm text-red-500">{dobError}</p>}
                  </div>
                </div>
              )}

              {step === 2 && (
                <div className="space-y-4 flex-1">
                  <h2 className="text-xl font-semibold">What's your sex?</h2>
                  <RadioGroup
                    value={formData.sex}
                    onValueChange={(value) => updateFormData("sex", value as "male" | "female")}
                    className="flex flex-col space-y-2"
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="male" id="male" />
                      <Label htmlFor="male">Male</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="female" id="female" />
                      <Label htmlFor="female">Female</Label>
                    </div>
                  </RadioGroup>
                </div>
              )}

              {step === 3 && (
                <div className="space-y-4 flex-1">
                  <h2 className="text-xl font-semibold">What's your weight?</h2>
                  <div className="flex space-x-2">
                    <div className="flex-1">
                      <Label htmlFor="weight">Weight</Label>
                      <Input
                        id="weight"
                        type="number"
                        min="0"
                        step="0.1"
                        value={formData.weight}
                        onChange={(e) => updateFormData("weight", e.target.value)}
                        placeholder="Enter your weight"
                      />
                    </div>
                    <div className="w-24">
                      <Label htmlFor="weightUnit">Unit</Label>
                      <Select
                        value={formData.weightUnit}
                        onValueChange={(value) => updateFormData("weightUnit", value as "kg" | "lbs")}
                      >
                        <SelectTrigger id="weightUnit">
                          <SelectValue placeholder="Unit" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="kg">kg</SelectItem>
                          <SelectItem value="lbs">lbs</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>
              )}

              {step === 4 && (
                <div className="space-y-4 flex-1">
                  <h2 className="text-xl font-semibold">How many days per week?</h2>
                  <div className="space-y-6">
                    <div>
                      <div className="flex justify-between mb-2">
                        <Label>Days per week: {formData.daysPerWeek}</Label>
                      </div>
                      <Slider
                        value={[formData.daysPerWeek]}
                        min={1}
                        max={7}
                        step={1}
                        onValueChange={(value) => updateFormData("daysPerWeek", value[0])}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>1</span>
                      <span>2</span>
                      <span>3</span>
                      <span>4</span>
                      <span>5</span>
                      <span>6</span>
                      <span>7</span>
                    </div>
                  </div>
                </div>
              )}

              {step === 5 && (
                <div className="space-y-4 flex-1">
                  <h2 className="text-xl font-semibold">What's your goal?</h2>
                  <RadioGroup
                    value={formData.goal}
                    onValueChange={(value) => updateFormData("goal", value)}
                    className="flex flex-col space-y-2"
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="strength" id="strength" />
                      <Label htmlFor="strength">Increase Strength</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="muscle" id="muscle" />
                      <Label htmlFor="muscle">Build Muscle</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="health" id="health" />
                      <Label htmlFor="health">Better Health & Fitness</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="endurance" id="endurance" />
                      <Label htmlFor="endurance">Increase Endurance</Label>
                    </div>
                  </RadioGroup>
                </div>
              )}
            </motion.div>
          </AnimatePresence>

          <div className="mt-8 flex justify-end">
            <Button
              onClick={handleNext}
              disabled={
                (step === 0 && !formData.name) ||
                (step === 1 && !formData.dob) ||
                (step === 3 && !formData.weight) ||
                (step === 5 && !formData.goal)
              }
            >
              {step === totalSteps - 1 ? "Submit" : "Continue"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

