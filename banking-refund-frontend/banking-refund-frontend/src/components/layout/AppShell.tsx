import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { LogOut, ShieldCheck, LayoutDashboard, ReceiptText, Code2 } from "lucide-react";
import { useAuth } from "../../features/auth/AuthContext";

function linkClass({ isActive }: { isActive: boolean }) {
  return `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
    isActive ? "bg-teal/10 text-teal" : "text-slateText-600 hover:bg-slate-50 hover:text-ink"
  }`;
}

export function AppShell() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-50">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 border-r border-slateText-200 bg-white lg:flex lg:flex-col">
        <div className="flex h-20 items-center gap-3 border-b border-slateText-100 px-6">
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-navy text-white">
            <ShieldCheck size={21} />
          </div>
          <div>
            <p className="font-bold tracking-tight">RefundOS</p>
            <p className="text-xs text-slateText-400">Refund operations</p>
          </div>
        </div>

        <nav className="flex-1 space-y-1 p-4">
          {user?.role === "CUSTOMER" && (
            <>
              <NavLink className={linkClass} to="/dashboard"><LayoutDashboard size={18} /> Dashboard</NavLink>
              <NavLink className={linkClass} to="/refunds"><ReceiptText size={18} /> My refunds</NavLink>
            </>
          )}

          {user?.role === "ADMIN" && (
            <NavLink className={linkClass} to="/admin"><ShieldCheck size={18} /> Admin console</NavLink>
          )}

          {user?.role === "DEVELOPER" && (
            <NavLink className={linkClass} to="/developer"><Code2 size={18} /> Audit logs</NavLink>
          )}
        </nav>

        <div className="border-t border-slateText-100 p-4">
          <div className="mb-3 rounded-xl bg-slate-50 p-3">
            <p className="truncate text-sm font-semibold">{user?.name}</p>
            <p className="truncate text-xs text-slateText-500">{user?.email}</p>
            <span className="mt-2 inline-flex rounded-full bg-teal/10 px-2 py-1 text-[10px] font-bold uppercase tracking-wide text-teal">
              {user?.role}
            </span>
          </div>
          <button
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slateText-600 hover:bg-red-50 hover:text-danger"
            onClick={() => { logout(); navigate("/login"); }}
          >
            <LogOut size={18} /> Sign out
          </button>
        </div>
      </aside>

      <main className="lg:pl-64">
        <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 px-5 py-4 backdrop-blur lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal">Secure workspace</p>
              <h1 className="mt-1 text-xl font-bold tracking-tight text-ink">
                {user?.role === "ADMIN" ? "Refund administration" : user?.role === "DEVELOPER" ? "System audit" : "Your banking workspace"}
              </h1>
            </div>
            <div className="hidden rounded-full border border-slateText-200 bg-white px-3 py-1.5 text-xs font-semibold text-slateText-600 sm:block">
              Protected session
            </div>
          </div>
        </header>

        <div className="p-5 lg:p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
