import { Link, NavLink } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

// The voice assistant is a separate app that shares this site's backend.
const VOICE_URL: string = import.meta.env.VITE_VOICE_URL || "http://localhost:5174";

export function Navbar() {
  const { user, logout, token } = useAuth();

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex-shrink-0 flex items-center">
            <Link to="/" className="text-2xl font-bold text-primary-700">
              IdeaLab AI
            </Link>
          </div>
          <div className="hidden md:flex space-x-8 items-center">
            <NavLink
              to="/"
              className={({ isActive }) =>
                `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-primary-100 text-primary-900"
                    : "text-gray-600 hover:text-primary-700"
                }`
              }
            >
              Home
            </NavLink>
            <NavLink
              to="/about"
              className={({ isActive }) =>
                `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-primary-100 text-primary-900"
                    : "text-gray-600 hover:text-primary-700"
                }`
              }
            >
              About
            </NavLink>
            <NavLink
              to="/events"
              className={({ isActive }) =>
                `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-primary-100 text-primary-900"
                    : "text-gray-600 hover:text-primary-700"
                }`
              }
            >
              Events
            </NavLink>
            <NavLink
              to="/projects"
              className={({ isActive }) =>
                `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-primary-100 text-primary-900"
                    : "text-gray-600 hover:text-primary-700"
                }`
              }
            >
              Projects
            </NavLink>
            <NavLink
              to="/people"
              className={({ isActive }) =>
                `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-primary-100 text-primary-900"
                    : "text-gray-600 hover:text-primary-700"
                }`
              }
            >
              People
            </NavLink>
            <NavLink
              to="/facilities"
              className={({ isActive }) =>
                `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-primary-100 text-primary-900"
                    : "text-gray-600 hover:text-primary-700"
                }`
              }
            >
              Facilities
            </NavLink>
            <NavLink
              to="/chat"
              className={({ isActive }) =>
                `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-secondary-100 text-secondary-900"
                    : "text-gray-600 hover:text-secondary-700"
                }`
              }
            >
              AI Assistant
            </NavLink>
            <a
              href={VOICE_URL}
              rel="noopener noreferrer"
              className="px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-secondary-700 transition-colors"
            >
              Voice Assistant
            </a>
            {token && (
              <NavLink
                to="/dashboard"
                className={({ isActive }) =>
                  `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-accent-100 text-accent-900"
                      : "text-gray-600 hover:text-accent-700"
                  }`
                }
              >
                Dashboard
              </NavLink>
            )}
          </div>
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <span className="text-sm text-gray-600 hidden md:inline">
                  {user.full_name}
                </span>
                <button
                  onClick={logout}
                  className="px-3 py-1 text-sm text-gray-600 hover:text-primary-700"
                >
                  Sign out
                </button>
              </>
            ) : (
              <NavLink
                to="/login"
                className="px-4 py-2 bg-primary-600 text-white rounded-md text-sm font-medium hover:bg-primary-700 transition-colors"
              >
                Sign in
              </NavLink>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

export function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-white text-lg font-semibold mb-4">IdeaLab AI</h3>
            <p className="text-sm">
              A voice-first AI assistant for the college IdeaLab.
            </p>
          </div>
          <div>
            <h4 className="text-white font-medium mb-3">Quick Links</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/about" className="hover:text-white transition-colors">About</Link></li>
              <li><Link to="/events" className="hover:text-white transition-colors">Events</Link></li>
              <li><Link to="/projects" className="hover:text-white transition-colors">Projects</Link></li>
              <li><Link to="/people" className="hover:text-white transition-colors">People</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-medium mb-3">Resources</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/facilities" className="hover:text-white transition-colors">Facilities</Link></li>
              <li><Link to="/achievements" className="hover:text-white transition-colors">Achievements</Link></li>
              <li><Link to="/media" className="hover:text-white transition-colors">Media</Link></li>
              <li><Link to="/contact" className="hover:text-white transition-colors">Contact</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-medium mb-3">AI Assistant</h4>
            <p className="text-sm">
              Try the AI Assistant for IdeaLab information, project guidance, and research help.
            </p>
            <Link
              to="/chat"
              className="inline-block mt-2 px-4 py-2 bg-secondary-600 text-white rounded-md text-sm font-medium hover:bg-secondary-700 transition-colors"
            >
              Open Assistant
            </Link>
          </div>
        </div>
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm">
          &copy; {new Date().getFullYear()} IdeaLab AI. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
