import { useState, useEffect } from '@wordpress/element';
import { useBlockProps, RichText, InspectorControls } from '@wordpress/block-editor';
import {
	SelectControl,
	Button,
	TextControl,
	PanelBody,
	Placeholder,
	Spinner,
} from '@wordpress/components';
import apiFetch from '@wordpress/api-fetch';
import { __ } from '@wordpress/i18n';

function getBestPhotoUrl(media) {
	if (!media) return '';
	const sizes = media.media_details?.sizes;
	return (
		sizes?.bc_quote_photo?.source_url ||
		sizes?.thumbnail?.source_url ||
		sizes?.medium?.source_url ||
		media.source_url
	);
}

export default function Edit({ attributes, setAttributes, isSelected }) {
	const {
		authorId,
		authorName,
		authorPhotoUrl,
		quoteText,
		citationSource,
	} = attributes;

	const [authors, setAuthors] = useState([]);
	const [isLoading, setIsLoading] = useState(true);

	useEffect(() => {
		fetchAuthors();
	}, []);

	function fetchAuthors() {
		setIsLoading(true);
		apiFetch({
			path: '/wp/v2/quote-authors?per_page=100&_embed',
		})
			.then((data) => {
				setAuthors(data);
				setIsLoading(false);
			})
			.catch(() => setIsLoading(false));
	}

	function handleAuthorChange(id) {
		const author = authors.find((a) => a.id === parseInt(id));
		if (author) {
			const media = author._embedded?.['wp:featuredmedia']?.[0];
			setAttributes({
				authorId: author.id,
				authorName: author.title.rendered,
				authorPhotoUrl: getBestPhotoUrl(media),
			});
		} else {
			setAttributes({
				authorId: 0,
				authorName: '',
				authorPhotoUrl: '',
			});
		}
	}

	const authorOptions = authors.map((a) => ({
		label: a.title.rendered,
		value: a.id,
	}));

	const blockProps = useBlockProps();

	const commonFormats = [
		'core/bold',
		'core/italic',
		'core/text-color',
	];

	if (!authorId && !isSelected) {
		return (
			<div {...blockProps}>
				<Placeholder
					icon="format-quote"
					label={__('Cita SUD', 'bc-quote-block')}
					instructions={__('Selecciona un autor para comenzar.', 'bc-quote-block')}
				>
					<div className="bc-quote-placeholder-controls">
						{isLoading ? (
							<Spinner />
						) : (
							<>
								<SelectControl
									value={authorId}
									options={[
										{ label: '— Seleccionar Autor —', value: 0 },
										...authorOptions,
									]}
									onChange={handleAuthorChange}
								/>
								<Button
									variant="secondary"
									onClick={() => window.open('post-new.php?post_type=bc_quote_author', '_blank')}
								>
									{__('+ Nuevo Autor', 'bc-quote-block')}
								</Button>
							</>
						)}
					</div>
				</Placeholder>
			</div>
		);
	}

	return (
		<>
			<InspectorControls>
				<PanelBody title={__('Autor', 'bc-quote-block')} initialOpen={true}>
					{isLoading ? (
						<Spinner />
					) : (
						<>
							<SelectControl
								label={__('Seleccionar Autor', 'bc-quote-block')}
								value={authorId}
								options={[
									{ label: '— Seleccionar —', value: 0 },
									...authorOptions,
								]}
								onChange={handleAuthorChange}
							/>
							<Button
								variant="secondary"
								isSmall
								onClick={() => window.open('post-new.php?post_type=bc_quote_author', '_blank')}
								style={{ marginTop: 8 }}
							>
								{__('+ Nuevo Autor', 'bc-quote-block')}
							</Button>
						</>
					)}
				</PanelBody>
				<PanelBody title={__('Fuente', 'bc-quote-block')} initialOpen={true}>
					<TextControl
						label={__('Añade la fuente de la cita', 'bc-quote-block')}
						help={__('Ej: "Si sólo amanece", Conferencia General de octubre 2014', 'bc-quote-block')}
						value={citationSource}
						onChange={(v) => setAttributes({ citationSource: v })}
					/>
				</PanelBody>
			</InspectorControls>

			<div {...blockProps}>
				<div className="bc-quote-card">
					<div className="bc-quote-main">
						{authorPhotoUrl && (
							<div className="bc-quote-photo">
								<img src={authorPhotoUrl} alt={authorName} />
							</div>
						)}
						<div className="bc-quote-text">
							<span className="bc-quote-open" aria-hidden="true">&#x201C;</span>
							<RichText
								tagName="p"
								value={quoteText}
								onChange={(v) => setAttributes({ quoteText: v })}
								placeholder={__('Escribe la cita aquí…', 'bc-quote-block')}
								allowedFormats={commonFormats}
							/>
							<span className="bc-quote-close" aria-hidden="true">&#x201D;</span>
						</div>
					</div>
					{(authorName || citationSource) && (
						<div className="bc-quote-citation">
							{authorName && (
								<span className="bc-quote-author">{authorName}</span>
							)}
							{authorName && citationSource && (
								<span className="bc-quote-sep">, </span>
							)}
							{citationSource && (
								<span className="bc-quote-source">{citationSource}</span>
							)}
						</div>
					)}
				</div>
			</div>
		</>
	);
}
