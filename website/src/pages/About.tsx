import { Link } from "react-router-dom";
import idealabData from "../data/idealab.json";

export function About() {
  return (
    <div className="min-h-screen py-16">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">About IdeaLab</h1>

        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Our Purpose</h2>
          <p className="text-gray-700 leading-relaxed">
            The IdeaLab is a college initiative that fosters innovation through
            continuous learning by building, experimentation, collaboration,
            mentoring, and sharing knowledge. It is a space where students can
            explore ideas, work on real projects, and develop practical skills
            alongside faculty and industry mentors.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Innovation and Experiential Learning
          </h2>
          <p className="text-gray-700 leading-relaxed">
            IdeaLab follows a structured ideation process:
          </p>
          <div className="mt-4 p-6 bg-gray-50 rounded-lg">
            <p className="text-gray-700 font-medium">
              Problem/Idea → Understand → Define → Ideate → Discuss → Prototype →
              Test → Get Feedback → Improve → Build
            </p>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Vision</h2>
          <p className="text-gray-700 leading-relaxed">{idealabData.vision}</p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Mission</h2>
          <ul className="list-disc list-inside text-gray-700 space-y-2">
            {idealabData.mission.map((m, i) => (
              <li key={i}>{m}</li>
            ))}
          </ul>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Executive Board
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {idealabData.executiveBoard.map((m, i) => (
              <div key={i} className="p-4 bg-gray-50 rounded-lg text-center">
                <p className="font-semibold text-gray-900">{m.name}</p>
                <p className="text-sm text-gray-600">{m.role}</p>
                <p className="text-xs text-gray-500">{m.department}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Tech Gurus</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {idealabData.techGurus.map((m, i) => (
              <div key={i} className="p-4 bg-gray-50 rounded-lg text-center">
                <p className="font-semibold text-gray-900 text-sm">{m.name}</p>
                <p className="text-xs text-gray-500">{m.department}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Operational Managers
          </h2>
          <div className="grid grid-cols-2 gap-4">
            {idealabData.operationalManagers.map((m, i) => (
              <div key={i} className="p-4 bg-gray-50 rounded-lg text-center">
                <p className="font-semibold text-gray-900 text-sm">{m.name}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Coordinators
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {idealabData.coordinators.map((m, i) => (
              <div key={i} className="p-4 bg-gray-50 rounded-lg text-center">
                <p className="font-semibold text-gray-900 text-sm">{m.name}</p>
                <p className="text-xs text-gray-500">{m.department}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            IDEA Lab Overview
          </h2>
          <div className="p-6 bg-gray-50 rounded-lg space-y-2">
            <p className="text-gray-700">
              <span className="font-semibold">Lab Value:</span> {idealabData.ideaLabWorth}
            </p>
            <p className="text-gray-700">
              <span className="font-semibold">Total IDEA Labs across India:</span>{" "}
              {idealabData.totalLabs}
            </p>
            <p className="text-gray-700">
              <span className="font-semibold">Stakeholders:</span>{" "}
              {idealabData.stakeholders.join(", ")}
            </p>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Activities Conducted
          </h2>
          <ul className="list-disc list-inside text-gray-700 space-y-2">
            {idealabData.activities.map((a, i) => (
              <li key={i}>
                <span className="font-medium">{a.name}</span> — {a.description}
              </li>
            ))}
          </ul>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Available Machinery & Equipment
          </h2>
          <div className="flex flex-wrap gap-2">
            {idealabData.machinery.map((m, i) => (
              <span
                key={i}
                className="px-3 py-1 bg-secondary-100 text-secondary-800 rounded-full text-sm"
              >
                {m}
              </span>
            ))}
          </div>
          <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              "cnc-wood-router.png",
              "laser-cutting.png",
              "table-saw.png",
              "3d-printer.png",
              "3d-scanner.png",
              "sublimation-printer.png",
              "lathe-machine.png",
              "welding-machine.png",
              "iot-sensors.png",
            ].map((img, i) => (
              <img
                key={i}
                src={`/ppt-images/${img}`}
                alt={img.replace(".png", "").replace(/-/g, " ")}
                className="rounded-lg shadow-sm w-full h-32 object-cover"
              />
            ))}
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Expected Outcomes
          </h2>
          <ul className="list-disc list-inside text-gray-700 space-y-2">
            {idealabData.expectedOutcomes.map((o, i) => (
              <li key={i}>{o}</li>
            ))}
          </ul>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Partners & Accreditation
          </h2>
          <div className="flex flex-wrap items-center justify-center gap-8">
            <img src="/ppt-images/naac-logo.png" alt="NAAC" className="h-16 object-contain" />
            <img src="/ppt-images/aicte-idea-lab-logo.png" alt="AICTE IDEA Lab" className="h-16 object-contain" />
          </div>
        </section>

        <section>
          <p className="text-gray-700 leading-relaxed">
            The IdeaLab AI assistant helps you explore ideas, research topics, and
            develop projects. It follows the IdeaLab process — asking what problem
            you are solving, who it is for, and what already exists before jumping
            to solutions.
          </p>
          <Link
            to="/chat"
            className="mt-4 inline-block px-6 py-3 bg-secondary-600 text-white rounded-lg font-medium hover:bg-secondary-700 transition-colors"
          >
            Try the AI Assistant
          </Link>
        </section>
      </div>
    </div>
  );
}