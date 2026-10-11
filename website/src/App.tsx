import { Routes, Route, Navigate } from "react-router-dom";
import { Home, About, Events, EventDetail, Projects, ProjectDetail, People, Facilities, EquipmentDetail, Achievements, Media, Contact, Chat, Login, Register } from "@/pages";
import { PublicLayout, DashboardLayout } from "@/components/Layout";
import { Dashboard } from "@/pages/dashboard/Dashboard";
import { EventsDashboard } from "@/pages/dashboard/EventsDashboard";
import { ProjectsDashboard } from "@/pages/dashboard/ProjectsDashboard";
import { PeopleDashboard, EquipmentDashboard, DocumentsDashboard, SettingsDashboard } from "@/pages/dashboard/PeopleEquipmentDocumentsSettings";
import { UsersDashboard } from "@/pages/dashboard/UsersDashboard";
import { AuditDashboard } from "@/pages/dashboard/AuditDashboard";
import { RequireAuth, RequireSuperuser } from "@/components/RequireAuth";

function App() {
  return (
    <Routes>
      {/* Public website routes */}
      <Route path="/" element={<PublicLayout />}>
        <Route index element={<Home />} />
        <Route path="about" element={<About />} />
        <Route path="events" element={<Events />} />
        <Route path="events/:id" element={<EventDetail />} />
        <Route path="projects" element={<Projects />} />
        <Route path="projects/:id" element={<ProjectDetail />} />
        <Route path="people" element={<People />} />
        <Route path="facilities" element={<Facilities />} />
        <Route path="facilities/:id" element={<EquipmentDetail />} />
        <Route path="achievements" element={<Achievements />} />
        <Route path="media" element={<Media />} />
        <Route path="contact" element={<Contact />} />
        <Route path="chat" element={<Chat />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
      </Route>

      {/* Protected dashboard routes */}
      <Route path="/dashboard" element={
        <RequireAuth>
          <DashboardLayout />
        </RequireAuth>
      }>
        <Route index element={<Dashboard />} />
        <Route path="events" element={<EventsDashboard />} />
        <Route path="projects" element={<ProjectsDashboard />} />
        <Route path="people" element={<PeopleDashboard />} />
        <Route path="equipment" element={<EquipmentDashboard />} />
        <Route path="documents" element={<DocumentsDashboard />} />
        <Route path="users" element={
          <RequireSuperuser>
            <UsersDashboard />
          </RequireSuperuser>
        } />
        <Route path="audit" element={
          <RequireSuperuser>
            <AuditDashboard />
          </RequireSuperuser>
        } />
        <Route path="settings" element={
          <RequireSuperuser>
            <SettingsDashboard />
          </RequireSuperuser>
        } />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
