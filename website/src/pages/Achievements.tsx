import { Link } from "react-router-dom";

export function Achievements() {
  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Achievements & Impact
        </h1>
        <p className="text-gray-600 mb-8">
          Verified achievements, awards, patents, and outcomes from IdeaLab
          activities.
        </p>

        <div className="bg-white rounded-xl shadow-md p-8 text-center">
          <div className="text-6xl mb-4">🏆</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            No achievements recorded yet
          </h2>
          <p className="text-gray-500">
            Achievement records will be added as they are verified.
          </p>
        </div>
      </div>
    </div>
  );
}

export function Media() {
  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Media & Resources</h1>
        <p className="text-gray-600 mb-8">
          Posters, photos, videos, brochures, and public documents from IdeaLab
          activities.
        </p>

        <div className="bg-white rounded-xl shadow-md p-8 text-center">
          <div className="text-6xl mb-4">📁</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Media library coming soon
          </h2>
          <p className="text-gray-500">
            Public documents and media will be available here once uploaded.
          </p>
        </div>
      </div>
    </div>
  );
}

export function Contact() {
  return (
    <div className="min-h-screen py-12">
      <div className="max-w-3xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Contact & Participation</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Get in Touch
            </h2>
            <div className="space-y-4 text-gray-700">
              <p>
                <strong>Email:</strong>{" "}
                <a
                  href="mailto:admin@idealab.local"
                  className="text-primary-600 hover:text-primary-700"
                >
                  admin@idealab.local
                </a>
              </p>
              <p>
                <strong>Location:</strong> College IdeaLab, Main Campus
              </p>
              <p>
                <strong>Hours:</strong> Monday – Friday, 9:00 AM – 6:00 PM
              </p>
            </div>
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Enquiry Form
            </h2>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Name
                </label>
                <input
                  type="text"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Email
                </label>
                <input
                  type="email"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Message
                </label>
                <textarea
                  rows={4}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                  required
                />
              </div>
              <button
                type="submit"
                className="w-full px-4 py-2 bg-primary-600 text-white rounded-md font-medium hover:bg-primary-700 transition-colors"
              >
                Send Message
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
