import { useCallback, useEffect, useState } from 'react'
import { AlertCircle, BarChart3, Download, LoaderCircle, RefreshCw, TriangleAlert } from 'lucide-react'

const endpoints = ['/api/analytics/summary', '/api/analytics/distributions', '/api/analytics/geography', '/api/analytics/attention']
const reports = [
  ['parcels', 'Parcel Summary', 'Parcel identifiers, location, land attributes, and record status.'],
  ['priorities', 'Inspection Priority', 'Explainable inspection scores and current workflow levels.'],
  ['grievances', 'Grievance Summary', 'Aggregate-safe grievance references, categories, and statuses.'],
  ['inspections', 'Inspection Summary', 'Inspection outcomes, follow-up state, and evidence counts.'],
  ['cases', 'Administrative Cases', 'Case status, review stage, resolution type, and priority context.'],
]

const Metric = ({ label, value, detail }) => <article className="rounded-2xl border border-ink/10 bg-white p-4"><p className="font-display text-2xl font-extrabold">{value}</p><p className="mt-1 text-[8px] font-extrabold uppercase tracking-wider text-ink/50">{label}</p>{detail && <p className="mt-2 text-[9px] text-ink/45">{detail}</p>}</article>

function Bars({ title, items, emptyText }) {
  const total = items?.reduce((sum, item) => sum + item.count, 0) || 0
  return <section className="rounded-2xl border border-ink/10 bg-white p-4"><h3 className="font-display text-base font-extrabold">{title}</h3>{total === 0 ? <p className="mt-4 rounded-xl bg-sand/60 p-4 text-xs text-ink/50">{emptyText}</p> : <div className="mt-4 space-y-3">{items.map((item) => <div key={item.label}><div className="mb-1 flex justify-between gap-3 text-[10px]"><strong>{item.label}</strong><span>{item.count} · {item.percentage}%</span></div><div className="h-2 overflow-hidden rounded-full bg-sand" role="img" aria-label={`${item.label}: ${item.count}, ${item.percentage} percent`}><span className="block h-full rounded-full bg-moss" style={{ width: `${Math.max(item.percentage, item.count ? 2 : 0)}%` }} /></div></div>)}</div>}</section>
}

export default function GovernanceAnalytics({ onViewCase, onViewGrievance, onViewPriority }) {
  const [state, setState] = useState({ loading: true, error: '', data: null })
  const [reportState, setReportState] = useState({ name: '', error: '' })
  const load = useCallback(() => {
    setState({ loading: true, error: '', data: null })
    Promise.all(endpoints.map((url) => fetch(url).then((response) => response.ok ? response.json() : Promise.reject())))
      .then(([summary, distributions, geography, attention]) => setState({ loading: false, error: '', data: { summary, distributions, geography, attention } }))
      .catch(() => setState({ loading: false, error: 'Governance analytics could not be loaded. Ensure the local backend is running.', data: null }))
  }, [])
  useEffect(() => { load() }, [load])

  const download = async (name) => {
    if (reportState.name) return
    setReportState({ name, error: '' })
    try {
      const response = await fetch(`/api/reports/${name}.csv`)
      if (!response.ok) throw new Error()
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      const disposition = response.headers.get('content-disposition') || ''
      const serverFilename = disposition.match(/filename="?([^";]+)"?/i)?.[1]
      link.href = url; link.download = serverFilename || `landstack_${name}_report.csv`; document.body.appendChild(link); link.click(); link.remove()
      URL.revokeObjectURL(url)
      setReportState({ name: '', error: '' })
    } catch {
      setReportState({ name: '', error: 'Report download failed. Ensure the local backend is available and try again.' })
    }
  }

  if (state.loading) return <div className="grid min-h-[420px] place-items-center rounded-2xl bg-white text-xs text-ink/50"><span className="flex items-center gap-2"><LoaderCircle size={16} className="animate-spin" /> Loading governance analytics…</span></div>
  if (state.error) return <div className="flex items-center justify-between gap-3 rounded-xl bg-rose-50 p-4 text-xs text-rose-800"><span className="flex items-center gap-2"><AlertCircle size={16} />{state.error}</span><button onClick={load} className="rounded-lg border border-rose-300 px-3 py-2 font-bold">Retry</button></div>
  const { summary, distributions, geography, attention } = state.data
  const refreshed = new Date(summary.refreshed_at).toLocaleString()
  const metrics = [
    ['Total Parcels', summary.total_parcels, 'Parcels currently represented'],
    ['Review-Recommended', summary.review_recommended_parcels, 'Priority level is not Routine'],
    ['Satellite Analyses', summary.satellite_analyses, 'Parcels with actual demo analyses'],
    ['Completed Inspections', summary.completed_inspections, 'Inspection Completed status'],
    ['Open Grievances', summary.open_grievances, 'Not Resolved or Closed'],
    ['Active Cases', summary.active_cases, 'Not Resolved or Closed'],
    ['Resolved / Closed Cases', summary.resolved_or_closed_cases, summary.total_cases ? `${summary.resolution_rate}% of ${summary.total_cases} cases` : 'Resolution rate: N/A'],
  ]
  const attentionAction = (item) => item.action === 'case' ? onViewCase(item.reference) : item.action === 'grievance' ? onViewGrievance(item) : onViewPriority(item)
  return <div className="space-y-4">
    <section className="flex flex-col justify-between gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 sm:flex-row sm:items-center"><div><p className="text-[9px] font-extrabold uppercase tracking-widest text-moss">Current descriptive overview</p><p className="mt-1 text-xs font-bold">{summary.storage_mode === 'fallback' ? 'Fallback mode · analytics reflect current local demo-session data.' : 'Database mode'}</p><p className="mt-1 text-[9px] text-ink/50">Last refreshed: {refreshed}</p></div><button onClick={load} className="flex items-center justify-center gap-2 rounded-xl bg-ink px-4 py-3 text-[10px] font-bold text-white"><RefreshCw size={13} /> Refresh Analytics</button></section>
    <p className="flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 p-3 text-[10px] text-amber-950"><TriangleAlert size={15} className="shrink-0" />LANDSTACK analytics currently use synthetic demonstration parcel data and local prototype workflow records. They do not represent official government statistics.</p>
    <div className="grid grid-cols-2 gap-2 md:grid-cols-4 xl:grid-cols-7">{metrics.map(([label, value, detail]) => <Metric key={label} label={label} value={value} detail={detail} />)}</div>
    <div className="grid gap-4 xl:grid-cols-2"><Bars title="Inspection Priority Distribution" items={distributions.priority_levels} emptyText="No priority data available." /><Bars title="Grievance Categories" items={distributions.grievance_categories} emptyText="No grievance data available in the current session." /><Bars title="Administrative Case Status" items={distributions.case_statuses} emptyText="No administrative cases available." /><Bars title="Inspection Outcomes" items={distributions.inspection_outcomes} emptyText="No inspections recorded in the current session." /></div>
    <section className="rounded-2xl border border-ink/10 bg-white p-4"><div className="flex items-center gap-2"><BarChart3 size={18} className="text-moss" /><h3 className="font-display text-base font-extrabold">Satellite Change Overview</h3></div><div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4">{distributions.satellite_statuses.map((item) => <Metric key={item.label} label={item.label} value={item.count} />)}<Metric label="Average Actual Change" value={distributions.average_satellite_change_percentage == null ? 'N/A' : `${distributions.average_satellite_change_percentage}%`} detail="Analyzed parcels only" /></div></section>
    <section className="overflow-hidden rounded-2xl border border-ink/10 bg-white"><div className="border-b p-4"><h3 className="font-display text-base font-extrabold">Activity by Taluka</h3><p className="text-[9px] text-ink/45">Sorted by recorded workflow activity, then parcel count.</p></div><div className="overflow-x-auto"><table className="w-full min-w-[680px] text-left text-xs"><thead className="bg-sand/70 text-[9px] uppercase tracking-wider text-ink/45"><tr>{['Taluka', 'Parcels', 'Review Recommended', 'Grievances', 'Inspections', 'Active Cases'].map((label) => <th key={label} className="px-4 py-3">{label}</th>)}</tr></thead><tbody className="divide-y divide-ink/10">{geography.talukas.map((item) => <tr key={item.taluka}><td className="px-4 py-3 font-bold">{item.taluka}</td><td className="px-4 py-3">{item.parcel_count}</td><td className="px-4 py-3">{item.review_count}</td><td className="px-4 py-3">{item.grievance_count}</td><td className="px-4 py-3">{item.inspection_count}</td><td className="px-4 py-3">{item.active_case_count}</td></tr>)}</tbody></table></div></section>
    <section className="rounded-2xl border border-ink/10 bg-white p-4"><h3 className="font-display text-base font-extrabold">Requires Attention</h3><p className="text-[9px] text-ink/45">Existing inspection priorities and unresolved workflow statuses only—no new score or prediction.</p>{attention.items.length ? <div className="mt-3 grid gap-2 md:grid-cols-2">{attention.items.map((item) => <article key={`${item.type}-${item.reference}`} className="rounded-xl border p-3 text-[10px]"><div className="flex items-start justify-between gap-3"><div><p className="text-[8px] font-extrabold uppercase tracking-wider text-moss">{item.type}</p><strong className="mt-1 block text-xs">{item.reference}</strong><p>{item.status} · {item.taluka}</p><p className="mt-1 text-ink/50">{item.reason}</p></div><button onClick={() => attentionAction(item)} className="shrink-0 rounded-lg bg-ink px-3 py-2 font-bold text-white">View</button></div></article>)}</div> : <p className="mt-3 rounded-xl bg-sand/60 p-4 text-xs text-ink/50">No current items match the attention rules.</p>}</section>
    <section className="rounded-2xl border border-ink/10 bg-white p-4"><h3 className="font-display text-base font-extrabold">Reports</h3><p className="text-[9px] text-ink/45">Governance-safe UTF-8 CSV exports. Private identities, GPS coordinates, evidence paths, and internal administrative notes are excluded.</p>{reportState.error && <p role="alert" className="mt-3 rounded-xl bg-rose-50 p-3 text-[10px] text-rose-800">{reportState.error}</p>}<div className="mt-3 grid gap-2 md:grid-cols-2 xl:grid-cols-5">{reports.map(([name, label, description]) => <article key={name} className="rounded-xl border p-3"><strong className="text-xs">{label}</strong><p className="mt-1 min-h-10 text-[9px] text-ink/50">{description}</p><button onClick={() => download(name)} disabled={Boolean(reportState.name)} className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg border border-ink/15 px-3 py-2 text-[10px] font-bold disabled:opacity-50">{reportState.name === name ? <LoaderCircle size={12} className="animate-spin" /> : <Download size={12} />} {reportState.name === name ? 'Preparing…' : 'Download CSV'}</button></article>)}</div></section>
  </div>
}
