import { ReactNode } from "react";
import { Link, Outlet } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Navbar, Footer } from "@/components/Navbar";

export function PublicLayout() {
  return (
    <>
      <Navbar />
      <main className="flex-grow">
        <Outlet />
      </main>
      <Footer />
    </>
  );
}

export function DashboardLayout() {
  return (
    <div className="flex h-screen bg-gray-50">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <DashboardHeader />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function DashboardSidebar() {
  const links = [
    { to: "/dashboard", label: "Overview" },
    { to: "/dashboard/events", label: "Events" },
    { to: "/dashboard/projects", label: "Projects" },
    { to: "/dashboard/people", label: "People" },
    { to: "/dashboard/equipment", label: "Equipment" },
    { to: "/dashboard/documents", label: "Documents" },
    { to: "/dashboard/users", label: "Users" },
    { to: "/dashboard/audit", label: "Audit Logs" },
    { to: "/dashboard/settings", label: "Settings" },
  ];

  return (
    <aside className="w-64 bg-gray-900 text-gray-300 flex flex-col">
      <div className="p-4 border-b border-gray-800">
        <span className="text-xl font-bold text-white">Dashboard</span>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {links.map(({ to, label }) => (
          <Link
            key={to}
            to={to}
            className="block px-3 py-2 rounded-md text-sm hover:bg-gray-800 hover:text-white transition-colors"
          >
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}

function DashboardHeader() {
  const { user, logout } = useAuth();
  return (
    <header className="bg-white shadow-sm border-b px-6 py-3 flex justify-between items-center">
      <h1 className="text-lg font-semibold text-gray-900">Admin Dashboard</h1>
      <div className="flex items-center space-x-4">
        <span className="text-sm text-gray-600">{user?.full_name}</span>
        <button
          onClick={logout}
          className="text-sm text-gray-600 hover:text-gray-900"
        >
          Sign out
        </button>
      </div>
    </header>
  );
}
