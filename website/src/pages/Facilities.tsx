import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "@/api/client";

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

export function Facilities() {
const { data: equipment, isLoading } = useQuery({
    queryKey: ["equipment"],
    queryFn: () => api.get<Equipment[]>("/content/equipment"),
  });

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Facilities & Equipment</h1>
        <p className="text-gray-600 mb-8">
          Browse available IdeaLab equipment and facilities.
        </p>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-48 bg-gray-300 rounded-lg animate-pulse"></div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {equipment?.map((eq) => (
              <EquipmentCard key={eq.id} equipment={eq} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function EquipmentCard({ equipment }: { equipment: Equipment }) {
  const specs = equipment.specifications as Record<string, string> | null;

  return (
    <Link
      to={`/facilities/${equipment.id}`}
      className="block bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow"
    >
      <div className="flex justify-between items-start mb-3">
        <h3 className="font-bold text-lg text-gray-900">{equipment.name}</h3>
        <span
          className={`px-2 py-1 text-xs rounded-full ${
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
        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
          {equipment.category}
        </span>
      )}
      {equipment.description && (
        <p className="text-sm text-gray-600 mt-3 line-clamp-3">{equipment.description}</p>
      )}
      {equipment.location && (
        <p className="text-sm text-gray-500 mt-2">📍 {equipment.location}</p>
      )}
      {equipment.quantity !== null && (
        <p className="text-sm text-gray-500 mt-1">Quantity: {equipment.quantity}</p>
      )}
    </Link>
  );
}

