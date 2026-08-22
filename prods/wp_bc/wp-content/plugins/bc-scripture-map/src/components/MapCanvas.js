import { useEffect, useRef } from '@wordpress/element';

const MAPLIBRE_CSS = 'https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css';

const TYPE_CONFIG = {
	city:        { path: 'M10 8h4v7h-4zm1 0v2h2V8z',                        color: '#e74c3c' },
	settlement:  { path: 'M9 11l3-3 3 3v4H9z',                             color: '#9b59b6' },
	mountain:    { path: 'M12 7l5 7H7z',                                    color: '#8B4513' },
	sea:         { path: 'M8 11q2-3 4 0q2 3 4 0v4H8z',                     color: '#2980b9' },
	river:       { path: 'M12 7l-4 5h8z',                                   color: '#5dade2' },
	region:      { path: 'M12 8l4 4-4 4-4-4z',                              color: '#27ae60' },
	wilderness:  { path: 'M12 7l3 4h-2v4h-2v-4H9z',                         color: '#e67e22' },
	landmark:    { path: 'M12 7l1.5 3.5 3.5.5-2.5 2.5.5 3.5L12 15l-3 2 .5-3.5L7 11l3.5-.5z', color: '#f1c40f' },
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

export default function MapCanvas({ data, height, isEditor }) {
	const containerRef = useRef(null);
	const mapRef = useRef(null);

	useEffect(() => {
		if (mapRef.current) return;

		const el = containerRef.current;
		if (!el) return;

		let cancelled = false;

		const init = async () => {
			if (!document.querySelector('link[href="' + MAPLIBRE_CSS + '"]')) {
				const link = document.createElement('link');
				link.rel = 'stylesheet';
				link.href = MAPLIBRE_CSS;
				document.head.appendChild(link);
			}

			let maplibregl;
			try {
				maplibregl = await import('maplibre-gl');
				maplibregl = maplibregl.default || maplibregl;
			} catch (e) {
				console.warn('MapLibre GL JS failed to load:', e);
				el.innerHTML =
					'<div style="padding:40px;text-align:center;color:#666">' +
					'<p>Mapa no disponible en el editor.</p>' +
					'<p style="font-size:12px">El mapa se mostrará correctamente en la página publicada.</p>' +
					'</div>';
				return;
			}

			if (cancelled) return;

			try {
				const map = new maplibregl.Map({
					container: el,
					style: getBaseStyle(data.tileProvider || 'openfreemap'),
					center: [data.centerLng || 35.2, data.centerLat || 31.8],
					zoom: data.zoom || 6,
					pitch: isEditor ? 0 : data.pitch || 45,
					bearing: data.bearing || 0,
					interactive: isEditor,
					attributionControl: false,
				});

				map.on('style.load', () => {
					if (isEditor) {
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
					}

					if (data.locations && data.locations.length) {
						addMarkers(map, data.locations, maplibregl);
						fitMapToLocations(map, data.locations, maplibregl);
					}

					if (!isEditor && data.routes && data.routes.length) {
						addRoutes(map, data.routes, maplibregl);
					}

					if (!isEditor && data.regions && data.regions.length) {
						addRegions(map, data.regions, maplibregl);
					}
				});

				map.on('resize', () => map.resize());
				mapRef.current = map;
			} catch (e) {
				console.warn('MapLibre init error:', e);
				el.innerHTML =
					'<div style="padding:40px;text-align:center;color:#666">Mapa del editor</div>';
			}
		};

		init();

		return () => {
			cancelled = true;
			if (mapRef.current) {
				mapRef.current.remove();
				mapRef.current = null;
			}
		};
	}, []);

	return (
		<div
			ref={containerRef}
			className="bc-scripture-map-canvas"
			style={{ height: height || 500, width: '100%', borderRadius: 4, overflow: 'hidden' }}
		/>
	);
}

function getBaseStyle(provider) {
	if (provider === 'satellite') {
		return {
			version: 8,
			sources: {
				raster: {
					type: 'raster',
					tiles: [
						'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
					],
					tileSize: 256,
				},
			},
			layers: [{ id: 'raster-layer', type: 'raster', source: 'raster' }],
		};
	}
	return {
		version: 8,
		sources: {
			osm: {
				type: 'raster',
				tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
				tileSize: 256,
				maxzoom: 19,
			},
			topo: {
				type: 'raster',
				tiles: ['https://tile.opentopomap.org/{z}/{x}/{y}.png'],
				tileSize: 256,
				maxzoom: 17,
			},
		},
		layers: [
			{
				id: 'base-layer',
				type: 'raster',
				source: provider === 'topo' ? 'topo' : 'osm',
			},
		],
	};
}

function fitMapToLocations(map, locations, maplibregl) {
	if (locations.length === 0) return;
	const bounds = new maplibregl.LngLatBounds();
	locations.forEach((loc) => bounds.extend([loc.lng, loc.lat]));
	map.fitBounds(bounds, { padding: 60, maxZoom: 14 });
}

function addMarkers(map, locations, maplibregl) {
	locations.forEach((loc) => {
		if (!loc.lat || !loc.lng) return;
		const el = document.createElement('div');
		el.className = 'bc-map-marker';
		el.innerHTML = getMarkerSvg(loc.type);
		el.style.cursor = 'pointer';

		let popupHtml = `<div class="bc-map-popup"><h4>${loc.title}</h4>`;
		if (loc.description) popupHtml += `<p>${loc.description}</p>`;
		if (loc.scriptures && loc.scriptures.length) {
			const refs = loc.scriptures
				.map((s) => (typeof s === 'string' ? s : s.ref))
				.filter(Boolean)
				.join(', ');
			if (refs) popupHtml += `<p class="bc-map-refs"><strong>Ref:</strong> ${refs}</p>`;
		}
		popupHtml += '</div>';

		new maplibregl.Marker({ element: el })
			.setLngLat([loc.lng, loc.lat])
			.setPopup(new maplibregl.Popup({ offset: 25 }).setHTML(popupHtml))
			.addTo(map);
	});
}

function addRoutes(map, routes, maplibregl) {
	routes.forEach((route) => {
		if (!route.coordinates || route.coordinates.length < 2) return;
		const id = `r-${Math.random().toString(36).slice(2, 7)}`;
		map.addSource(id, {
			type: 'geojson',
			data: {
				type: 'Feature',
				geometry: { type: 'LineString', coordinates: route.coordinates },
				properties: {},
			},
		});
		map.addLayer({
			id,
			type: 'line',
			source: id,
			paint: {
				'line-color': route.color || '#3498db',
				'line-width': route.width || 3,
				'line-opacity': 0.8,
			},
		});
	});
}

function addRegions(map, regions, maplibregl) {
	regions.forEach((region) => {
		if (!region.coordinates || region.coordinates.length < 3) return;
		const id = `rg-${Math.random().toString(36).slice(2, 7)}`;
		map.addSource(id, {
			type: 'geojson',
			data: {
				type: 'Feature',
				geometry: { type: 'Polygon', coordinates: [region.coordinates] },
				properties: {},
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
	});
}
