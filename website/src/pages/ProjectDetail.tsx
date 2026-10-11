import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { api } from "@/api/client";
import { useAuth } from "@/contexts/AuthContext";

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
  created_at: string;
  updated_at: string;
  access_level: string;
}

export function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();

const { data: project, isLoading, error } = useQuery({
    queryKey: ["project", id],
    queryFn: () => api.get<Project>(`/content/projects/${id}`),
  });

  if (isLoading) {
    return (
      <div className="min-h-screen py-16">
        <div className="max-w-4xl mx-auto px-4 animate-pulse space-y-4">
          <div className="h-10 bg-gray-300 rounded w-1/3"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="min-h-screen py-16 text-center">
        <p className="text-red-600">Project not found.</p>
        <Link to="/projects" className="text-primary-600 hover:underline mt-2 inline-block">
          ← Back to Projects
        </Link>
      </div>
    );
  }

  const techList = project.technologies
    ? project.technologies.split(",").map((t) => t.trim())
    : [];

  return (
    <div className="min-h-screen py-12 bg-gray-50">
      <div className="max-w-4xl mx-auto px-4">
        <Link to="/projects" className="text-sm text-primary-600 hover:underline mb-4 inline-block">
          ← Back to Projects
        </Link>

        <div className="bg-white rounded-xl shadow-md p-8">
          <div className="flex justify-between items-start mb-4">
            <h1 className="text-3xl font-bold text-gray-900">{project.title}</h1>
            {project.status && (
              <span className="px-3 py-1 text-sm rounded-full bg-primary-100 text-primary-800">
                {project.status}
              </span>
            )}
          </div>

          {project.domain && (
            <span className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded mb-4">
              {project.domain}
            </span>
          )}

          {project.summary && (
            <p className="text-lg text-gray-700 mb-6">{project.summary}</p>
          )}

          {project.description && (
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">About</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{project.description}</p>
            </div>
          )}

          {techList.length > 0 && (
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Technologies</h2>
              <div className="flex flex-wrap gap-2">
                {techList.map((tech, i) => (
                  <span key={i} className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded">
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="border-t pt-4 text-sm text-gray-500 space-y-1">
            {project.started_at && <p>Started: {new Date(project.started_at).toLocaleDateString()}</p>}
            <p>Created: {new Date(project.created_at).toLocaleDateString()}</p>
            {project.is_published && (
              <span className="inline-block mt-2 px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                Published
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}