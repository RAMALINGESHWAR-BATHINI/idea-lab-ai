import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { Link } from "react-router-dom";

interface Project {
  id: string;
  title: string;
  summary: string | null;
  description: string | null;
  status: string | null;
  domain: string | null;
  technologies: string | null;
  is_active: boolean;
  is_published: boolean;
  started_at: string | null;
  access_level: string;
  created_at: string;
  updated_at: string;
}

export function Projects() {
const { data: projects, isLoading, error } = useQuery({
    queryKey: ["projects"],
    queryFn: () => api.get<Project[]>("/content/projects"),
  });

  if (isLoading) {
    return (
      <div className="min-h-screen py-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-300 rounded w-1/4"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-48 bg-gray-300 rounded-lg"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen py-16 text-center">
        <p className="text-red-600">Failed to load projects. Please try again later.</p>
      </div>
    );
  }

  const published = (projects || []).filter((p) => p.is_published);

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
          <Link
            to="/chat"
            className="px-4 py-2 bg-secondary-600 text-white rounded-lg font-medium hover:bg-secondary-700 transition-colors"
          >
            Ask AI about projects
          </Link>
        </div>

        {published.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">No published projects yet.</p>
            <Link
              to="/contact"
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              Contact us to showcase your project →
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {published.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function ProjectCard({ project }: { project: Project }) {
  const techList = project.technologies
    ? project.technologies.split(",").map((t) => t.trim())
    : [];

  return (
    <Link
      to={`/projects/${project.id}`}
      className="block bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow"
    >
      <h3 className="font-bold text-xl text-gray-900 mb-2">{project.title}</h3>
      {project.domain && (
        <span className="inline-block px-2 py-1 text-xs bg-primary-100 text-primary-800 rounded-full mb-3">
          {project.domain}
        </span>
      )}
      <p className="text-sm text-gray-600 mb-4 line-clamp-3">
        {project.summary || project.description || "No description available."}
      </p>
      {techList.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {techList.slice(0, 4).map((tech, i) => (
            <span
              key={i}
              className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
            >
              {tech}
            </span>
          ))}
          {techList.length > 4 && (
            <span className="px-2 py-1 text-xs text-gray-500">
              +{techList.length - 4} more
            </span>
          )}
        </div>
      )}
      {project.status && (
        <span className="text-xs text-gray-500 font-medium">{project.status}</span>
      )}
    </Link>
  );
}

