import { useEffect, useRef, useState } from 'react'
import { AlertCircle, Camera, CheckCircle2, Crosshair, LoaderCircle, MapPin, Trash2, X } from 'lucide-react'

const outcomes = ['No Significant Issue Observed', 'Requires Further Review', 'Change Confirmed On Site', 'Unable To Verify']
const allowedTypes = new Set(['image/jpeg', 'image/png', 'image/webp'])
const allowedExtensions = new Set(['jpg', 'jpeg', 'png', 'webp'])
const MAX_BYTES = 5 * 1024 * 1024

const readError = async (response) => {
  try {
    const body = await response.json()
    return body.detail?.message || 'Inspection could not be submitted.'
  } catch { return 'Inspection could not be submitted.' }
}

export default function InspectionForm({ parcel, initialPriority = null, onClose, onCompleted, completionLabel = 'Close inspection' }) {
  const [priority, setPriority] = useState(initialPriority)
  const [contextError, setContextError] = useState('')
  const [location, setLocation] = useState({ latitude: '', longitude: '', accuracy: '', source: 'Unavailable' })
  const [gpsState, setGpsState] = useState('idle')
  const [gpsMessage, setGpsMessage] = useState('')
  const [observations, setObservations] = useState('')
  const [outcome, setOutcome] = useState('')
  const [followUp, setFollowUp] = useState(false)
  const [recommendation, setRecommendation] = useState('')
  const [photos, setPhotos] = useState([])
  const [photoError, setPhotoError] = useState('')
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [success, setSuccess] = useState(null)
  const [lightbox, setLightbox] = useState(null)
  const submissionKey = useRef(globalThis.crypto?.randomUUID?.().replaceAll('-', '') || `inspection${Date.now()}`)
  const photosRef = useRef([])
  photosRef.current = photos

  useEffect(() => {
    if (initialPriority) return undefined
    const controller = new AbortController()
    fetch(`/api/parcels/${encodeURIComponent(parcel.parcel_id)}/priority`, { signal: controller.signal })
      .then((response) => { if (!response.ok) throw new Error(); return response.json() })
      .then(setPriority)
      .catch((error) => { if (error.name !== 'AbortError') setContextError('Priority context is unavailable. Close this form and ensure the backend is running.') })
    return () => controller.abort()
  }, [initialPriority, parcel.parcel_id])

  useEffect(() => () => photosRef.current.forEach((photo) => URL.revokeObjectURL(photo.preview)), [])

  const useLocation = () => {
    setGpsMessage(''); setGpsState('loading')
    if (!navigator.geolocation) {
      setGpsState('error'); setGpsMessage('GPS is not supported by this browser. Enter coordinates manually or use Unable To Verify.')
      return
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({ latitude: position.coords.latitude.toFixed(6), longitude: position.coords.longitude.toFixed(6), accuracy: Math.round(position.coords.accuracy).toString(), source: 'Browser GPS' })
        setGpsState('success'); setGpsMessage('Current location captured for this inspection only.')
      },
      (error) => {
        const messages = { 1: 'Location permission was denied.', 2: 'Current position is unavailable.', 3: 'Location request timed out.' }
        setGpsState('error'); setGpsMessage(`${messages[error.code] || 'Location could not be captured automatically.'} Enter coordinates manually or continue as Unable To Verify if appropriate.`)
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 },
    )
  }

  const updateCoordinate = (key, value) => {
    setLocation((current) => ({ ...current, [key]: value, accuracy: current.source === 'Browser GPS' ? '' : current.accuracy, source: value || current[key === 'latitude' ? 'longitude' : 'latitude'] ? 'Manual' : 'Unavailable' }))
    setGpsState('idle'); setGpsMessage('Manual coordinates will be used for this inspection.')
  }

  const addPhotos = (event) => {
    const incoming = [...event.target.files]
    event.target.value = ''
    setPhotoError('')
    if (photos.length + incoming.length > 3) { setPhotoError('A maximum of 3 photos is allowed.'); return }
    for (const file of incoming) {
      const extension = file.name.split('.').pop()?.toLowerCase()
      if (!allowedTypes.has(file.type) || !allowedExtensions.has(extension)) { setPhotoError('Only JPEG, PNG, and WEBP photos are allowed.'); return }
      if (file.size > MAX_BYTES) { setPhotoError('Each photo must be 5 MB or smaller.'); return }
    }
    setPhotos((current) => [...current, ...incoming.map((file) => ({ file, preview: URL.createObjectURL(file) }))])
  }

  const removePhoto = (index) => setPhotos((current) => current.filter((photo, itemIndex) => {
    if (itemIndex === index) URL.revokeObjectURL(photo.preview)
    return itemIndex !== index
  }))

  const validate = () => {
    const latitude = location.latitude === '' ? null : Number(location.latitude)
    const longitude = location.longitude === '' ? null : Number(location.longitude)
    if (observations.trim().length < 10 || observations.trim().length > 2000) return 'Observations must contain 10–2000 characters.'
    if (!outcome) return 'Choose an inspection outcome.'
    if ((latitude === null) !== (longitude === null)) return 'Enter both latitude and longitude.'
    if (latitude !== null && (!Number.isFinite(latitude) || latitude < -90 || latitude > 90)) return 'Latitude must be between -90 and 90.'
    if (longitude !== null && (!Number.isFinite(longitude) || longitude < -180 || longitude > 180)) return 'Longitude must be between -180 and 180.'
    if (outcome !== 'Unable To Verify' && (latitude === null || longitude === null)) return 'A valid location is required unless the outcome is Unable To Verify.'
    return ''
  }

  const submit = async (event) => {
    event.preventDefault()
    if (submitting || success) return
    const error = validate()
    if (error) { setFormError(error); return }
    setFormError(''); setSubmitting(true)
    const form = new FormData()
    form.append('payload', JSON.stringify({
      inspection_outcome: outcome,
      latitude: location.latitude === '' ? null : Number(location.latitude),
      longitude: location.longitude === '' ? null : Number(location.longitude),
      gps_accuracy_m: location.accuracy === '' ? null : Number(location.accuracy),
      location_source: location.latitude === '' ? 'Unavailable' : location.source,
      officer_display_name: 'Demo Field Officer', officer_reference: 'DEMO-OFFICER-01',
      observations: observations.trim(), requires_follow_up: followUp,
      recommendation: followUp ? recommendation.trim() || null : null,
    }))
    photos.forEach(({ file }) => form.append('photos', file))
    try {
      const response = await fetch(`/api/parcels/${encodeURIComponent(parcel.parcel_id)}/inspections`, { method: 'POST', headers: { 'X-Idempotency-Key': submissionKey.current }, body: form })
      if (!response.ok) throw new Error(await readError(response))
      const record = await response.json()
      setSuccess(record); onCompleted?.(record)
    } catch (error) {
      setFormError(error.message || 'Inspection submission failed. Check the backend and try again.'); setSubmitting(false)
    }
  }

  return <div className="fixed inset-0 z-[70] overflow-y-auto bg-ink/70 p-2 backdrop-blur-sm sm:p-5" role="dialog" aria-modal="true" aria-label="Field inspection form">
    <div className="mx-auto min-h-full max-w-3xl rounded-2xl bg-white shadow-2xl sm:min-h-0">
      <header className="sticky top-0 z-10 flex items-start justify-between rounded-t-2xl bg-ink px-4 py-4 text-white sm:px-6"><div><p className="text-[9px] font-extrabold uppercase tracking-[.18em] text-lime">Demo Field Inspection</p><h2 className="mt-1 font-display text-xl font-extrabold">{parcel.parcel_id}</h2><p className="text-[10px] text-white/55">Survey {parcel.survey_number} · {parcel.village}</p></div><button type="button" onClick={onClose} className="rounded-xl bg-white/10 p-2" aria-label="Close inspection"><X size={19} /></button></header>
      {success ? <div className="grid min-h-[520px] place-items-center p-6 text-center"><div><CheckCircle2 className="mx-auto text-emerald-600" size={50} /><h3 className="mt-4 font-display text-xl font-extrabold">Inspection completed</h3><p className="mt-2 text-sm font-bold">{success.inspection_id}</p><p className="mt-3 rounded-xl bg-amber-50 p-3 text-xs text-amber-900">{success.storage_notice}</p><button onClick={onClose} className="mt-5 rounded-xl bg-ink px-5 py-3 text-xs font-bold text-white">{completionLabel}</button></div></div> : !priority ? <div className="grid min-h-[520px] place-items-center p-6 text-center text-sm text-ink/55">{contextError || <span className="flex items-center gap-2"><LoaderCircle className="animate-spin" /> Loading parcel context…</span>}</div> : <form onSubmit={submit} className="space-y-5 p-4 sm:p-6">
        <section className="rounded-2xl bg-sand/65 p-4"><h3 className="text-[10px] font-extrabold uppercase tracking-widest text-moss">Parcel context</h3><div className="mt-3 grid grid-cols-2 gap-3 text-xs sm:grid-cols-4"><div><span className="text-ink/45">Taluka</span><p className="font-bold">{parcel.taluka}</p></div><div><span className="text-ink/45">Area</span><p className="font-bold">{parcel.area_hectares} ha</p></div><div><span className="text-ink/45">Priority</span><p className="font-bold">{priority.priority_score} · {priority.priority_level}</p></div><div><span className="text-ink/45">Satellite change</span><p className="font-bold">{priority.change_percentage == null ? 'No analysis' : `${priority.change_percentage}%`}</p></div></div><p className="mt-3 text-[10px] text-ink/50">Verification: {parcel.verification_status}</p></section>
        <section><div className="flex flex-wrap items-center justify-between gap-2"><div><h3 className="text-xs font-extrabold">Location</h3><p className="text-[10px] text-ink/50">Location is captured only for this inspection record.</p></div><button type="button" onClick={useLocation} disabled={gpsState === 'loading'} className="flex items-center gap-2 rounded-xl border border-moss px-3 py-2 text-xs font-bold text-moss disabled:opacity-50">{gpsState === 'loading' ? <LoaderCircle size={15} className="animate-spin" /> : <Crosshair size={15} />} Use My Location</button></div>
          {gpsMessage && <p role="status" className={`mt-2 rounded-xl p-3 text-[10px] ${gpsState === 'error' ? 'bg-amber-50 text-amber-900' : 'bg-emerald-50 text-emerald-800'}`}>{gpsMessage}</p>}
          <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-3"><label className="text-[10px] font-bold">Latitude<input aria-label="Manual latitude" inputMode="decimal" value={location.latitude} onChange={(event) => updateCoordinate('latitude', event.target.value)} placeholder="-90 to 90" className="mt-1 h-11 w-full rounded-xl border border-ink/15 px-3 text-sm font-normal" /></label><label className="text-[10px] font-bold">Longitude<input aria-label="Manual longitude" inputMode="decimal" value={location.longitude} onChange={(event) => updateCoordinate('longitude', event.target.value)} placeholder="-180 to 180" className="mt-1 h-11 w-full rounded-xl border border-ink/15 px-3 text-sm font-normal" /></label><label className="text-[10px] font-bold">Accuracy (metres)<input value={location.accuracy} readOnly placeholder="GPS only" className="mt-1 h-11 w-full rounded-xl border border-ink/10 bg-sand/50 px-3 text-sm font-normal" /></label></div>
        </section>
        <section><label className="text-xs font-extrabold">Field observations <span className="text-rose-600">*</span><textarea aria-label="Inspection observations" value={observations} onChange={(event) => setObservations(event.target.value)} maxLength={2000} rows={5} placeholder="Describe what was observed at the site…" className="mt-2 w-full resize-y rounded-xl border border-ink/15 p-3 text-sm font-normal" /></label><p className="text-right text-[9px] text-ink/40">{observations.length} / 2000</p></section>
        <section><div className="flex items-center justify-between"><div><h3 className="text-xs font-extrabold">Photo evidence</h3><p className="text-[10px] text-ink/50">JPEG, PNG, or WEBP · maximum 5 MB each · up to 3</p></div><label className="flex cursor-pointer items-center gap-2 rounded-xl bg-sand px-3 py-2 text-xs font-bold"><Camera size={15} /> Add Photo<input type="file" accept="image/jpeg,image/png,image/webp" multiple onChange={addPhotos} className="sr-only" /></label></div>{photoError && <p role="alert" className="mt-2 text-[10px] font-bold text-rose-700">{photoError}</p>}<div className="mt-3 grid grid-cols-3 gap-2">{photos.map((photo, index) => <div key={photo.preview} className="relative overflow-hidden rounded-xl border border-ink/10"><button type="button" onClick={() => setLightbox(photo)} className="block aspect-square w-full"><img src={photo.preview} alt={`Evidence preview ${index + 1}`} className="h-full w-full object-cover" /></button><button type="button" onClick={() => removePhoto(index)} className="absolute right-1 top-1 rounded-lg bg-ink/85 p-1.5 text-white" aria-label={`Remove photo ${index + 1}`}><Trash2 size={13} /></button></div>)}</div></section>
        <section><label className="text-xs font-extrabold">Inspection outcome <span className="text-rose-600">*</span><select aria-label="Inspection outcome" value={outcome} onChange={(event) => setOutcome(event.target.value)} className="mt-2 h-11 w-full rounded-xl border border-ink/15 px-3 text-sm font-normal"><option value="">Choose outcome…</option>{outcomes.map((value) => <option key={value}>{value}</option>)}</select></label><p className="mt-2 text-[10px] text-ink/50">The outcome reflects field observations only and is not a legal determination.</p></section>
        <section className="rounded-xl border border-ink/10 p-3"><label className="flex items-center gap-2 text-xs font-bold"><input type="checkbox" checked={followUp} onChange={(event) => setFollowUp(event.target.checked)} /> Requires follow-up</label>{followUp && <textarea aria-label="Follow-up recommendation" value={recommendation} onChange={(event) => setRecommendation(event.target.value)} maxLength={1000} rows={2} placeholder="Optional recommendation, such as request senior review…" className="mt-3 w-full rounded-xl border border-ink/15 p-3 text-sm" />}</section>
        {formError && <div role="alert" className="flex items-start gap-2 rounded-xl bg-rose-50 p-3 text-xs font-semibold text-rose-800"><AlertCircle size={16} className="shrink-0" />{formError}</div>}
        <div className="sticky bottom-0 -mx-4 flex gap-3 border-t border-ink/10 bg-white/95 p-4 backdrop-blur sm:-mx-6 sm:px-6"><button type="button" onClick={onClose} className="h-12 flex-1 rounded-xl border border-ink/15 text-xs font-bold">Cancel</button><button type="submit" disabled={submitting} className="flex h-12 flex-[2] items-center justify-center gap-2 rounded-xl bg-ink text-xs font-bold text-white disabled:cursor-not-allowed disabled:opacity-60">{submitting ? <><LoaderCircle size={16} className="animate-spin" /> Submitting…</> : <><MapPin size={16} /> Complete Inspection</>}</button></div>
      </form>}
    </div>
    {lightbox && <button type="button" onClick={() => setLightbox(null)} className="fixed inset-0 z-[80] grid place-items-center bg-black/85 p-4" aria-label="Close evidence preview"><img src={lightbox.preview} alt="Large evidence preview" className="max-h-[90vh] max-w-full rounded-xl object-contain" /></button>}
  </div>
}
