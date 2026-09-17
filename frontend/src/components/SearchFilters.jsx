import { Search, SlidersHorizontal, X } from 'lucide-react'

const filterOptions = [
  { key: 'taluka', label: 'Taluka', values: ['Ratnagiri', 'Chiplun', 'Sangameshwar'] },
  { key: 'land_use', label: 'Land use', values: ['Agricultural', 'Orchard', 'Residential', 'Mixed'] },
  { key: 'verification_status', label: 'Verification', values: ['Verified', 'Pending Verification', 'Requires Verification'] },
  { key: 'risk_status', label: 'Review status', values: ['Normal', 'Requires Verification', 'Flagged for Review'] },
]

export default function SearchFilters({ filters, onChange, onClear, parcels, loading, onResult }) {
  const count = parcels?.features?.length || 0
  const activeFilters = Object.values(filters).filter(Boolean).length
  return (
    <section className="mb-4 rounded-2xl border border-ink/10 bg-white p-3 shadow-sm md:p-4">
      <div className="flex flex-col gap-3 xl:flex-row">
        <div className="relative min-w-0 flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-moss" size={18} />
          <input
            aria-label="Search parcels"
            value={filters.search}
            onChange={(event) => onChange('search', event.target.value)}
            placeholder="Search parcel ID, survey number, or village..."
            className="h-11 w-full rounded-xl border border-ink/15 bg-sand/45 pl-11 pr-10 text-sm outline-none transition focus:border-moss focus:ring-2 focus:ring-moss/10"
          />
          {filters.search && <button onClick={() => onChange('search', '')} className="absolute right-3 top-1/2 -translate-y-1/2 text-ink/45" aria-label="Clear search"><X size={17} /></button>}
          {filters.search && !loading && count > 0 && (
            <div className="absolute left-0 right-0 top-12 z-30 max-h-60 overflow-auto rounded-xl border border-ink/10 bg-white p-1.5 shadow-panel">
              {parcels.features.slice(0, 8).map((feature) => <button key={feature.properties.parcel_id} onClick={() => onResult(feature)} className="block w-full rounded-lg px-3 py-2 text-left hover:bg-sand"><span className="block text-xs font-extrabold text-ink">{feature.properties.parcel_id} · {feature.properties.survey_number}</span><span className="text-[10px] text-ink/50">{feature.properties.village} · {feature.properties.taluka}</span></button>)}
            </div>
          )}
          {filters.search && !loading && count === 0 && <div className="absolute left-0 right-0 top-12 z-30 rounded-xl border border-ink/10 bg-white p-4 text-center text-xs text-ink/55 shadow-panel">No search results</div>}
        </div>
        <div className="grid grid-cols-2 gap-2 md:grid-cols-4 xl:flex xl:flex-1">
          {filterOptions.map(({ key, label, values }) => (
            <select key={key} value={filters[key]} onChange={(event) => onChange(key, event.target.value)} className="h-11 min-w-0 flex-1 rounded-xl border border-ink/15 bg-white px-3 text-xs font-semibold outline-none focus:border-moss" aria-label={label}>
              <option value="">All {label}</option>
              {values.map((value) => <option key={value}>{value}</option>)}
            </select>
          ))}
        </div>
      </div>
      <div className="mt-3 flex items-center justify-between text-[10px] font-bold uppercase tracking-wider text-ink/50">
        <span className="flex items-center gap-2"><SlidersHorizontal size={13} /> {loading ? 'Loading parcels…' : `${count} parcel${count === 1 ? '' : 's'} visible`}</span>
        <button disabled={!activeFilters} onClick={onClear} className="rounded-lg px-2 py-1 text-moss enabled:hover:bg-sand disabled:opacity-30">Clear filters</button>
      </div>
    </section>
  )
}
