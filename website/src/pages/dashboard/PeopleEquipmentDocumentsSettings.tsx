import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { useAuth } from "@/contexts/AuthContext";

export function PeopleDashboard() {
  const { token } = useAuth();

  const { data: faculty, isLoading: facultyLoading } = useQuery(["faculty"], () =>
    api.get<any[]>("/content/faculty", token || undefined)
  );
  const { data: staff, isLoading: staffLoading } = useQuery(["staff"], () =>
    api.get<any[]>("/content/staff", token || undefined)
  );
  const { data: members, isLoading: membersLoading } = useQuery(["idealab-members"], () =>
    api.get<any[]>("/content/idealab-members", token || undefined)
  );

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">People Management</h1>

      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Faculty</h2>
        {facultyLoading ? (
          <p className="text-gray-500">Loading...</p>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Designation</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {faculty?.map((f) => (
                <tr key={f.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{f.full_name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{f.email || "—"}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{f.designation || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">IdeaLab Members</h2>
        {membersLoading ? (
          <p className="text-gray-500">Loading...</p>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Team</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {members?.map((m) => (
                <tr key={m.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{m.full_name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{m.role_title || "—"}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{m.team || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export function EquipmentDashboard() {
  const { token } = useAuth();
  const { data: equipment, isLoading } = useQuery(["equipment-admin"], () =>
    api.get<any[]>("/content/equipment", token || undefined)
  );

  if (isLoading) return <div className="text-gray-500">Loading equipment...</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Equipment</h1>
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {equipment?.map((e) => (
            <tr key={e.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{e.name}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{e.category || "—"}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{e.status || "—"}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{e.location || "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function DocumentsDashboard() {
  const { token } = useAuth();
  const { data: docs, isLoading } = useQuery(["documents"], () =>
    api.get<any[]>("/content/documents", token || undefined)
  );

  if (isLoading) return <div className="text-gray-500">Loading documents...</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Documents</h1>
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Access</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {docs?.map((d) => (
            <tr key={d.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{d.title}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{d.doc_type}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{d.processing_status}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{d.access_level}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function SettingsDashboard() {
  const { token } = useAuth();
  const { data: settings, isLoading } = useQuery(["settings"], () =>
    api.get<any[]>("/admin/settings", token || undefined)
  );

  if (isLoading) return <div className="text-gray-500">Loading settings...</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">System Settings</h1>
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Key</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Public</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {settings?.map((s) => (
            <tr key={s.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{s.key}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{s.value || "—"}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {s.is_public ? "Yes" : "No"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

