export const talukaBoundary = {
  type: 'FeatureCollection',
  features: [{
    type: 'Feature',
    properties: { name: 'Ratnagiri Demo Taluka', synthetic: true },
    geometry: {
      type: 'Polygon',
      coordinates: [[
        [73.294, 16.985], [73.325, 16.985], [73.328, 17.006],
        [73.296, 17.008], [73.294, 16.985],
      ]],
    },
  }],
}

export const villageBoundary = {
  type: 'FeatureCollection',
  features: [{
    type: 'Feature',
    properties: { name: 'Nachane Demo Village', synthetic: true },
    geometry: {
      type: 'Polygon',
      coordinates: [[
        [73.3002, 16.9884], [73.3212, 16.9884], [73.322, 17.0026],
        [73.3006, 17.0033], [73.3002, 16.9884],
      ]],
    },
  }],
}
