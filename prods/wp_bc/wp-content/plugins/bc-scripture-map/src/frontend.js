import './style.scss';

const TYPE_CONFIG = {
	city:        { path: 'M10 8h4v7h-4zm1 0v2h2V8z',                        color: '#e74c3c', label: 'Ciudad' },
	settlement:  { path: 'M9 11l3-3 3 3v4H9z',                             color: '#9b59b6', label: 'Asentamiento' },
	mountain:    { path: 'M12 7l5 7H7z',                                    color: '#8B4513', label: 'Montaña' },
	sea:         { path: 'M8 11q2-3 4 0q2 3 4 0v4H8z',                     color: '#2980b9', label: 'Mar' },
	river:       { path: 'M12 7l-4 5h8z',                                   color: '#5dade2', label: 'Río' },
	region:      { path: 'M12 8l4 4-4 4-4-4z',                              color: '#27ae60', label: 'Región' },
	wilderness:  { path: 'M12 7l3 4h-2v4h-2v-4H9z',                         color: '#e67e22', label: 'Desierto' },
	landmark:    { path: 'M12 7l1.5 3.5 3.5.5-2.5 2.5.5 3.5L12 15l-3 2 .5-3.5L7 11l3.5-.5z', color: '#f1c40f', label: 'Emblemático' },
};

function getMarkerSvg(type) {
	const cfg = TYPE_CONFIG[type] || { path: '', color: '#e74c3c' };
	const icon = cfg.path
		? `<path fill="#fff" d="${cfg.path}"/>`
		: '';
	return `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="36" viewBox="0 0 24 36">
		<path fill="${cfg.color}" stroke="rgba(0,0,0,0.2)" stroke-width="0.5" d="M12 0C5.4 0 0 5.4 0 12c0 9 12 24 12 24s12-15 12-24C24 5.4 18.6 0 12 0z"/>
		<circle fill="rgba(255,255,255,0.85)" cx="12" cy="12" r="6"/>
		${icon}
	</svg>`;
}

document.addEventListener('DOMContentLoaded', function () {
	const containers = document.querySelectorAll('.bc-scripture-map-inner[data-map]');
	if (!containers.length) return;

	const linkEl = document.createElement('link');
	linkEl.rel = 'stylesheet';
	linkEl.href = 'https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css';
	document.head.appendChild(linkEl);

	import('maplibre-gl').then((maplibregl) => {
		containers.forEach((container) => {
			try {
				const raw = container.getAttribute('data-map');
				if (!raw) return;
				const data = JSON.parse(raw);
				initMap(container, data, maplibregl.default || maplibregl);
			} catch (e) {
				console.error('Error initializing map:', e);
			}
		});
	});
});

function initMap(container, data, maplibregl) {
	const map = new maplibregl.Map({
		container,
		style: getStyle(data.tileProvider),
		center: [data.centerLng || 35.2, data.centerLat || 31.8],
		zoom: data.zoom || 6,
		pitch: data.pitch || 45,
		bearing: data.bearing || 0,
		attributionControl: true,
	});

	map.addControl(new maplibregl.NavigationControl(), 'top-right');
	map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }));

	map.on('style.load', () => {
		map.addSource('terrain', {
			type: 'raster-dem',
			encoding: 'terrarium',
			tiles: [
				'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png',
			],
			tileSize: 256,
			maxzoom: 15,
		});

		map.setTerrain({
			source: 'terrain',
			exaggeration: data.exaggeration || 1.5,
		});

		if (data.locations && data.locations.length) {
			addMarkers(map, data.locations, maplibregl, data.showLabels);
			fitMapToLocations(map, data.locations);
		}

		if (data.routes && data.routes.length) {
			addRoutes(map, data.routes, maplibregl);
		}

		if (data.regions && data.regions.length) {
			addRegions(map, data.regions, maplibregl);
		}

		const attribution = document.querySelector(
			'.maplibregl-ctrl-attrib .maplibregl-ctrl-attrib-inner'
		);
		if (attribution) {
			const span = document.createElement('span');
			span.innerHTML =
				' | Datos bíblicos © <a href="https://openbible.info/geo/" target="_blank">OpenBible.info</a> (CC-BY)';
			attribution.appendChild(span);
		}
	});

	map.on('resize', () => {
		map.resize();
	});
}

function getStyle(provider) {
	if (provider === 'satellite') {
		return {
			version: 8,
			sources: {
				satellite: {
					type: 'raster',
					tiles: [
						'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
					],
					tileSize: 256,
				},
			},
			layers: [
				{ id: 'satellite-layer', type: 'raster', source: 'satellite' },
			],
		};
	}

	return {
		version: 8,
		sources: {
			osm: {
				type: 'raster',
				tiles: [
					'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
				],
				tileSize: 256,
				maxzoom: 19,
			},
			topo: {
				type: 'raster',
				tiles: [
					'https://tile.opentopomap.org/{z}/{x}/{y}.png',
				],
				tileSize: 256,
				maxzoom: 17,
			},
		},
		layers: [
			{
				id: 'osm-layer',
				type: 'raster',
				source: provider === 'topo' ? 'topo' : 'osm',
			},
		],
	};
}

function fitMapToLocations(map, locations) {
	if (locations.length === 0) return;
	const bounds = new maplibregl.LngLatBounds();
	locations.forEach((loc) => bounds.extend([loc.lng, loc.lat]));
	map.fitBounds(bounds, { padding: 60, maxZoom: 14 });
}

function addMarkers(map, locations, maplibregl, showLabels) {
	locations.forEach((loc) => {
		if (!loc.lat || !loc.lng) return;

		const el = document.createElement('div');
		el.className = 'bc-map-marker';
		el.innerHTML = getMarkerSvg(loc.type);
		el.style.cursor = 'pointer';

		const popupHtml = getPopupHtml(loc);

		const marker = new maplibregl.Marker({ element: el })
			.setLngLat([loc.lng, loc.lat])
			.setPopup(new maplibregl.Popup({ offset: 25 }).setHTML(popupHtml))
			.addTo(map);

		if (showLabels) {
			const labelEl = document.createElement('div');
			labelEl.className = 'bc-map-label';
			labelEl.textContent = loc.title;
			labelEl.style.cssText =
				'position:absolute;bottom:-18px;left:50%;transform:translateX(-50%);font-size:11px;font-weight:bold;color:#333;text-shadow:0 0 3px #fff;white-space:nowrap;pointer-events:none;';
			el.appendChild(labelEl);
		}
	});
}

function getPopupHtml(loc) {
	let html = '<div class="bc-map-popup">';
	html += `<h4>${loc.title}</h4>`;
	if (loc.description) {
		html += `<p>${loc.description}</p>`;
	}
	if (loc.scriptures && loc.scriptures.length) {
		const refs = loc.scriptures
			.map((s) => (typeof s === 'string' ? s : s.ref))
			.filter(Boolean)
			.join(', ');
		if (refs) {
			html += `<p class="bc-map-refs"><strong>Referencias:</strong> ${refs}</p>`;
		}
	}
	if (loc.dateFrom) {
		const dateStr = loc.dateTo
			? `${loc.dateFrom}–${loc.dateTo}`
			: `~${loc.dateFrom}`;
		html += `<p class="bc-map-date"><strong>Período:</strong> ${dateStr}</p>`;
	}
	html += '</div>';
	return html;
}

function addRoutes(map, routes, maplibregl) {
	routes.forEach((route) => {
		if (!route.coordinates || route.coordinates.length < 2) return;
		const id = `route-${Math.random().toString(36).slice(2, 9)}`;
		map.addSource(id, {
			type: 'geojson',
			data: {
				type: 'Feature',
				properties: {},
				geometry: {
					type: 'LineString',
					coordinates: route.coordinates,
				},
			},
		});
		map.addLayer({
			id,
			type: 'line',
			source: id,
			layout: {
				'line-join': 'round',
				'line-cap': 'round',
			},
			paint: {
				'line-color': route.color || '#3498db',
				'line-width': route.width || 3,
				'line-opacity': 0.8,
				'line-dasharray': route.dashed ? [2, 2] : undefined,
			},
		});
	});
}

function addRegions(map, regions, maplibregl) {
	regions.forEach((region) => {
		if (!region.coordinates || region.coordinates.length < 3) return;
		const id = `region-${Math.random().toString(36).slice(2, 9)}`;
		map.addSource(id, {
			type: 'geojson',
			data: {
				type: 'Feature',
				properties: {},
				geometry: {
					type: 'Polygon',
					coordinates: [region.coordinates],
				},
			},
		});
		map.addLayer({
			id,
			type: 'fill',
			source: id,
			paint: {
				'fill-color': region.color || '#2ecc71',
				'fill-opacity': region.opacity || 0.2,
			},
		});
		if (region.label) {
			const centroid = region.coordinates.reduce(
				(acc, c) => [acc[0] + c[0], acc[1] + c[1]],
				[0, 0]
			);
			centroid[0] /= region.coordinates.length;
			centroid[1] /= region.coordinates.length;
			new maplibregl.Marker({ color: 'transparent' })
				.setLngLat(centroid)
				.setPopup(
					new maplibregl.Popup({ closeButton: false }).setHTML(
						`<strong>${region.label}</strong>`
					)
				)
				.addTo(map);
		}
	});
}
