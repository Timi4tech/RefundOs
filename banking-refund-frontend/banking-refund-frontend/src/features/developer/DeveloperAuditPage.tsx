import { useEffect, useState } from "react";
import { Code2, Search } from "lucide-react";
import api from "../../lib/api";
import type { AuditLog, Paginated } from "../../types";
import { Pagination } from "../../components/ui/Pagination";

export function DeveloperAuditPage() {
  const [data,setData] = useState<Paginated<AuditLog>>({items:[],total:0,page:1,page_size:15,total_pages:1});
  const [page,setPage] = useState(1);
  const [date,setDate] = useState("");

  async function load() {
    const {data} = await api.get("/developer/audit-logs",{params:{page,page_size:15,created_date:date||undefined}});
    setData(data);
  }
  useEffect(()=>{load().catch(() => undefined)},[page,date]);

  return (
    <div className="mx-auto max-w-7xl">
      <div className="mb-7"><p className="text-sm font-semibold text-teal">Developer workspace</p><h2 className="mt-1 text-3xl font-bold tracking-tight">Audit logs</h2><p className="mt-2 text-sm text-slate-500">Read-only operational events for debugging and system observability.</p></div>
      <div className="panel overflow-hidden">
        <div className="flex flex-col justify-between gap-3 border-b border-slateText-100 p-4 sm:flex-row"><div className="flex items-center gap-2 font-semibold"><Code2 size={18}/> System events</div><div className="relative"><Search className="absolute left-3 top-3 text-slateText-400" size={16}/><input className="input pl-9 sm:w-64" type="date" value={date} onChange={e=>{setPage(1);setDate(e.target.value)}} /></div></div>
        <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="bg-slate-50 text-xs uppercase text-slateText-500"><tr><th className="px-5 py-3">Time</th><th className="px-5 py-3">Action</th><th className="px-5 py-3">Actor</th><th className="px-5 py-3">Refund</th><th className="px-5 py-3">Note</th></tr></thead><tbody>{data.items.map(log=><tr key={log.id} className="border-t border-slateText-100"><td className="whitespace-nowrap px-5 py-4 text-slateText-500">{new Date(log.created_at).toLocaleString()}</td><td className="px-5 py-4 font-semibold">{log.action}</td><td className="px-5 py-4">{log.actor_type}</td><td className="px-5 py-4 font-mono text-xs">{log.refund_id?.slice(0,12) ?? "—"}</td><td className="max-w-md px-5 py-4 text-slateText-500">{log.note}</td></tr>)}</tbody></table></div>
        {data.items.length===0 && <div className="p-10 text-center text-sm text-slateText-400">No audit logs found.</div>}
        <Pagination page={data.page} totalPages={data.total_pages} onChange={setPage}/>
      </div>
    </div>
  );
}
