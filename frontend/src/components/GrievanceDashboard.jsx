import { useCallback, useEffect, useMemo, useState } from 'react'
import { AlertCircle, BriefcaseBusiness, Eye, LoaderCircle, MapPin, RotateCcw, Search } from 'lucide-react'
import { buildFallbackParcels } from '../data/fallbackParcels'
import { grievanceCategories, grievanceStatuses } from '../data/grievanceOptions'
import GrievanceForm from './GrievanceForm'

const emptyFilters = { status: '', category: '', taluka: '' }

export default function GrievanceDashboard({ onViewParcel, onViewCase }) {
  const parcelFeatures = useMemo(() => buildFallbackParcels().features, [])
  const [parcelSearch, setParcelSearch] = useState('')
  const [formParcel, setFormParcel] = useState(null)
  const [items, setItems] = useState(null)
  const [queueError, setQueueError] = useState('')
  const [filters, setFilters] = useState(emptyFilters)
  const [trackingReference, setTrackingReference] = useState('')
  const [tracking, setTracking] = useState({ state: 'idle', result: null, message: '' })
  const [caseAction, setCaseAction] = useState({ grievanceId: '', error: '' })
  const loadQueue = useCallback(() => {
    setQueueError('')
    fetch('/api/grievances?limit=100').then((response) => { if (!response.ok) throw new Error(); return response.json() }).then((data) => setItems(data.items)).catch(() => setQueueError('Grievance queue is unavailable. Ensure the local backend is running.'))
  }, [])
  useEffect(() => { loadQueue() }, [loadQueue])
  const parcelResults = useMemo(() => {
    const term = parcelSearch.trim().toLowerCase()
    if (!term) return []
    return parcelFeatures.filter(({ properties }) => [properties.parcel_id, properties.survey_number, properties.village].some((value) => value.toLowerCase().includes(term))).slice(0, 6)
  }, [parcelFeatures, parcelSearch])
  const visible = useMemo(() => (items || []).filter((item) => (!filters.status || item.status === filters.status) && (!filters.category || item.category === filters.category) && (!filters.taluka || item.taluka === filters.taluka)), [items, filters])
  const track = async () => {
    const reference = trackingReference.trim().toUpperCase()
    if (!reference) { setTracking({ state: 'error', result: null, message: 'Enter a grievance reference.' }); return }
    setTracking({ state: 'loading', result: null, message: '' })
    try {
      const response = await fetch(`/api/grievances/${encodeURIComponent(reference)}`)
      if (response.status === 404) { setTracking({ state: 'error', result: null, message: 'No grievance found for this reference.' }); return }
      if (!response.ok) throw new Error()
      setTracking({ state: 'success', result: await response.json(), message: '' })
    } catch { setTracking({ state: 'error', result: null, message: 'Tracking is unavailable. Ensure the local backend is running.' }) }
  }
  const submitted = (result) => {
    setTrackingReference(result.grievance_id)
    setTracking({ state: 'success', result, message: '' })
    loadQueue()
  }
  const openCase = async (item) => {
    if (item.administrative_case) { onViewCase(item.administrative_case.case_id); return }
    if (caseAction.grievanceId) return
    setCaseAction({ grievanceId: item.grievance_id, error: '' })
    try {
      const key = globalThis.crypto?.randomUUID?.().replaceAll('-', '') || `opencase${Date.now()}`
      const response = await fetch(`/api/grievances/${encodeURIComponent(item.grievance_id)}/case`, { method: 'POST', headers: { 'X-Idempotency-Key': key } })
      const body = await response.json()
      if (!response.ok) throw new Error(body.detail?.message || 'Administrative case could not be opened.')
      loadQueue(); onViewCase(body.case_id)
    } catch (error) { setCaseAction({ grievanceId: '', error: error.message || 'Administrative case could not be opened.' }); return }
    setCaseAction({ grievanceId: '', error: '' })
  }

  return <div className="space-y-4">
    <div className="grid gap-4 xl:grid-cols-2">
      <section className="rounded-2xl border border-ink/10 bg-white p-4"><p className="text-[9px] font-extrabold uppercase tracking-widest text-moss">Citizen entry point</p><h3 className="mt-1 font-display text-lg font-extrabold">Report a Parcel Concern</h3><p className="mt-1 text-[10px] text-ink/50">Search by parcel ID, survey number, or village. No personal contact information is required.</p><label className="mt-4 flex h-11 items-center gap-2 rounded-xl border border-ink/15 px-3"><Search size={16} className="text-moss" /><input aria-label="Citizen parcel search" value={parcelSearch} onChange={(event) => setParcelSearch(event.target.value)} placeholder="Search parcel ID, survey number, or village…" className="min-w-0 flex-1 bg-transparent text-xs outline-none" /></label><div className="mt-2 space-y-2">{parcelResults.map(({ properties }) => <button key={properties.parcel_id} onClick={() => setFormParcel(properties)} className="flex w-full items-center justify-between gap-3 rounded-xl bg-sand/60 p-3 text-left"><span><strong className="block text-xs">{properties.parcel_id} · {properties.survey_number}</strong><span className="text-[9px] text-ink/50">{properties.village} · {properties.taluka}</span></span><span className="shrink-0 text-[9px] font-bold text-moss">Submit grievance</span></button>)}{parcelSearch.trim() && parcelResults.length === 0 && <p className="rounded-xl bg-amber-50 p-3 text-xs text-amber-900">No matching synthetic parcel found.</p>}</div></section>
      <section className="rounded-2xl border border-ink/10 bg-white p-4"><p className="text-[9px] font-extrabold uppercase tracking-widest text-moss">Track grievance</p><h3 className="mt-1 font-display text-lg font-extrabold">Check Current Status</h3><div className="mt-4 flex gap-2"><input aria-label="Grievance reference" value={trackingReference} onChange={(event) => setTrackingReference(event.target.value)} placeholder="GRV-2026-0001" className="h-11 min-w-0 flex-1 rounded-xl border border-ink/15 px-3 text-xs uppercase" /><button onClick={track} disabled={tracking.state === 'loading'} className="h-11 rounded-xl bg-ink px-5 text-xs font-bold text-white disabled:opacity-60">{tracking.state === 'loading' ? 'Checking…' : 'Track'}</button></div>{tracking.state === 'error' && <p role="alert" className="mt-3 rounded-xl bg-rose-50 p-3 text-xs text-rose-800">{tracking.message}</p>}{tracking.result && <div className="mt-3 rounded-xl bg-sand/65 p-3 text-xs"><p className="font-display text-base font-extrabold">{tracking.result.grievance_id}</p><div className="mt-2 grid grid-cols-2 gap-2 text-[10px]"><p><span className="text-ink/45">Parcel</span><strong className="block">{tracking.result.parcel_id}</strong></p><p><span className="text-ink/45">Status</span><strong className="block">{tracking.result.status}</strong></p><p><span className="text-ink/45">Category</span><strong className="block">{tracking.result.category}</strong></p><p><span className="text-ink/45">Submitted</span><strong className="block">{new Date(tracking.result.submitted_at).toLocaleString()}</strong></p></div>{tracking.result.administrative_case && <div className="mt-3 rounded-lg border border-violet-200 bg-violet-50 p-2 text-[10px] text-violet-950"><strong>{tracking.result.administrative_case.case_id}</strong><p>{tracking.result.administrative_case.case_status} · {tracking.result.administrative_case.review_stage}</p><p className="text-[9px] opacity-65">Updated {new Date(tracking.result.administrative_case.updated_at).toLocaleString()}</p>{tracking.result.administrative_case.resolution_type && <p className="mt-1">Resolution: {tracking.result.administrative_case.resolution_type}</p>}</div>}<p className="mt-2 text-[9px] text-ink/50">Last updated: {new Date(tracking.result.updated_at).toLocaleString()}</p></div>}</section>
    </div>
    <div className="rounded-xl border border-blue-200 bg-blue-50 p-3 text-[10px] text-blue-900">Citizen-submitted information requires official verification and does not constitute a legal determination.</div>
    {caseAction.error && <p role="alert" className="rounded-xl bg-rose-50 p-3 text-xs text-rose-800">{caseAction.error}</p>}
    <section className="rounded-2xl border border-ink/10 bg-white p-4"><div className="flex items-center justify-between"><div><p className="text-[9px] font-extrabold uppercase tracking-widest text-moss">Officer view</p><h3 className="font-display text-lg font-extrabold">Grievance Queue</h3></div><button onClick={() => setFilters(emptyFilters)} className="flex items-center gap-1 text-[10px] font-bold text-moss"><RotateCcw size={13} /> Clear filters</button></div><div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-3"><select aria-label="Grievance status filter" value={filters.status} onChange={(event) => setFilters((current) => ({ ...current, status: event.target.value }))} className="h-10 rounded-xl border border-ink/15 px-3 text-xs"><option value="">All statuses</option>{grievanceStatuses.map((value) => <option key={value}>{value}</option>)}</select><select aria-label="Grievance category filter" value={filters.category} onChange={(event) => setFilters((current) => ({ ...current, category: event.target.value }))} className="h-10 rounded-xl border border-ink/15 px-3 text-xs"><option value="">All categories</option>{grievanceCategories.map((value) => <option key={value}>{value}</option>)}</select><select aria-label="Grievance taluka filter" value={filters.taluka} onChange={(event) => setFilters((current) => ({ ...current, taluka: event.target.value }))} className="h-10 rounded-xl border border-ink/15 px-3 text-xs"><option value="">All talukas</option>{['Ratnagiri', 'Chiplun', 'Sangameshwar'].map((value) => <option key={value}>{value}</option>)}</select></div></section>
    {queueError ? <div className="flex items-center justify-between gap-3 rounded-xl bg-rose-50 p-4 text-xs text-rose-800"><span className="flex items-center gap-2"><AlertCircle size={16} />{queueError}</span><button onClick={loadQueue} className="shrink-0 rounded-lg border border-rose-300 px-3 py-2 font-bold">Retry</button></div> : !items ? <div className="grid min-h-48 place-items-center rounded-2xl bg-white text-xs text-ink/50"><span className="flex items-center gap-2"><LoaderCircle size={16} className="animate-spin" /> Loading grievance queue…</span></div> : <section className="overflow-hidden rounded-2xl border border-ink/10 bg-white"><div className="border-b border-ink/10 px-4 py-3 text-[10px] text-ink/50">Newest first · {visible.length} grievances</div><div className="overflow-x-auto"><table className="w-full min-w-[980px] text-left text-xs"><thead className="bg-sand/70 text-[9px] uppercase tracking-wider text-ink/45"><tr>{['Grievance ID', 'Parcel', 'Village', 'Category', 'Status', 'Submitted', 'Evidence', 'Actions'].map((heading) => <th key={heading} className="px-4 py-3">{heading}</th>)}</tr></thead><tbody className="divide-y divide-ink/8">{visible.map((item) => <tr key={item.grievance_id}><td className="px-4 py-3 font-bold">{item.grievance_id}</td><td className="px-4 py-3">{item.parcel_id}</td><td className="px-4 py-3">{item.village}</td><td className="px-4 py-3">{item.category}</td><td className="px-4 py-3"><span className="rounded-full bg-blue-100 px-2 py-1 text-[9px] font-bold text-blue-800">{item.status}</span></td><td className="px-4 py-3">{new Date(item.submitted_at).toLocaleDateString()}</td><td className="px-4 py-3">{item.evidence_count}</td><td className="px-4 py-3"><div className="flex gap-1"><button onClick={() => onViewParcel(item)} className="flex items-center gap-1 rounded-lg border border-ink/15 px-2 py-2 text-[9px] font-bold"><Eye size={12} /> Parcel</button><button onClick={() => openCase(item)} disabled={caseAction.grievanceId === item.grievance_id} className="flex items-center gap-1 rounded-lg bg-ink px-2 py-2 text-[9px] font-bold text-white disabled:opacity-50"><BriefcaseBusiness size={12} />{caseAction.grievanceId === item.grievance_id ? 'Opening…' : item.administrative_case ? 'View Case' : 'Open Case'}</button></div></td></tr>)}</tbody></table>{visible.length === 0 && <p className="p-8 text-center text-xs text-ink/50">No grievances match the current filters.</p>}</div></section>}
    <p className="flex items-start gap-2 rounded-xl bg-amber-50 p-3 text-[10px] text-amber-900"><MapPin size={14} className="shrink-0" />Field verification may be recommended after administrative review. No inspection is created automatically.</p>
    {formParcel && <GrievanceForm parcel={formParcel} completionLabel="Return to grievance workspace" onCompleted={submitted} onClose={() => { setFormParcel(null); loadQueue() }} />}
  </div>
}
