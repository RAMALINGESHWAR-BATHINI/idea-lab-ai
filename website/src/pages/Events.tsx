import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { Link } from "react-router-dom";

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
  updated_at: string;
}

export function Events() {
const { data: events, isLoading, error } = useQuery({
    queryKey: ["events"],
    queryFn: () => api.get<Event[]>("/content/events"),
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
        <p className="text-red-600">Failed to load events. Please try again later.</p>
      </div>
    );
  }

  const upcoming = (events || []).filter((e) => {
    if (e.starts_at) {
      const date = new Date(e.starts_at);
      return date > new Date();
    }
    return false;
  });

  const past = (events || []).filter((e) => {
    if (e.starts_at) {
      const date = new Date(e.starts_at);
      return date <= new Date();
    }
    return false;
  });

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Events</h1>

        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Upcoming</h2>
          {upcoming.length === 0 ? (
            <p className="text-gray-500">No upcoming events.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {upcoming.map((event) => (
                <EventCard key={event.id} event={event} />
              ))}
            </div>
          )}
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Past Events</h2>
          {past.length === 0 ? (
            <p className="text-gray-500">No past events yet.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {past.map((event) => (
                <EventCard key={event.id} event={event} />
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function EventCard({ event }: { event: Event }) {
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "Date TBD";
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  return (
    <Link
      to={`/events/${event.id}`}
      className="block bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow"
    >
      <div className="flex justify-between items-start mb-3">
        <h3 className="font-bold text-lg text-gray-900">{event.title}</h3>
        <span
          className={`px-2 py-1 text-xs rounded-full ${
            event.status === "PUBLISHED"
              ? "bg-green-100 text-green-800"
              : "bg-gray-100 text-gray-600"
          }`}
        >
          {event.kind}
        </span>
      </div>
      <p className="text-sm text-gray-600 mb-3 line-clamp-3">
        {event.description || "No description available."}
      </p>
      <div className="text-sm text-gray-500 space-y-1">
        <p>📅 {formatDate(event.starts_at)}</p>
        {event.venue && <p>📍 {event.venue}</p>}
        {event.registration_url && (
          <p className="text-primary-600 font-medium">Register →</p>
        )}
      </div>
    </Link>
  );
}

