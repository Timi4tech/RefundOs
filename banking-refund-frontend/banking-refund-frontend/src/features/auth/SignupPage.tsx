import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, ShieldCheck } from "lucide-react";
import { useAuth } from "./AuthContext";

export function SignupPage() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault(); setError(""); setBusy(true);
    try {
      const user = await signup(name, email, password);
      navigate(user.role === "ADMIN" ? "/admin" : user.role === "DEVELOPER" ? "/developer" : "/dashboard", { replace: true });
    } catch (err: any) {
      setError(err.response?.data?.detail ?? "Unable to create account.");
    } finally { setBusy(false); }
  }

  return (
    <div className="grid min-h-screen lg:grid-cols-[.8fr_1.2fr] bg-slate-50">
      <div className="hidden bg-navy p-12 text-white lg:flex lg:flex-col lg:justify-between">
        <div className="flex items-center gap-3"><div className="grid h-11 w-11 place-items-center rounded-xl bg-white/10"><ShieldCheck /></div><b>RefundOS</b></div>
        <div><p className="text-sm font-semibold uppercase tracking-[.2em] text-teal-200">Secure by design</p><h1 className="mt-4 text-4xl font-bold leading-tight">One workspace for customers and trusted operators.</h1><p className="mt-5 text-white/60">Every role sees only the tools and records appropriate to its responsibility.</p></div>
        <p className="text-xs text-white/40">Refund operations platform</p>
      </div>

      <div className="flex items-center justify-center p-6">
        <form onSubmit={submit} className="w-full max-w-md">
          <h2 className="text-3xl font-bold tracking-tight">Create your account</h2>
          <p className="mt-2 text-sm text-slateText-500">Your access level is assigned by the backend.</p>
          {error && <div className="mt-5 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
          <div className="mt-7 space-y-5">
            <div><label className="label">Full name</label><input className="input" required value={name} onChange={(e) => setName(e.target.value)} /></div>
            <div><label className="label">Email</label><input className="input" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></div>
            <div><label className="label">Password</label><input className="input" type="password" minLength={8} required value={password} onChange={(e) => setPassword(e.target.value)} /></div>
            <button className="btn-primary w-full py-3.5" disabled={busy}>{busy ? "Creating…" : "Create account"} {!busy && <ArrowRight size={17} />}</button>
          </div>
          <p className="mt-7 text-center text-sm text-slateText-500">Already registered? <Link className="font-semibold text-teal hover:underline" to="/login">Sign in</Link></p>
        </form>
      </div>
    </div>
  );
}
