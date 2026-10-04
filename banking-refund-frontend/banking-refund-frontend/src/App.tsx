import { Navigate, Route, Routes } from "react-router-dom";
import { ProtectedRoute, PublicRoute } from "./app/router/guards";
import { AppShell } from "./components/layout/AppShell";
import { LoginPage } from "./features/auth/LoginPage";
import { SignupPage } from "./features/auth/SignupPage";
import { CustomerDashboard } from "./features/customer/CustomerDashboard";
import { RefundsPage } from "./features/customer/RefundsPage";
import { AdminDashboard } from "./features/admin/AdminDashboard";
import { DeveloperAuditPage } from "./features/developer/DeveloperAuditPage";
import { useAuth } from "./features/auth/AuthContext";

function HomeRedirect() {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (user.role === "ADMIN") return <Navigate to="/admin" replace />;
  if (user.role === "DEVELOPER") return <Navigate to="/developer" replace />;
  return <Navigate to="/dashboard" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route element={<PublicRoute />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route element={<AppShell />}>
          <Route path="/" element={<HomeRedirect />} />
          <Route path="/dashboard" element={<CustomerDashboard />} />
          <Route path="/refunds" element={<RefundsPage />} />

          <Route element={<ProtectedRoute roles={["ADMIN"]} />}>
            <Route path="/admin" element={<AdminDashboard />} />
          </Route>

          <Route element={<ProtectedRoute roles={["DEVELOPER"]} />}>
            <Route path="/developer" element={<DeveloperAuditPage />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
