import { ArrowUpRight, Clock3, ShieldCheck, WalletCards } from "lucide-react";
import { ChatWidget } from "../../components/chat/ChatWidget";

export function CustomerDashboard() {
  return (
    <div className="mx-auto max-w-7xl">
      <div className="mb-8 flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div><p className="text-sm font-semibold text-teal">Overview</p><h2 className="mt-1 text-3xl font-bold tracking-tight">Good to see you.</h2><p className="mt-2 text-sm text-slateText-500">Track your refund requests and get help when you need it.</p></div>
        <a className="btn-primary" href="/refunds">View refunds <ArrowUpRight size={17} /></a>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="panel p-5"><div className="mb-6 grid h-10 w-10 place-items-center rounded-xl bg-teal/10 text-teal"><WalletCards size={19}/></div><p className="text-sm text-slateText-500">Refund requests</p><p className="mt-1 text-3xl font-bold">—</p><p className="mt-2 text-xs text-slateText-400">Live from your account</p></div>
        <div className="panel p-5"><div className="mb-6 grid h-10 w-10 place-items-center rounded-xl bg-amber-50 text-amber-700"><Clock3 size={19}/></div><p className="text-sm text-slateText-500">Awaiting review</p><p className="mt-1 text-3xl font-bold">—</p><p className="mt-2 text-xs text-slateText-400">Pending or escalated</p></div>
        <div className="panel p-5"><div className="mb-6 grid h-10 w-10 place-items-center rounded-xl bg-emerald-50 text-emerald-700"><ShieldCheck size={19}/></div><p className="text-sm text-slateText-500">Account status</p><p className="mt-1 text-3xl font-bold">Secure</p><p className="mt-2 text-xs text-slateText-400">Authenticated session</p></div>
      </div>

      <div className="mt-6 panel p-6"><h3 className="font-bold">How refunds are handled</h3><div className="mt-5 grid gap-4 md:grid-cols-4">{["Submit request","Policy checks","AI analysis","Final decision"].map((x, i) => <div key={x} className="rounded-xl bg-slate-50 p-4"><span className="text-xs font-bold text-teal">0{i+1}</span><p className="mt-2 text-sm font-semibold">{x}</p><p className="mt-1 text-xs leading-5 text-slateText-500">Your request moves through a controlled, auditable process.</p></div>)}</div></div>
      <ChatWidget />
    </div>
  );
}
