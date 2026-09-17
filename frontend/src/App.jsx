import { lazy, Suspense, useEffect, useMemo, useRef, useState } from 'react'
import { AlertTriangle, BarChart3, BriefcaseBusiness, ClipboardList, LandPlot, Map, Menu, MessageSquareWarning, Play, ShieldCheck, Wifi, X } from 'lucide-react'
import DemoGuide from './components/DemoGuide'
import MapView from './components/MapView'
import SearchFilters from './components/SearchFilters'
import { buildFallbackParcels, filterFallbackParcels } from './data/fallbackParcels'

const CaseDashboard = lazy(() => import('./components/CaseDashboard'))
const CaseDetail = lazy(() => import('./components/CaseDetail'))
const GovernanceAnalytics = lazy(() => import('./components/GovernanceAnalytics'))
const GrievanceDashboard = lazy(() => import('./components/GrievanceDashboard'))
const InspectionForm = lazy(() => import('./components/InspectionForm'))
const PriorityDashboard = lazy(() => import('./components/PriorityDashboard'))

const emptyFilters = { search: '', taluka: '', land_use: '', verification_status: '', risk_status: '' }
const nav = [
  { id: 'map', label: 'GIS Explorer', icon: Map },
  { id: 'priority', label: 'Inspection Priority', icon: ClipboardList },
  { id: 'grievances', label: 'Citizen Grievances', icon: MessageSquareWarning },
  { id: 'cases', label: 'Administrative Review', icon: BriefcaseBusiness },
  { id: 'analytics', label: 'Governance Analytics', icon: BarChart3 },
]

const AsyncView = () => <div className="grid min-h-[420px] place-items-center rounded-3xl bg-white text-sm text-ink/55" role="status">Loading workspace…</div>
const AsyncModal = () => <div className="fixed inset-0 z-[100] grid place-items-center bg-black/60" role="status"><span className="rounded-xl bg-white px-5 py-4 text-xs font-bold text-ink">Loading workflow…</span></div>

function Sidebar({ open, close, view, onNavigate, onStartDemo }) {
  return <aside className={`${open ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-ink p-5 text-white transition-transform lg:static lg:translate-x-0`}>
    <div className="flex items-center justify-between"><div className="flex items-center gap-3"><div className="grid h-10 w-10 place-items-center rounded-xl bg-lime text-ink"><LandPlot size={22} /></div><div><h1 className="font-display text-lg font-extrabold tracking-tight">LANDSTACK</h1><p className="max-w-[150px] text-[8px] font-bold uppercase leading-relaxed tracking-[.13em] text-white/45">Integrated GIS digital public infrastructure</p></div></div><button onClick={close} className="p-2 lg:hidden" aria-label="Close navigation"><X size={20} /></button></div>
    <button onClick={() => { onStartDemo(); close() }} className="mt-7 flex w-full items-center justify-center gap-2 rounded-xl bg-lime px-4 py-3 text-xs font-extrabold text-ink"><Play size={15} /> Start Demo</button>
    <nav className="mt-5 space-y-2" aria-label="Primary navigation"><p className="mb-3 px-3 text-[10px] font-bold uppercase tracking-[.2em] text-white/35">Workspace</p>{nav.map(({ id, label, icon: Icon }) => <button key={id} aria-current={view === id ? 'page' : undefined} onClick={() => { onNavigate(id); close() }} className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm font-semibold ${view === id ? 'bg-white/10 text-lime' : 'text-white/70 hover:bg-white/5 hover:text-white'}`}><Icon size={18} />{label}</button>)}</nav>
    <div className="mt-auto rounded-2xl border border-white/10 bg-white/5 p-4"><div className="flex items-center gap-2 text-xs font-bold text-lime"><ShieldCheck size={16} /> SIH 2026 Prototype</div><p className="mt-2 text-[9px] font-bold uppercase tracking-widest text-amber-200">Demo / Synthetic Data</p><p className="mt-2 text-[10px] leading-relaxed text-white/45">React + FastAPI · PostgreSQL/PostGIS-ready · free/open-source.</p></div>
  </aside>
}

const queryString = (filters) => {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => { if (value.trim()) params.set(key, value.trim()) })
  return params.toString()
}

export default function App() {
  const fallbackData = useRef(buildFallbackParcels())
  const [parcels, setParcels] = useState(null)
  const [apiState, setApiState] = useState('connecting')
  const [filters, setFilters] = useState(emptyFilters)
  const [loading, setLoading] = useState(true)
  const [selectedParcel, setSelectedParcel] = useState(null)
  const [navOpen, setNavOpen] = useState(false)
  const [currentView, setCurrentView] = useState('map')
  const [inspectionContext, setInspectionContext] = useState(null)
  const [parcelInitialTab, setParcelInitialTab] = useState('Overview')
  const [caseDetailId, setCaseDetailId] = useState(null)
  const [caseRevision, setCaseRevision] = useState(0)
  const [demoGuideOpen, setDemoGuideOpen] = useState(false)
  const initialLoad = useRef(true)

  useEffect(() => {
    const controller = new AbortController()
    Promise.all([
      fetch('/api/health', { signal: controller.signal }).then((response) => response.json()),
      fetch('/api/parcels', { signal: controller.signal }).then((response) => { if (!response.ok) throw new Error('Parcel API unavailable'); return response.json() }),
    ]).then(([health, data]) => {
      if (health.database !== 'connected') throw new Error('Database unavailable')
      setParcels(data); setApiState('connected'); setLoading(false); initialLoad.current = false
    }).catch((error) => {
      if (error.name !== 'AbortError') { setParcels(fallbackData.current); setApiState('fallback'); setLoading(false); initialLoad.current = false }
    })
    return () => controller.abort()
  }, [])

  useEffect(() => {
    if (initialLoad.current) return undefined
    const timer = window.setTimeout(() => {
      setLoading(true)
      if (apiState === 'fallback') {
        setParcels(filterFallbackParcels(fallbackData.current, filters)); setLoading(false); return
      }
      fetch(`/api/parcels?${queryString(filters)}`)
        .then((response) => { if (!response.ok) throw new Error('API unavailable'); return response.json() })
        .then((data) => { setParcels(data); setLoading(false) })
        .catch(() => { setApiState('fallback'); setParcels(filterFallbackParcels(fallbackData.current, filters)); setLoading(false) })
    }, 250)
    return () => window.clearTimeout(timer)
  }, [filters, apiState])

  const selectParcel = (feature, initialTab = 'Overview') => {
    const base = feature.properties
    setParcelInitialTab(initialTab)
    setSelectedParcel(base)
    if (apiState === 'connected') {
      fetch(`/api/parcels/${encodeURIComponent(base.parcel_id)}`).then((response) => response.ok ? response.json() : Promise.reject()).then(setSelectedParcel).catch(() => setSelectedParcel(base))
    }
  }
  const updateFilter = (key, value) => { setFilters((current) => ({ ...current, [key]: value })); setSelectedParcel(null) }
  const viewPriorityParcel = (item) => {
    const feature = fallbackData.current.features.find((candidate) => candidate.properties.parcel_id === item.parcel_id)
    setFilters(emptyFilters)
    setParcels(fallbackData.current)
    setCurrentView('map')
    if (feature) selectParcel(feature)
  }
  const startPriorityInspection = (priority) => {
    const feature = fallbackData.current.features.find((candidate) => candidate.properties.parcel_id === priority.parcel_id)
    if (feature) setInspectionContext({ parcel: feature.properties, priority })
  }
  const viewGrievance = (item) => {
    const feature = fallbackData.current.features.find((candidate) => candidate.properties.parcel_id === item.parcel_id)
    setFilters(emptyFilters); setParcels(fallbackData.current); setCurrentView('map')
    if (feature) selectParcel(feature, 'Grievances')
  }
  const openParcelById = (parcelId) => {
    const feature = fallbackData.current.features.find((candidate) => candidate.properties.parcel_id === parcelId)
    setCaseDetailId(null); setFilters(emptyFilters); setParcels(fallbackData.current); setCurrentView('map')
    if (feature) selectParcel(feature)
  }
  const startCaseInspection = (caseDetail) => {
    const feature = fallbackData.current.features.find((candidate) => candidate.properties.parcel_id === caseDetail.parcel_id)
    if (feature) { setCaseDetailId(null); setInspectionContext({ parcel: feature.properties, priority: caseDetail.priority }) }
  }
  const openDemoParcel = (initialTab = 'Overview') => {
    const feature = fallbackData.current.features.find((candidate) => candidate.properties.parcel_id === 'RTN-CHI-0013')
    setFilters(emptyFilters); setParcels(fallbackData.current); setCurrentView('map')
    if (feature) selectParcel(feature, initialTab)
  }
  const navigateDemo = (target) => {
    setDemoGuideOpen(false)
    if (target === 'gis') openDemoParcel('Overview')
    else if (target === 'satellite') openDemoParcel('Satellite History')
    else if (target === 'priority') openDemoParcel('Priority')
    else if (target === 'grievance') openDemoParcel('Grievances')
    else if (target === 'cases') setCurrentView('cases')
    else setCurrentView('analytics')
  }
  const count = parcels?.features.length || 0
  const banner = useMemo(() => apiState === 'fallback' ? 'Local Demo Mode — PostgreSQL/PostGIS is unavailable. Workflow records are stored for the current backend session only.' : null, [apiState])

  return <div className="flex min-h-screen bg-sand">
    {navOpen && <button className="fixed inset-0 z-30 bg-black/40 lg:hidden" onClick={() => setNavOpen(false)} aria-label="Close navigation overlay" />}
    <Sidebar open={navOpen} close={() => setNavOpen(false)} view={currentView} onNavigate={setCurrentView} onStartDemo={() => setDemoGuideOpen(true)} />
    <main className="flex min-w-0 flex-1 flex-col p-3 md:p-5 lg:p-7">
      <header className="mb-4 flex items-center justify-between gap-4"><div className="flex items-center gap-3"><button onClick={() => setNavOpen(true)} className="grid h-10 w-10 place-items-center rounded-xl border border-ink/10 bg-white lg:hidden" aria-label="Open navigation"><Menu size={20} /></button><div><p className="text-[10px] font-extrabold uppercase tracking-[.18em] text-moss">Ratnagiri demonstration area</p><h2 className="font-display text-xl font-extrabold tracking-tight md:text-2xl">{currentView === 'priority' ? 'Inspection priority' : currentView === 'grievances' ? 'Citizen grievances' : currentView === 'cases' ? 'Administrative review' : currentView === 'analytics' ? 'Governance analytics' : 'Parcel intelligence'}</h2></div></div><div className="flex items-center gap-2 rounded-full border border-ink/10 bg-white px-3 py-2 text-[10px] font-bold text-ink/65 shadow-sm"><span className={`status-dot h-2 w-2 rounded-full ${apiState === 'fallback' ? 'bg-amber-500' : 'bg-lime'}`} /><Wifi size={13} className="hidden sm:block" /><span>{apiState === 'connected' ? 'PostGIS connected' : apiState === 'fallback' ? 'Fallback active' : 'Connecting…'}</span></div></header>
      {banner && <div role="status" className="mb-3 flex items-center gap-2 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-[11px] font-semibold text-amber-900"><AlertTriangle size={15} />{banner}</div>}
      <Suspense fallback={<AsyncView />}>{currentView === 'priority' ? <PriorityDashboard onView={viewPriorityParcel} onStartInspection={startPriorityInspection} /> : currentView === 'grievances' ? <GrievanceDashboard key={caseRevision} onViewParcel={viewGrievance} onViewCase={setCaseDetailId} /> : currentView === 'cases' ? <CaseDashboard key={caseRevision} onViewCase={setCaseDetailId} /> : currentView === 'analytics' ? <GovernanceAnalytics onViewCase={setCaseDetailId} onViewGrievance={viewGrievance} onViewPriority={viewPriorityParcel} /> : <>
        <SearchFilters filters={filters} onChange={updateFilter} onClear={() => { setFilters(emptyFilters); setSelectedParcel(null) }} parcels={parcels} loading={loading} onResult={selectParcel} />
        <div className="mb-4 grid grid-cols-3 gap-2 md:gap-4">{[[loading ? '…' : count, 'Visible parcels'], ['3', 'Talukas'], ['PostGIS', apiState === 'connected' ? 'Data source' : 'Fallback ready']].map(([value, label]) => <div key={label} className="rounded-2xl border border-ink/10 bg-white px-3 py-3 md:px-5 md:py-4"><p className="font-display text-lg font-extrabold md:text-xl">{value}</p><p className="text-[9px] font-bold uppercase tracking-wider text-ink/45">{label}</p></div>)}</div>
        <div className="min-h-0 flex-1">{parcels ? <MapView parcels={parcels} selectedParcel={selectedParcel} onSelect={selectParcel} onClose={() => setSelectedParcel(null)} initialTab={parcelInitialTab} onViewCase={setCaseDetailId} /> : <div className="grid h-full min-h-[520px] place-items-center rounded-3xl bg-white text-sm text-ink/50">Loading parcels…</div>}</div>
      </>}</Suspense>
      <footer className="mt-3 flex flex-col justify-between gap-1 px-1 text-[9px] text-ink/45 xl:flex-row"><span>LANDSTACK uses synthetic demonstration data—not official cadastral, ownership, or legal records.</span><span>Automated analysis supports prioritization; official verification and human decision-making remain mandatory.</span><span>Basemap © OpenStreetMap contributors</span></footer>
    </main>
    <Suspense fallback={inspectionContext ? <AsyncModal /> : null}>{inspectionContext && <InspectionForm parcel={inspectionContext.parcel} initialPriority={inspectionContext.priority} onClose={() => setInspectionContext(null)} />}</Suspense>
    <Suspense fallback={caseDetailId ? <AsyncModal /> : null}>{caseDetailId && <CaseDetail caseId={caseDetailId} onClose={() => setCaseDetailId(null)} onChanged={() => setCaseRevision((value) => value + 1)} onOpenParcel={openParcelById} onStartInspection={startCaseInspection} />}</Suspense>
    {demoGuideOpen && <DemoGuide onClose={() => setDemoGuideOpen(false)} onNavigate={navigateDemo} />}
  </div>
}
