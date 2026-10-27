import { Route, Routes } from "react-router-dom";
import Systems from "./pages/Systems";
import Login from "./pages/Login";
import EnrollPasskey from "./pages/EnrollPasskey";
import Sessions from "./pages/Sessions";
import Recovery from "./pages/Recovery";
import Home from "./pages/Home";
import ResourceView from "./pages/ResourceView";
import Policies from "./pages/Policies";
import Dashboard from "./pages/Dashboard";
import EventDetail from "./pages/EventDetail";

export default function App() {
  return (
    <Routes>
      <Route path="/systems" element={<Systems />} />
      <Route path="/login" element={<Login />} />
      <Route path="/passkeys" element={<EnrollPasskey />} />
      <Route path="/sessions" element={<Sessions />} />
      <Route path="/recovery" element={<Recovery />} />
      <Route path="/" element={<Home />} />
      <Route path="/resources/:id" element={<ResourceView />} />
      <Route path="/admin/policies" element={<Policies />} />
      <Route path="/admin/dashboard" element={<Dashboard />} />
      <Route path="/admin/events/:id" element={<EventDetail />} />
    </Routes>
  );
}
