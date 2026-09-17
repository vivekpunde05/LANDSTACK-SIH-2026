const ring = (west, south, east, north) => [[
  [west, south], [east, south], [east, north], [west, north], [west, south],
]]

export function buildFallbackParcels() {
  const features = []
  const widths = [0.00235, 0.00265, 0.00215, 0.00255, 0.0024, 0.0027]
  const heights = [0.00215, 0.00245, 0.00225, 0.00255]
  const uses = ['Agricultural', 'Orchard', 'Residential', 'Mixed']
  const types = ['Dry crop land', 'Horticultural land', 'Settlement land', 'Mixed-use land']
  const verification = ['Verified', 'Pending Verification', 'Requires Verification']
  const risks = ['Normal', 'Requires Verification', 'Flagged for Review']
  const talukas = ['Ratnagiri', 'Ratnagiri', 'Chiplun', 'Sangameshwar']
  const villages = ['Nachane Demo Village', 'Mirjole Demo Village', 'Chiplun Demo Village', 'Sangameshwar Demo Village']
  const timestamp = '2026-08-15T10:30:00+00:00'
  let id = 1
  for (let row = 0; row < 4; row += 1) {
    let x = 73.3032
    for (let col = 0; col < 6; col += 1) {
      const west = x + (row % 2 ? 0.00012 : 0)
      const south = 16.9908 + heights.slice(0, row).reduce((a, b) => a + b, 0) + row * 0.00018
      const parcelId = `RTN-${talukas[row].slice(0, 3).toUpperCase()}-${String(id).padStart(4, '0')}`
      const properties = {
        parcel_id: parcelId, survey_number: `SYN-${100 + id}`, village: villages[row], taluka: talukas[row], district: 'Ratnagiri',
        area_hectares: Number((widths[col] * heights[row] * 12100 * 0.91).toFixed(2)), land_type: types[(row + col) % 4],
        land_use: uses[(row * 2 + col) % 4], record_status: id % 7 === 0 ? 'Under Review' : 'Active',
        verification_status: verification[(row + col * 2) % 3], risk_status: risks[(row * 2 + col) % 3],
        record_reference: `DEMO-REC-${String(id).padStart(4, '0')}`, record_type: 'Synthetic Parcel Record',
        source_label: 'LANDSTACK Demo Dataset', is_synthetic: true, created_at: timestamp, updated_at: timestamp,
      }
      features.push({ type: 'Feature', id: parcelId, geometry: { type: 'Polygon', coordinates: ring(west, south, west + widths[col], south + heights[row]) }, properties })
      x += widths[col] + 0.00018
      id += 1
    }
  }
  return { type: 'FeatureCollection', features }
}

export function filterFallbackParcels(collection, filters) {
  const search = filters.search.trim().toLowerCase()
  return {
    ...collection,
    features: collection.features.filter(({ properties: p }) => {
      const matchesSearch = !search || [p.parcel_id, p.survey_number, p.village].some((value) => value.toLowerCase().includes(search))
      return matchesSearch && ['taluka', 'land_use', 'verification_status', 'risk_status'].every((key) => !filters[key] || p[key] === filters[key])
    }),
  }
}
