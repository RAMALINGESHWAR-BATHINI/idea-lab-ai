import { Link } from "react-router-dom";

export function Home() {
  const features = [
    {
      title: "Event Management",
      description: "Create, schedule, and manage IdeaLab events, workshops, and hackathons.",
      icon: "📅",
    },
    {
      title: "Project Showcase",
      description: "Browse student projects, view prototypes, and track development milestones.",
      icon: "🚀",
    },
    {
      title: "AI Assistant",
      description: "Get help with ideation, research, and project development through AI.",
      icon: "🤖",
    },
    {
      title: "Equipment Booking",
      description: "Reserve IdeaLab equipment and facilities for your projects.",
      icon: "🔧",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-primary-50 to-white">
      <section className="py-20 text-center">
        <div className="max-w-4xl mx-auto px-4">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Welcome to IdeaLab AI
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            A college IdeaLab fostering innovation through building, experimentation,
            collaboration, and mentoring.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              to="/projects"
              className="px-8 py-3 bg-primary-600 text-white rounded-lg text-lg font-medium hover:bg-primary-700 transition-colors"
            >
              Explore Projects
            </Link>
            <Link
              to="/chat"
              className="px-8 py-3 bg-secondary-600 text-white rounded-lg text-lg font-medium hover:bg-secondary-700 transition-colors"
            >
              Ask the AI Assistant
            </Link>
          </div>
        </div>
      </section>

      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            What IdeaLab AI Offers
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((f) => (
              <div key={f.title} className="text-center p-6 rounded-xl bg-gray-50">
                <div className="text-4xl mb-4">{f.icon}</div>
                <h3 className="font-semibold text-lg text-gray-900 mb-2">{f.title}</h3>
                <p className="text-sm text-gray-600">{f.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Join the IdeaLab Community
          </h2>
          <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
            Whether you're a student with a passion for building, a faculty member
            looking to mentor, or an industry partner interested in collaboration,
            the IdeaLab welcomes you.
          </p>
          <Link
            to="/contact"
            className="px-8 py-3 bg-accent-600 text-white rounded-lg text-lg font-medium hover:bg-accent-700 transition-colors"
          >
            Get in Touch
          </Link>
        </div>
      </section>
    </div>
  );
}
