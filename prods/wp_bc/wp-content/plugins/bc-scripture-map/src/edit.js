import { useBlockProps } from '@wordpress/block-editor';
import { Spinner } from '@wordpress/components';
import { useState, useEffect, useRef, useCallback } from '@wordpress/element';
import { __ } from '@wordpress/i18n';
import apiFetch from '@wordpress/api-fetch';
import InspectorPanel from './components/InspectorPanel';
import MapCanvas from './components/MapCanvas';

export default function Edit({ attributes, setAttributes }) {
	const blockProps = useBlockProps();
	const [allLocations, setAllLocations] = useState([]);
	const [loading, setLoading] = useState(true);
	const [search, setSearch] = useState('');
	const [typeFilter, setTypeFilter] = useState('');
	const [page, setPage] = useState(1);
	const [hasMore, setHasMore] = useState(false);
	const [totalLocations, setTotalLocations] = useState(0);
	const searchTimer = useRef(null);

	const fetchLocations = useCallback((q, type, pg) => {
		setLoading(true);
		const params = new URLSearchParams();
		if (q) params.set('search', q);
		if (type) params.set('type', type);
		params.set('page', pg);
		params.set('per_page', 50);

		apiFetch({ path: '/bc-scripture-map/v1/locations?' + params.toString(), parse: false })
			.then((response) => {
				const totalPages = parseInt(response.headers.get('X-WP-TotalPages') || '1', 10);
				return response.json().then((data) => ({ data, totalPages }));
			})
			.then(({ data, totalPages }) => {
				if (Array.isArray(data)) {
					setAllLocations((prev) => (pg === 1 ? data : [...prev, ...data]));
					setHasMore(pg < totalPages);
				}
			})
			.catch(() => {
				if (pg === 1) setAllLocations([]);
			})
			.finally(() => setLoading(false));
	}, []);

	const fetchTotalCount = useCallback(() => {
		apiFetch({ path: '/bc-scripture-map/v1/locations?per_page=1', parse: false })
			.then((response) => {
				setTotalLocations(parseInt(response.headers.get('X-WP-Total') || '0', 10));
			})
			.catch(() => {});
	}, []);

	useEffect(() => {
		fetchTotalCount();
	}, [fetchTotalCount]);

	useEffect(() => {
		setPage(1);
		fetchLocations(search, typeFilter, 1);
	}, [search, typeFilter, fetchLocations]);

	useEffect(() => {
		if (page > 1) {
			fetchLocations(search, typeFilter, page);
		}
	}, [page, search, typeFilter, fetchLocations]);

	const handleSearch = (value) => {
		clearTimeout(searchTimer.current);
		searchTimer.current = setTimeout(() => {
			setSearch(value);
		}, 300);
	};

	const handleTypeFilter = (value) => {
		setTypeFilter(value);
	};

	const handleLoadMore = () => {
		setPage((p) => p + 1);
	};

	const selectedLocations = allLocations.filter((loc) =>
		(attributes.locationIds || []).includes(loc.id)
	);

	const mapData = {
		centerLng: attributes.centerLng,
		centerLat: attributes.centerLat,
		zoom: attributes.zoom,
		pitch: attributes.pitch,
		bearing: attributes.bearing,
		exaggeration: attributes.exaggeration,
		locations: selectedLocations,
		routes: attributes.routes || [],
		regions: attributes.regions || [],
	};

	return (
		<>
			<InspectorPanel
				attributes={attributes}
				setAttributes={setAttributes}
				locations={allLocations}
				loading={loading}
				hasMore={hasMore}
				onSearch={handleSearch}
				onTypeFilter={handleTypeFilter}
				onLoadMore={handleLoadMore}
				totalLocations={totalLocations}
				typeFilter={typeFilter}
			/>
			<div {...blockProps}>
				{attributes.mapTitle && (
					<h3 className="bc-scripture-map-title">{attributes.mapTitle}</h3>
				)}
				{loading && allLocations.length === 0 ? (
					<div className="bc-map-loading">
						<Spinner />
						<span>{__('Cargando ubicaciones…', 'bc-scripture-map')}</span>
					</div>
				) : (
					<MapCanvas
						data={mapData}
						height={attributes.height}
						isEditor={true}
					/>
				)}
			</div>
		</>
	);
}
