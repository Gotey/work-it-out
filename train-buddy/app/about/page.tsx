export default function AboutPage() {
  return (
    <div className="container max-w-3xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">About Train Buddy</h1>

      <div className="space-y-6">
        <p>
          Train Buddy is your personal workout companion designed to help you achieve your fitness goals. Whether you're
          looking to build muscle, increase strength, improve your health, or boost your endurance, Train Buddy provides
          personalized workout plans tailored to your specific needs.
        </p>

        <h2 className="text-2xl font-semibold">Our Mission</h2>
        <p>
          Our mission is to make fitness accessible to everyone, regardless of their experience level or available
          equipment. We believe that with the right guidance and motivation, anyone can transform their body and improve
          their health.
        </p>

        <h2 className="text-2xl font-semibold">Features</h2>
        <ul className="list-disc pl-6 space-y-2">
          <li>Personalized workout plans based on your goals and preferences</li>
          <li>Form checking using advanced camera technology</li>
          <li>Progress tracking to keep you motivated</li>
          <li>Exercise demonstrations to ensure proper form</li>
          <li>Adaptive workouts that evolve as you improve</li>
        </ul>

        <h2 className="text-2xl font-semibold">Our Team</h2>
        <p>
          Train Buddy was created by a team of fitness enthusiasts, certified personal trainers, and software developers
          who are passionate about helping people achieve their fitness goals.
        </p>
      </div>
    </div>
  )
}

