import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { api } from "@/api/client";
import { useAuth } from "@/contexts/AuthContext";

interface Event {
  id: string;
  title: string;
  kind: string;
  description: string | null;
  venue: string | null;
  starts_at: string | null;
  ends_at: string | null;
  organizer: string | null;
  registration_url: string | null;
  capacity: number | null;
  status: string;
  access_level: string;
  created_at: string;
}

export function EventDetail() {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();

const { data: event, isLoading, error } = useQuery({
    queryKey: ["event", id],
    queryFn: () => api.get<Event>(`/content/events/${id}`),
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

  if (error || !event) {
    return (
      <div className="min-h-screen py-16 text-center">
        <p className="text-red-600">Event not found.</p>
        <Link to="/events" className="text-primary-600 hover:underline mt-2 inline-block">
          ← Back to Events
        </Link>
      </div>
    );
  }

  const formatDate = (d: string | null) => {
    if (!d) return null;
    return new Date(d).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  return (
    <div className="min-h-screen py-12 bg-gray-50">
      <div className="max-w-4xl mx-auto px-4">
        <Link to="/events" className="text-sm text-primary-600 hover:underline mb-4 inline-block">
          ← Back to Events
        </Link>

        <div className="bg-white rounded-xl shadow-md p-8">
          <div className="flex justify-between items-start mb-4">
            <h1 className="text-3xl font-bold text-gray-900">{event.title}</h1>
            <span className="px-3 py-1 text-sm rounded-full bg-primary-100 text-primary-800">
              {event.kind}
            </span>
          </div>

          {event.description && (
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Description</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{event.description}</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 text-gray-700">
            {event.starts_at && (
              <div>
                <span className="font-medium">Starts:</span>{" "}
                {formatDate(event.starts_at)}
                {event.ends_at && (
                  <> – {formatDate(event.ends_at)}</>
                )}
              </div>
            )}
            {event.venue && (
              <div>
                <span className="font-medium">Venue:</span> {event.venue}
              </div>
            )}
            {event.organizer && (
              <div>
                <span className="font-medium">Organizer:</span> {event.organizer}
              </div>
            )}
            {event.capacity && (
              <div>
                <span className="font-medium">Capacity:</span> {event.capacity}
              </div>
            )}
          </div>

          {event.registration_url && (
            <a
              href={event.registration_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
            >
              Register →
            </a>
          )}
        </div>
      </div>
    </div>
  );
}