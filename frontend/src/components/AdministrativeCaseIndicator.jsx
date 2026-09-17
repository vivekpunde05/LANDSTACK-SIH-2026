import { useCallback, useEffect, useState } from 'react'
import { BriefcaseBusiness, LoaderCircle } from 'lucide-react'

export default function AdministrativeCaseIndicator({ parcelId, onViewCase }) {
  const [state, setState] = useState({ loading: true, item: null, error: '' })
  const load = useCallback(() => {
    setState({ loading: true, item: null, error: '' })
    fetch(`/api/cases?parcel_id=${encodeURIComponent(parcelId)}&limit=1`)
      .then((response) => response.ok ? response.json() : Promise.reject())
      .then((data) => setState({ loading: false, item: data.items[0] || null, error: '' }))
      .catch(() => setState({ loading: false, item: null, error: 'Administrative case status is unavailable. Ensure the local backend is running.' }))
  }, [parcelId])
  useEffect(() => { load() }, [load])
  if (state.loading) return <div className="flex items-center gap-2 rounded-xl border border-ink/10 p-3 text-[10px] text-ink/45"><LoaderCircle size={13} className="animate-spin" /> Checking administrative case…</div>
  if (state.error) return <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-[10px] text-rose-900"><p role="alert">{state.error}</p><button onClick={load} className="mt-2 rounded-lg border border-rose-300 px-3 py-2 font-bold">Retry</button></div>
  if (!state.item) return <div className="rounded-xl border border-ink/10 p-3 text-[10px] text-ink/50">No administrative case is linked to this parcel in the current session.</div>
  return <div className="rounded-xl border border-violet-200 bg-violet-50 p-3 text-[10px] text-violet-950"><div className="flex items-center gap-2 font-extrabold uppercase tracking-wider"><BriefcaseBusiness size={14} /> Administrative Case</div><p className="mt-2 text-sm font-extrabold">{state.item.case_id}</p><p className="mt-1">{state.item.case_status} · {state.item.review_stage}</p>{onViewCase && <button onClick={() => onViewCase(state.item.case_id)} className="mt-3 rounded-lg bg-violet-900 px-3 py-2 font-bold text-white">View Case</button>}</div>
}
