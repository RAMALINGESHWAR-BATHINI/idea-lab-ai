import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import idealabData from "../data/idealab.json";

interface Faculty {
  id: string;
  full_name: string;
  email: string | null;
  phone: string | null;
  designation: string | null;
  specialization: string | null;
  research_interests: string | null;
  bio: string | null;
  office_location: string | null;
  photo_url: string | null;
  is_hod: boolean;
  is_public: boolean;
  access_level: string;
  department: { id: string; name: string; code: string } | null;
  created_at: string;
}

interface Staff {
  id: string;
  full_name: string;
  email: string | null;
  phone: string | null;
  designation: string | null;
  responsibilities: string | null;
  access_level: string;
  department: { id: string; name: string; code: string } | null;
  created_at: string;
}

interface IdeaLabMember {
  id: string;
  full_name: string;
  email: string | null;
  role_title: string | null;
  team: string | null;
  bio: string | null;
  skills: string | null;
  joined_at: string | null;
  is_active: boolean;
  access_level: string;
  department: { id: string; name: string; code: string } | null;
  created_at: string;
}

export function People() {
const { data: faculty, isLoading: facultyLoading } = useQuery({
    queryKey: ["faculty"],
    queryFn: () => api.get<Faculty[]>("/content/faculty"),
  });
  const { data: members, isLoading: membersLoading } = useQuery({
    queryKey: ["idealab-members"],
    queryFn: () => api.get<IdeaLabMember[]>("/content/idealab-members"),
  });
  const { data: staff, isLoading: staffLoading } = useQuery({
    queryKey: ["staff"],
    queryFn: () => api.get<Staff[]>("/content/staff"),
  });

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">People</h1>

      <section className="mb-12">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">Executive Board</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {idealabData.executiveBoard.map((m, i) => (
            <div key={i} className="bg-white rounded-xl shadow-md p-6 text-center">
              <div className="w-16 h-16 rounded-full bg-secondary-100 flex items-center justify-center text-2xl mx-auto mb-3">
                {m.name.charAt(0)}
              </div>
              <h3 className="font-bold text-lg text-gray-900">{m.name}</h3>
              <p className="text-sm text-secondary-600 font-medium">{m.role}</p>
              <p className="text-xs text-gray-500">{m.department}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mb-12">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">Faculty & Mentors</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {idealabData.techGurus.map((m, i) => (
            <div key={i} className="bg-white rounded-xl shadow-md p-4 text-center">
              <h3 className="font-semibold text-sm text-gray-900">{m.name}</h3>
              <p className="text-xs text-gray-500">{m.department}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mb-12">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">Coordinators</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {idealabData.coordinators.map((m, i) => (
            <div key={i} className="bg-white rounded-xl shadow-md p-4 text-center">
              <h3 className="font-semibold text-sm text-gray-900">{m.name}</h3>
              <p className="text-xs text-gray-500">{m.department}</p>
            </div>
          ))}
        </div>
      </section>

    </div>
  </div>
  );
}

function PersonCard({ person }: { person: Faculty | Staff }) {
  const faculty = person as Faculty;
  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="flex items-start space-x-4">
        {faculty.photo_url ? (
          <img
            src={faculty.photo_url}
            alt={person.full_name}
            className="w-16 h-16 rounded-full object-cover"
          />
        ) : (
            <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center text-2xl">
              {person.full_name.charAt(0)}
            </div>
        )}
        <div className="flex-1">
          <h3 className="font-bold text-lg text-gray-900">{person.full_name}</h3>
          <p className="text-sm text-gray-600">{person.designation || "Faculty"}</p>
          {faculty.specialization && (
            <p className="text-sm text-gray-500 mt-1">Specialization: {faculty.specialization}</p>
          )}
          {faculty.email && (
            <p className="text-sm text-primary-600 mt-2">{faculty.email}</p>
          )}
        </div>
      </div>
    </div>
  );
}

function MemberCard({ member }: { member: IdeaLabMember }) {
  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h3 className="font-bold text-lg text-gray-900">{member.full_name}</h3>
      {member.role_title && (
        <p className="text-sm text-secondary-600 font-medium">{member.role_title}</p>
      )}
      {member.team && <p className="text-sm text-gray-500">Team: {member.team}</p>}
      {member.skills && (
        <p className="text-sm text-gray-600 mt-2">Skills: {member.skills}</p>
      )}
    </div>
  );
}


