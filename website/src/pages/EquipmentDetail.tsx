import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { api } from "@/api/client";
import { useAuth } from "@/contexts/AuthContext";

interface Equipment {
  id: string;
  name: string;
  category: string | null;
  description: string | null;
  specifications: Record<string, unknown> | null;
  serial_number: string | null;
  location: string | null;
  status: string | null;
  is_active: boolean;
  quantity: number | null;
  access_level: string;
  created_at: string;
  updated_at: string;
}

export function EquipmentDetail() {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();

  const { data: equipment, isLoading, error } = useQuery(
    ["equipment", id],
    () => api.get<Equipment>(`/content/equipment/${id}`, token || undefined)
  );

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

  if (error || !equipment) {
    return (
      <div className="min-h-screen py-16 text-center">
        <p className="text-red-600">Equipment not found.</p>
        <Link to="/facilities" className="text-primary-600 hover:underline mt-2 inline-block">
          ← Back to Facilities
        </Link>
      </div>
    );
  }

  const specs = equipment.specifications as Record<string, string> | null;

  return (
    <div className="min-h-screen py-12 bg-gray-50">
      <div className="max-w-4xl mx-auto px-4">
        <Link to="/facilities" className="text-sm text-primary-600 hover:underline mb-4 inline-block">
          ← Back to Facilities
        </Link>

        <div className="bg-white rounded-xl shadow-md p-8">
          <div className="flex justify-between items-start mb-4">
            <h1 className="text-3xl font-bold text-gray-900">{equipment.name}</h1>
            <span
              className={`px-3 py-1 text-sm rounded-full ${
                equipment.status === "available"
                  ? "bg-green-100 text-green-800"
                  : equipment.status === "maintenance"
                  ? "bg-yellow-100 text-yellow-800"
                  : "bg-gray-100 text-gray-600"
              }`}
            >
              {equipment.status || "unknown"}
            </span>
          </div>

          {equipment.category && (
            <span className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded mb-4">
              {equipment.category}
            </span>
          )}

          {equipment.description && (
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Description</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{equipment.description}</p>
            </div>
          )}

          {specs && Object.keys(specs).length > 0 && (
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Specifications</h2>
              <dl className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                {Object.entries(specs).map(([k, v]) => (
                  <div key={k} className="flex justify-between border-b border-gray-100 py-1">
                    <dt className="font-medium text-gray-500">{k}:</dt>
                    <dd className="text-gray-900">{String(v)}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}

          <div className="border-t pt-4 text-sm text-gray-500 space-y-1">
            {equipment.location && <p>Location: {equipment.location}</p>}
            {equipment.serial_number && <p>Serial: {equipment.serial_number}</p>}
            {equipment.quantity !== null && <p>Quantity: {equipment.quantity}</p>}
          </div>
        </div>
      </div>
    </div>
  );
}