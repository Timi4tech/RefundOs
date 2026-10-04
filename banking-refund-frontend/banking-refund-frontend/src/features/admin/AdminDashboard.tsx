import { useEffect, useState, type ReactNode } from "react";
import { Search, SlidersHorizontal, CheckCircle2, XCircle, AlertTriangle, Ticket } from "lucide-react";
import api from "../../lib/api";
import type { Paginated, Refund, RefundStatus } from "../../types";
import { StatusBadge } from "../../components/ui/StatusBadge";
import { Pagination } from "../../components/ui/Pagination";

const statuses: RefundStatus[] = ["PENDING","PROCESSING","APPROVED","REJECTED","REQUIRES_REVIEW","COMPLETED","FAILED"];

export function AdminDashboard() {
  const [data, setData] = useState<Paginated<Refund>>({items:[],total:0,page:1,page_size:10,total_pages:1});
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState("");
  const [ticketId, setTicketId] = useState("");
  const [date, setDate] = useState("");
  const [summary, setSummary] = useState({ created: 0, approved: 0, rejected: 0, escalated: 0 });

  async function load() {
    const [refundsResponse, summaryResponse] = await Promise.all([
      api.get("/admin/refunds", {
        params: {
          page,
          page_size: 10,
          status: status || undefined,
          refund_id: ticketId || undefined,
          created_date: date || undefined
        }
      }),
      api.get("/admin/refunds/summary")
    ]);

    setData(refundsResponse.data);
    setSummary(summaryResponse.data);
  }

  useEffect(() => { load().catch(() => undefined); }, [page, status, date]);

  return (
    <div className="mx-auto max-w-7xl">
      <div className="mb-7"><p className="text-sm font-semibold text-teal">Admin console</p><h2 className="mt-1 text-3xl font-bold tracking-tight">Refund operations</h2><p className="mt-2 text-sm text-slate-500">Search, review, and monitor refund tickets.</p></div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Metric icon={<Ticket size={19}/>} label="Created tickets" value={summary.created} />
        <Metric icon={<CheckCircle2 size={19}/>} label="Approved" value={summary.approved} />
        <Metric icon={<XCircle size={19}/>} label="Rejected" value={summary.rejected} />
        <Metric icon={<AlertTriangle size={19}/>} label="Escalated" value={summary.escalated} />
      </div>

      <div className="panel mt-6 p-4">
        <div className="mb-4 flex items-center gap-2 font-semibold"><SlidersHorizontal size={17}/> Ticket search</div>
        <div className="grid gap-3 md:grid-cols-3">
          <div className="relative"><Search className="absolute left-3 top-3 text-slate-400" size={17}/><input className="input pl-10" placeholder="Refund ticket ID" value={ticketId} onChange={e=>setTicketId(e.target.value)} onKeyDown={e=>e.key==="Enter"&&load()}/></div>
          <select className="input" value={status} onChange={e=>{setPage(1);setStatus(e.target.value)}}><option value="">All statuses</option>{statuses.map(s=><option key={s} value={s}>{s.replaceAll("_"," ")}</option>)}</select>
          <input className="input" type="date" value={date} onChange={e=>{setPage(1);setDate(e.target.value)}} />
        </div>
      </div>

      <div className="panel mt-6 overflow-hidden">
        <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="bg-slate-50 text-xs uppercase text-slateText-500"><tr><th className="px-5 py-3">Ticket</th><th className="px-5 py-3">Customer</th><th className="px-5 py-3">Amount</th><th className="px-5 py-3">Status</th><th className="px-5 py-3">Created</th></tr></thead><tbody>
          {data.items.map(r=><tr key={r.id} className="border-t border-slateText-100 hover:bg-slateText-50"><td className="px-5 py-4 font-semibold">{r.id.slice(0,12)}…</td><td className="px-5 py-4 text-slateText-500">{r.user_id.slice(0,12)}…</td><td className="px-5 py-4">{r.currency} {Number(r.amount).toLocaleString()}</td><td className="px-5 py-4"><StatusBadge status={r.status}/></td><td className="px-5 py-4 text-slateText-500">{new Date(r.created_at).toLocaleString()}</td></tr>)}
        </tbody></table></div>
        {data.items.length===0 && <div className="p-10 text-center text-sm text-slateText-400">No tickets match your filters.</div>}
        <Pagination page={data.page} totalPages={data.total_pages} onChange={setPage}/>
      </div>
    </div>
  );
}

function Metric({icon,label,value}:{icon:ReactNode;label:string;value:number}) {
  return <div className="panel p-5"><div className="mb-5 grid h-10 w-10 place-items-center rounded-xl bg-teal/10 text-teal">{icon}</div><p className="text-sm text-slateText-500">{label}</p><p className="mt-1 text-3xl font-bold">{value}</p></div>;
}
