import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { useAuth } from "@/contexts/AuthContext";

export function ProjectsDashboard() {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState<any>(null);

  const { data: projects, isLoading } = useQuery({
    queryKey: ["projects-admin"],
    queryFn: () => api.get<any[]>("/content/projects", token || undefined),
  });

  if (isLoading) return <div className="text-gray-500">Loading projects...</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
        <button
          onClick={() => setEditing({})}
          className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
        >
          New Project
        </button>
      </div>

      {editing && (
        <ProjectForm
          initial={editing}
          onClose={() => setEditing(null)}
          onSave={async (data) => {
            if (editing.id) {
              await api.patch(`/content/projects/${editing.id}`, data, token || undefined);
            } else {
              await api.post("/content/projects", data, token || undefined);
            }
            queryClient.invalidateQueries({ queryKey: ["projects-admin"] });
            setEditing(null);
          }}
        />
      )}

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Domain</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Published</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {projects?.map((p) => (
              <tr key={p.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{p.title}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{p.domain || "—"}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{p.status || "—"}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {p.is_published ? "Yes" : "No"}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <button
                    onClick={() => setEditing(p)}
                    className="text-primary-600 hover:text-primary-700 mr-2"
                  >
                    Edit
                  </button>
                  <button
                    onClick={async () => {
                      if (confirm("Delete this project?")) {
                        await api.delete(`/content/projects/${p.id}`, token || undefined);
                        queryClient.invalidateQueries({ queryKey: ["projects-admin"] });
                      }
                    }}
                    className="text-red-600 hover:text-red-700"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ProjectForm({
  initial,
  onClose,
  onSave,
}: {
  initial: any;
  onClose: () => void;
  onSave: (data: any) => Promise<void>;
}) {
  const [title, setTitle] = useState(initial.title || "");
  const [domain, setDomain] = useState(initial.domain || "");
  const [description, setDescription] = useState(initial.description || "");
  const [status, setStatus] = useState(initial.status || "active");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSave({ title, domain, description, status, is_published: true });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-lg font-semibold mb-4">
          {initial.id ? "Edit Project" : "New Project"}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Title</label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Domain</label>
            <input
              type="text"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
              rows={3}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Status</label>
            <input
              type="text"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            />
          </div>
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-md"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
            >
              {initial.id ? "Update" : "Create"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}