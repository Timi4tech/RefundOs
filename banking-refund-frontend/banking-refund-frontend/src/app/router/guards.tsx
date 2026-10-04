import { Navigate, Outlet, useLocation } from "react-router-dom";
import type { Role } from "../../types";
import { useAuth } from "../../features/auth/AuthContext";

export function PublicRoute() {
  const { user } = useAuth();
  return user ? <Navigate to="/" replace /> : <Outlet />;
}

export function ProtectedRoute({ roles }: { roles?: Role[] }) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
