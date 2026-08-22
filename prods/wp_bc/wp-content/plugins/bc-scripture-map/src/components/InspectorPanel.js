import { InspectorControls } from '@wordpress/block-editor';
import {
	PanelBody,
	SelectControl,
	RangeControl,
	TextControl,
	ToggleControl,
	Button,
	__experimentalNumberControl as NumberControl,
} from '@wordpress/components';
import { useState } from '@wordpress/element';
import { __ } from '@wordpress/i18n';

const TYPE_OPTIONS = [
	{ label: __('Todos los tipos', 'bc-scripture-map'), value: '' },
	{ label: __('Ciudad', 'bc-scripture-map'), value: 'city' },
	{ label: __('Asentamiento', 'bc-scripture-map'), value: 'settlement' },
	{ label: __('Región', 'bc-scripture-map'), value: 'region' },
	{ label: __('Montaña', 'bc-scripture-map'), value: 'mountain' },
	{ label: __('Mar', 'bc-scripture-map'), value: 'sea' },
	{ label: __('Río', 'bc-scripture-map'), value: 'river' },
	{ label: __('Desierto', 'bc-scripture-map'), value: 'wilderness' },
	{ label: __('Lugar emblemático', 'bc-scripture-map'), value: 'landmark' },
];

export default function InspectorPanel({
	attributes, setAttributes, locations, loading,
	hasMore, onSearch, onTypeFilter, onLoadMore, totalLocations, typeFilter,
}) {
	const [searchInput, setSearchInput] = useState('');
	const selectedIds = attributes.locationIds || [];

	const toggleLocation = (id) => {
		const current = [...selectedIds];
		const idx = current.indexOf(id);
		if (idx !== -1) {
			current.splice(idx, 1);
		} else {
			current.push(id);
		}
		setAttributes({ locationIds: current });
	};

	return (
		<InspectorControls>
			<PanelBody title={__('Configuración del Mapa', 'bc-scripture-map')} initialOpen={true}>
				<TextControl
					label={__('Título del mapa', 'bc-scripture-map')}
					value={attributes.mapTitle || ''}
					onChange={(v) => setAttributes({ mapTitle: v })}
				/>

				<SelectControl
					label={__('Proveedor de mapas', 'bc-scripture-map')}
					value={attributes.tileProvider || 'satellite'}
					options={[
						{ label: __('Satélite (Esri)', 'bc-scripture-map'), value: 'satellite' },
						{ label: __('OpenStreetMap', 'bc-scripture-map'), value: 'openfreemap' },
						{ label: __('OpenTopoMap (relieve)', 'bc-scripture-map'), value: 'topo' },
					]}
					onChange={(v) => setAttributes({ tileProvider: v })}
				/>

				<RangeControl
					label={__('Zoom', 'bc-scripture-map')}
					value={attributes.zoom || 6}
					onChange={(v) => setAttributes({ zoom: v })}
					min={1}
					max={18}
				/>

				<RangeControl
					label={__('Inclinación (pitch)', 'bc-scripture-map')}
					value={attributes.pitch || 45}
					onChange={(v) => setAttributes({ pitch: v })}
					min={0}
					max={85}
				/>

				<RangeControl
					label={__('Exageración del relieve', 'bc-scripture-map')}
					value={attributes.exaggeration || 1.5}
					onChange={(v) => setAttributes({ exaggeration: v })}
					min={0}
					max={5}
					step={0.1}
				/>

				<RangeControl
					label={__('Altura del mapa (px)', 'bc-scripture-map')}
					value={attributes.height || 500}
					onChange={(v) => setAttributes({ height: v })}
					min={200}
					max={800}
					step={50}
				/>

				<ToggleControl
					label={__('Mostrar etiquetas', 'bc-scripture-map')}
					checked={attributes.showLabels !== false}
					onChange={(v) => setAttributes({ showLabels: v })}
				/>
			</PanelBody>

			<PanelBody
				title={
					__('Ubicaciones', 'bc-scripture-map') +
					(totalLocations ? ` (${selectedIds.length} / ${totalLocations})` : '')
				}
				initialOpen={true}
			>
				<TextControl
					label={__('Buscar ubicación…', 'bc-scripture-map')}
					value={searchInput}
					placeholder={__('Escribe para filtrar…', 'bc-scripture-map')}
					onChange={(v) => {
						setSearchInput(v);
						onSearch(v);
					}}
				/>

				<SelectControl
					label={__('Filtrar por tipo', 'bc-scripture-map')}
					value={typeFilter || ''}
					options={TYPE_OPTIONS}
					onChange={(v) => onTypeFilter(v)}
				/>

				{loading && locations.length === 0 ? (
					<p style={{ color: '#666' }}>{__('Cargando ubicaciones…', 'bc-scripture-map')}</p>
				) : locations.length === 0 ? (
					<p style={{ color: '#999', fontStyle: 'italic' }}>
						{__('No hay ubicaciones con ese filtro.', 'bc-scripture-map')}
					</p>
				) : (
					<>
						<div style={{ maxHeight: 300, overflowY: 'auto' }}>
							{locations.map((loc) => (
								<div
									key={loc.id}
									onClick={() => toggleLocation(loc.id)}
									style={{
										padding: '6px 8px',
										cursor: 'pointer',
										background: selectedIds.includes(loc.id) ? '#e3f2fd' : 'transparent',
										borderLeft: selectedIds.includes(loc.id) ? '3px solid #1976d2' : '3px solid transparent',
										marginBottom: 2,
										borderRadius: 2,
									}}
								>
									<label style={{ cursor: 'pointer', fontSize: 13 }}>
										<input
											type="checkbox"
											checked={selectedIds.includes(loc.id)}
											onChange={() => toggleLocation(loc.id)}
											style={{ marginRight: 6 }}
										/>
										{loc.title}
										{loc.type && (
											<span style={{ color: '#888', fontSize: 11, marginLeft: 4 }}>
												({loc.type})
											</span>
										)}
									</label>
								</div>
							))}
						</div>
						{hasMore && (
							<div style={{ textAlign: 'center', marginTop: 8 }}>
								<Button
									isSecondary
									isSmall
									onClick={onLoadMore}
									disabled={loading}
								>
									{loading ? __('Cargando…', 'bc-scripture-map') : __('Cargar más', 'bc-scripture-map')}
								</Button>
							</div>
						)}
					</>
				)}
			</PanelBody>
		</InspectorControls>
	);
}
