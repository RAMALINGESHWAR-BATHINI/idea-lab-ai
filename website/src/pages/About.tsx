import { Link } from "react-router-dom";

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
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            How to Participate
          </h2>
          <ul className="list-disc list-inside text-gray-700 space-y-2">
            <li>Attend workshops, bootcamps, and ideation sessions</li>
            <li>Join or form a project team</li>
            <li>Mentor others or seek guidance from faculty coordinators</li>
            <li>Showcase achievements through verified publications and prototypes</li>
            <li>Collaborate with industry partners on real problems</li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            AI Assistant
          </h2>
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
