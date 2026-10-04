import { FormEvent, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { ArrowRight, LockKeyhole, ShieldCheck } from "lucide-react";
import { useAuth } from "./AuthContext";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const user = await login(email, password);
      const requested = (location.state as { from?: string } | null)?.from;
      navigate(requested ?? (user.role === "ADMIN" ? "/admin" : user.role === "DEVELOPER" ? "/developer" : "/dashboard"), { replace: true });
    } catch (err: any) {
      setError(err.response?.data?.detail ?? "Unable to sign in.");
    } finally { setBusy(false); }
  }

  return (
    <div className="min-h-screen bg-navy">
      <div className="grid min-h-screen lg:grid-cols-[1.05fr_.95fr]">
        <div className="hidden flex-col justify-between p-12 text-white lg:flex">
          <div className="flex items-center gap-3"><div className="grid h-11 w-11 place-items-center rounded-xl bg-white/10"><ShieldCheck /></div><b>RefundOS</b></div>
          <div className="max-w-xl">
            <p className="mb-4 text-sm font-semibold uppercase tracking-[.2em] text-teal-200">Refund intelligence</p>
            <h1 className="text-5xl font-bold leading-tight">A calmer way to manage sensitive refund decisions.</h1>
            <p className="mt-6 max-w-lg text-lg leading-8 text-white/60">Secure customer support, operational review, AI-assisted analysis, and a complete audit trail in one workspace.</p>
          </div>
          <p className="text-xs text-white/40">Protected banking operations workspace</p>
        </div>

        <div className="flex items-center justify-center bg-slate-50 p-6">
          <form onSubmit={submit} className="w-full max-w-md">
            <div className="mb-8 lg:hidden"><b className="text-xl">RefundOS</b></div>
            <p className="text-sm font-semibold text-teal">Welcome back</p>
            <h2 className="mt-1 text-3xl font-bold tracking-tight">Sign in to your workspace</h2>
            <p className="mt-2 text-sm text-slate-500">Use your registered account to continue.</p>

            {error && <div className="mt-5 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

            <div className="mt-7 space-y-5">
              <div><label className="label">Email</label><input className="input" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" /></div>
              <div><label className="label">Password</label><input className="input" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" /></div>
              <button className="btn-primary w-full py-3.5" disabled={busy}>{busy ? "Signing in…" : "Sign in"} {!busy && <ArrowRight size={17} />}</button>
            </div>

            <p className="mt-7 text-center text-sm text-slate-500">New here? <Link className="font-semibold text-teal hover:underline" to="/signup">Create an account</Link></p>
          </form>
        </div>
      </div>
    </div>
  );
}
