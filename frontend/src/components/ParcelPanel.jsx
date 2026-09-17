import { lazy, Suspense, useState } from 'react'
import { Building2, CalendarDays, CheckCircle2, FileText, LandPlot, MapPin, Ruler, X } from 'lucide-react'
import AdministrativeCaseIndicator from './AdministrativeCaseIndicator'

const SatelliteHistory = lazy(() => import('./SatelliteHistory'))
const PriorityTab = lazy(() => import('./PriorityTab'))
const InspectionsTab = lazy(() => import('./InspectionsTab'))
const GrievancesTab = lazy(() => import('./GrievancesTab'))

const tabs = ['Overview', 'Records', 'Satellite History', 'Priority', 'Inspections', 'Grievances']
const imageryParcels = new Set(['RTN-RAT-0001', 'RTN-RAT-0002', 'RTN-CHI-0013', 'RTN-SAN-0019'])
const tone = (value) => value === 'Verified' || value === 'Normal' || value === 'Active'
  ? 'bg-emerald-100 text-emerald-800'
  : value?.includes('Flagged') || value?.includes('Requires') ? 'bg-rose-100 text-rose-800' : 'bg-amber-100 text-amber-800'

function Row({ label, value, icon: Icon }) {
  return <div className="flex items-start gap-3 border-b border-ink/8 py-2.5 last:border-0"><Icon size={15} className="mt-0.5 shrink-0 text-moss" /><div><p className="text-[9px] font-bold uppercase tracking-wider text-ink/40">{label}</p><p className="mt-0.5 text-xs font-semibold text-ink">{value || 'Not available'}</p></div></div>
}

function Overview({ parcel, onViewCase }) {
  return <div className="space-y-3">
    <section className="rounded-xl bg-sand/65 p-3"><h3 className="text-[10px] font-extrabold uppercase tracking-widest text-moss">Location</h3><Row icon={MapPin} label="Village / Taluka" value={`${parcel.village} · ${parcel.taluka}`} /><Row icon={Building2} label="District" value={parcel.district} /></section>
    <section className="rounded-xl bg-sand/65 p-3"><h3 className="text-[10px] font-extrabold uppercase tracking-widest text-moss">Land information</h3><Row icon={Ruler} label="Area" value={`${parcel.area_hectares} hectares`} /><Row icon={LandPlot} label="Land type / Current use" value={`${parcel.land_type} · ${parcel.land_use}`} /></section>
    <section className="grid grid-cols-1 gap-2 sm:grid-cols-3 md:grid-cols-1">
      {[['Record status', parcel.record_status], ['Verification', parcel.verification_status], ['Review status', parcel.risk_status]].map(([label, value]) => <div key={label} className="rounded-xl border border-ink/10 p-3"><p className="text-[9px] font-bold uppercase tracking-wider text-ink/40">{label}</p><span className={`mt-1.5 inline-flex rounded-full px-2 py-1 text-[9px] font-bold ${tone(value)}`}>{value}</span></div>)}
    </section>
    {imageryParcels.has(parcel.parcel_id) && <div className="rounded-xl border border-blue-200 bg-blue-50 p-3 text-[10px] font-bold text-blue-900">Satellite analysis available for this demo parcel.</div>}
    <AdministrativeCaseIndicator parcelId={parcel.parcel_id} onViewCase={onViewCase} />
    <div className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-[10px] leading-relaxed text-amber-900"><strong>Dataset notice:</strong> Synthetic demonstration data only. No legal or cadastral validity.</div>
  </div>
}

function Records({ parcel }) {
  return <div><div className="mb-3 flex items-start gap-2 rounded-xl bg-blue-50 p-3 text-[10px] leading-relaxed text-blue-900"><FileText size={16} className="shrink-0" /><strong>Demo record only — not an official government cadastral record.</strong></div><div className="rounded-xl border border-ink/10 px-3"><Row icon={FileText} label="Record reference" value={parcel.record_reference} /><Row icon={FileText} label="Record type" value={parcel.record_type} /><Row icon={CheckCircle2} label="Record status" value={parcel.record_status} /><Row icon={Building2} label="Source" value={parcel.source_label} /><Row icon={CalendarDays} label="Last updated" value={new Date(parcel.updated_at).toLocaleString()} /></div></div>
}

export default function ParcelPanel({ parcel, onClose, initialTab = 'Overview', onViewCase }) {
  const [activeTab, setActiveTab] = useState(initialTab)
  if (!parcel) return null
  const content = activeTab === 'Overview' ? <Overview parcel={parcel} onViewCase={onViewCase} /> : activeTab === 'Records' ? <Records parcel={parcel} /> : activeTab === 'Satellite History' ? <SatelliteHistory parcel={parcel} /> : activeTab === 'Priority' ? <PriorityTab parcel={parcel} /> : activeTab === 'Inspections' ? <InspectionsTab parcel={parcel} /> : <GrievancesTab parcel={parcel} />
  return <aside className="absolute inset-x-2 bottom-2 z-20 max-h-[78vh] overflow-hidden rounded-2xl border border-white/60 bg-white/97 shadow-panel backdrop-blur md:inset-x-auto md:bottom-3 md:right-3 md:top-3 md:w-[390px]">
    <div className="flex items-start justify-between bg-ink px-4 py-4 text-white"><div><p className="text-[9px] font-extrabold uppercase tracking-[.18em] text-lime">Parcel Intelligence</p><h2 className="mt-1 font-display text-lg font-extrabold">{parcel.parcel_id}</h2><p className="mt-0.5 text-[10px] text-white/55">Survey {parcel.survey_number}</p></div><button onClick={onClose} className="rounded-xl bg-white/10 p-2 hover:bg-white/20" aria-label="Close details"><X size={18} /></button></div>
    <div className="flex overflow-x-auto border-b border-ink/10 bg-white px-2" role="tablist">{tabs.map((tab) => <button key={tab} role="tab" aria-selected={activeTab === tab} onClick={() => setActiveTab(tab)} className={`shrink-0 border-b-2 px-2.5 py-3 text-[9px] font-bold ${activeTab === tab ? 'border-moss text-moss' : 'border-transparent text-ink/40'}`}>{tab}</button>)}</div>
    <div className="max-h-[calc(78vh-125px)] overflow-auto p-4"><Suspense fallback={<div className="grid min-h-56 place-items-center text-xs text-ink/55" role="status">Loading parcel intelligence…</div>}>{content}</Suspense></div>
  </aside>
}
