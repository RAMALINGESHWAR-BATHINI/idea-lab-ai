import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { useAuth } from "@/contexts/AuthContext";
import { useState } from "react";

export function EventsDashboard() {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState<any>(null);

  const { data: events, isLoading } = useQuery(["events-admin"], () =>
    api.get<any[]>("/content/events", token || undefined)
  );

  const createMutation = useMutation(
    (data: any) => api.post<any>("/content/events", data, token || undefined),
    {
      onSuccess: () => queryClient.invalidateQueries(["events-admin"]),
    },
  );

  if (isLoading) return <div className="text-gray-500">Loading events...</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Events</h1>
        <button
          onClick={() => setEditing({})}
          className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
        >
          New Event
        </button>
      </div>

      {editing && (
        <EventForm
          initial={editing}
          onClose={() => setEditing(null)}
          onSave={async (data) => {
            if (editing.id) {
              await api.patch(`/content/events/${editing.id}`, data, token || undefined);
            } else {
              await createMutation.mutateAsync(data);
            }
            queryClient.invalidateQueries(["events-admin"]);
            setEditing(null);
          }}
        />
      )}

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Title
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {events?.map((e) => (
              <tr key={e.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {e.title}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {e.starts_at
                    ? new Date(e.starts_at).toLocaleDateString()
                    : "TBD"}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${
                      e.status === "PUBLISHED"
                        ? "bg-green-100 text-green-800"
                        : e.status === "DRAFT"
                        ? "bg-yellow-100 text-yellow-800"
                        : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {e.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <button
                    onClick={() => setEditing(e)}
                    className="text-primary-600 hover:text-primary-700 mr-2"
                  >
                    Edit
                  </button>
                  <button
                    onClick={async () => {
                      if (confirm("Delete this event?")) {
                        await api.delete(`/content/events/${e.id}`, token || undefined);
                        queryClient.invalidateQueries(["events-admin"]);
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

function EventForm({
  initial,
  onClose,
  onSave,
}: {
  initial: any;
  onClose: () => void;
  onSave: (data: any) => Promise<void>;
}) {
  const [title, setTitle] = useState(initial.title || "");
  const [kind, setKind] = useState(initial.kind || "EVENT");
  const [description, setDescription] = useState(initial.description || "");
  const [venue, setVenue] = useState(initial.venue || "");
  const [startsAt, setStartsAt] = useState(
    initial.starts_at ? new Date(initial.starts_at).toISOString().slice(0, 16) : ""
  );
  const [status, setStatus] = useState(initial.status || "DRAFT");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSave({
      title,
      kind,
      description,
      venue,
      starts_at: startsAt ? new Date(startsAt).toISOString() : null,
      status,
      access_level: "PUBLIC",
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-lg font-semibold mb-4">
          {initial.id ? "Edit Event" : "New Event"}
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
            <label className="block text-sm font-medium text-gray-700">Kind</label>
            <select
              value={kind}
              onChange={(e) => setKind(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            >
              <option value="EVENT">Event</option>
              <option value="WORKSHOP">Workshop</option>
              <option value="SEMINAR">Seminar</option>
              <option value="HACKATHON">Hackathon</option>
              <option value="MEETING">Meeting</option>
            </select>
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
            <label className="block text-sm font-medium text-gray-700">Venue</label>
            <input
              type="text"
              value={venue}
              onChange={(e) => setVenue(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Start</label>
            <input
              type="datetime-local"
              value={startsAt}
              onChange={(e) => setStartsAt(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Status</label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            >
              <option value="DRAFT">Draft</option>
              <option value="PENDING_REVIEW">Pending Review</option>
              <option value="PUBLISHED">Published</option>
              <option value="CANCELLED">Cancelled</option>
              <option value="ARCHIVED">Archived</option>
            </select>
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

