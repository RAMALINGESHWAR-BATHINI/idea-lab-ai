import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { useAuth } from "@/contexts/AuthContext";

export function Dashboard() {
  const { token } = useAuth();

const { data: events, isLoading: eventsLoading } = useQuery({
    queryKey: ["events"],
    queryFn: () => api.get<any[]>("/content/events", token || undefined),
  });

  const { data: projects, isLoading: projectsLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: () => api.get<any[]>("/content/projects", token || undefined),
  });

  const { data: equipment, isLoading: equipmentLoading } = useQuery({
    queryKey: ["equipment"],
    queryFn: () => api.get<any[]>("/content/equipment", token || undefined),
  });

  const stats = [
    {
      label: "Events",
      value: events?.length ?? (eventsLoading ? "..." : 0),
      color: "bg-blue-500",
    },
    {
      label: "Projects",
      value: projects?.length ?? (projectsLoading ? "..." : 0),
      color: "bg-green-500",
    },
    {
      label: "Equipment",
      value: equipment?.length ?? (equipmentLoading ? "..." : 0),
      color: "bg-purple-500",
    },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard Overview</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {stats.map((s) => (
          <div key={s.label} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className={`w-3 h-3 rounded-full ${s.color} mr-3`}></div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{s.value}</p>
                <p className="text-sm text-gray-600">{s.label}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-gray-900">Recent Events</h2>
          </div>
          <div className="p-4">
            {eventsLoading ? (
              <p className="text-gray-500">Loading...</p>
            ) : (events || []).length === 0 ? (
              <p className="text-gray-500">No events yet.</p>
            ) : (
              <ul className="space-y-2 text-sm">
                {events?.slice(0, 5).map((e) => (
                  <li key={e.id} className="border-l-2 border-primary-500 pl-3">
                    <span className="font-medium">{e.title}</span>
                    <span className="text-gray-500 ml-2">
                      ({e.status})
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-gray-900">Recent Projects</h2>
          </div>
          <div className="p-4">
            {projectsLoading ? (
              <p className="text-gray-500">Loading...</p>
            ) : (projects || []).length === 0 ? (
              <p className="text-gray-500">No projects yet.</p>
            ) : (
              <ul className="space-y-2 text-sm">
                {projects?.slice(0, 5).map((p) => (
                  <li key={p.id} className="border-l-2 border-secondary-500 pl-3">
                    <span className="font-medium">{p.title}</span>
                    <span className="text-gray-500 ml-2">
                      ({p.status || "active"})
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

