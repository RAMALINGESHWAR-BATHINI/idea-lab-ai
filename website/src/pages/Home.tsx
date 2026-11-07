import { Link } from "react-router-dom";
import idealabData from "../data/idealab.json";

export function Home() {
  const features = [
    {
      title: "Event Management",
      description: "Create, schedule, and manage IdeaLab events, workshops, and hackathons.",
      icon: "Event Management",
    },
    {
      title: "Project Showcase",
      description: "Browse student projects, view prototypes, and track development milestones.",
      icon: "Project Showcase",
    },
    {
      title: "AI Assistant",
      description: "Get help with ideation, research, and project development through AI.",
      icon: "AI Assistant",
    },
    {
      title: "Equipment Booking",
      description: "Reserve IdeaLab equipment and facilities for your projects.",
      icon: "Equipment Booking",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-primary-50 to-white">
      <section className="py-8 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex flex-wrap items-center justify-center gap-6">
            <img src="/ppt-images/gcet-logo.png" alt="" className="h-10 object-contain opacity-80" />
            <img src="/ppt-images/naac-logo.png" alt="" className="h-10 object-contain opacity-80" />
            <img src="/ppt-images/idealab-logo.png" alt="" className="h-10 object-contain opacity-80" />
            <img src="/ppt-images/iqac-logo.png" alt="" className="h-10 object-contain opacity-80" />
            <img src="/ppt-images/aicte-idea-lab-logo.png" alt="" className="h-10 object-contain opacity-80" />
          </div>
        </div>
      </section>

      <section className="py-20 text-center">
        <div className="max-w-4xl mx-auto px-4">
          <img
            src="/ppt-images/aicte-idea-lab-logo.png"
            alt="AICTE IDEA Lab Logo"
            className="mx-auto mb-6 h-24"
          />
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Welcome to IdeaLab
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            AICTE IDEA Lab at {idealabData.college} — fostering innovation
            through building, experimentation, collaboration, and mentoring.
          </p>
          <p className="text-sm text-gray-500 mb-8">
            {idealabData.accreditation}
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
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">
            IDEA Lab Value: {idealabData.ideaLabWorth}
          </h2>
          <p className="text-lg text-gray-600 text-center mb-8 max-w-2xl mx-auto">
            {idealabData.totalLabs} IDEA Labs across India. Stakeholders include{" "}
            {idealabData.stakeholders.join(", ")}.
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {["cnc-wood-router.png", "laser-cutting.png", "3d-printer.png", "iot-sensors.png"].map(
              (img, i) => (
                <img
                  key={i}
                  src={`/ppt-images/${img}`}
                  alt={img.replace(".png", "").replace(/-/g, " ")}
                  className="rounded-lg shadow-sm w-full h-32 object-cover"
                />
              )
            )}
          </div>
        </div>
      </section>

      <section className="py-16 bg-white">
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
