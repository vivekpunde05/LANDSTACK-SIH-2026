import { useEffect, useRef, useState } from 'react'
import Map from 'ol/Map.js'
import View from 'ol/View.js'
import GeoJSON from 'ol/format/GeoJSON.js'
import TileLayer from 'ol/layer/Tile.js'
import VectorLayer from 'ol/layer/Vector.js'
import OSM from 'ol/source/OSM.js'
import VectorSource from 'ol/source/Vector.js'
import { Fill, Stroke, Style } from 'ol/style.js'
import { fromLonLat } from 'ol/proj.js'
import { Layers3 } from 'lucide-react'
import { villageBoundary, talukaBoundary } from '../data/boundaries'
import LayerControl from './LayerControl'
import ParcelPanel from './ParcelPanel'

const format = new GeoJSON()
const readFeatures = (data) => format.readFeatures(data, { featureProjection: 'EPSG:3857' })
const boundaryStyle = (color, width) => new Style({ fill: new Fill({ color: `${color}0d` }), stroke: new Stroke({ color, width, lineDash: [8, 6] }) })
const parcelStyles = {
  default: new Style({ fill: new Fill({ color: 'rgba(168,217,111,.42)' }), stroke: new Stroke({ color: '#365e48', width: 1.5 }) }),
  hover: new Style({ fill: new Fill({ color: 'rgba(200,241,105,.72)' }), stroke: new Stroke({ color: '#18332d', width: 2.2 }) }),
  selected: new Style({ fill: new Fill({ color: 'rgba(24,51,45,.72)' }), stroke: new Stroke({ color: '#c8f169', width: 3 }) }),
}

export default function MapView({ parcels, selectedParcel, onSelect, onClose, initialTab = 'Overview', onViewCase }) {
  const containerRef = useRef(null)
  const mapRef = useRef(null)
  const layerRefs = useRef({})
  const hoveredRef = useRef(null)
  const selectedIdRef = useRef(null)
  const onSelectRef = useRef(onSelect)
  const [layerMenuOpen, setLayerMenuOpen] = useState(false)
  const [layers, setLayers] = useState({ parcels: true, village: true, taluka: true })
  onSelectRef.current = onSelect

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return undefined
    const talukaLayer = new VectorLayer({ source: new VectorSource({ features: readFeatures(talukaBoundary) }), style: boundaryStyle('#7c3aed', 3) })
    const villageLayer = new VectorLayer({ source: new VectorSource({ features: readFeatures(villageBoundary) }), style: boundaryStyle('#f59e0b', 2.5) })
    const parcelLayer = new VectorLayer({
      source: new VectorSource(),
      style: (feature) => feature.get('parcel_id') === selectedIdRef.current ? parcelStyles.selected : feature === hoveredRef.current ? parcelStyles.hover : parcelStyles.default,
    })
    layerRefs.current = { taluka: talukaLayer, village: villageLayer, parcels: parcelLayer }
    const map = new Map({
      target: containerRef.current,
      layers: [new TileLayer({ source: new OSM({ crossOrigin: 'anonymous' }), opacity: 0.82 }), talukaLayer, villageLayer, parcelLayer],
      view: new View({ center: fromLonLat([73.311, 16.996]), zoom: 14.2, minZoom: 11, maxZoom: 19 }),
    })
    mapRef.current = map
    map.on('pointermove', (event) => {
      if (event.dragging) return
      const feature = map.forEachFeatureAtPixel(event.pixel, (candidate, layer) => layer === parcelLayer ? candidate : null)
      if (hoveredRef.current !== feature) { hoveredRef.current = feature || null; parcelLayer.changed() }
      map.getTargetElement().style.cursor = feature ? 'pointer' : ''
    })
    map.on('singleclick', (event) => {
      const feature = map.forEachFeatureAtPixel(event.pixel, (candidate, layer) => layer === parcelLayer ? candidate : null)
      if (!feature) return
      const properties = { ...feature.getProperties() }
      delete properties.geometry
      onSelectRef.current({ type: 'Feature', id: properties.parcel_id, geometry: format.writeGeometryObject(feature.getGeometry(), { featureProjection: 'EPSG:3857' }), properties })
    })
    return () => { map.setTarget(undefined); mapRef.current = null; layerRefs.current = {} }
  }, [])

  useEffect(() => {
    const source = layerRefs.current.parcels?.getSource()
    if (!source) return
    source.clear()
    source.addFeatures(readFeatures(parcels))
  }, [parcels])

  useEffect(() => {
    selectedIdRef.current = selectedParcel?.parcel_id || null
    const parcelLayer = layerRefs.current.parcels
    parcelLayer?.changed()
    if (!selectedParcel || !parcelLayer || !mapRef.current) return
    const feature = parcelLayer.getSource().getFeatures().find((candidate) => candidate.get('parcel_id') === selectedParcel.parcel_id)
    if (feature) {
      const isMobile = (mapRef.current.getSize()?.[0] || 800) < 700
      mapRef.current.getView().fit(feature.getGeometry(), { padding: isMobile ? [60, 30, 330, 30] : [120, 430, 120, 120], maxZoom: 17, duration: 500 })
    }
  }, [selectedParcel])

  useEffect(() => { Object.entries(layers).forEach(([key, visible]) => layerRefs.current[key]?.setVisible(visible)) }, [layers])

  return <div className="relative h-full min-h-[520px] overflow-hidden rounded-[24px] border border-ink/10 bg-[#dfe4d8] shadow-panel md:rounded-[28px]">
    <div ref={containerRef} className="absolute inset-0" />
    <button onClick={() => setLayerMenuOpen(true)} className="absolute left-3 top-3 z-10 grid h-11 w-11 place-items-center rounded-xl bg-white shadow-panel md:hidden" aria-label="Open map layers"><Layers3 size={20} /></button>
    <LayerControl layers={layers} setLayers={setLayers} open={layerMenuOpen} onClose={() => setLayerMenuOpen(false)} />
    <ParcelPanel key={`${selectedParcel?.parcel_id || 'none'}-${initialTab}`} parcel={selectedParcel} onClose={onClose} initialTab={initialTab} onViewCase={onViewCase} />
    {!selectedParcel && parcels.features.length > 0 && <div className="pointer-events-none absolute bottom-4 left-1/2 z-10 -translate-x-1/2 rounded-full bg-ink/90 px-4 py-2 text-center text-[11px] font-semibold text-white shadow-lg">Hover to highlight · Click a parcel for intelligence</div>}
    {parcels.features.length === 0 && <div className="absolute left-1/2 top-1/2 z-10 -translate-x-1/2 -translate-y-1/2 rounded-2xl bg-white/95 px-6 py-5 text-center shadow-panel"><p className="text-sm font-bold">No parcels match filters</p><p className="mt-1 text-[10px] text-ink/50">Clear or adjust filters to restore parcels.</p></div>}
  </div>
}
