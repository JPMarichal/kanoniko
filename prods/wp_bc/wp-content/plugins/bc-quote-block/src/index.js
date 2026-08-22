import { registerBlockType } from '@wordpress/blocks';
import { useBlockProps, RichText } from '@wordpress/block-editor';
import './style.scss';
import './editor.scss';
import Edit from './edit';
import Save from './save';
import metadata from '../block.json';

const deprecated = [
	{
		attributes: {
			authorId: { type: 'number', default: 0 },
			authorName: { type: 'string', default: '' },
			authorPhotoUrl: { type: 'string', default: '' },
			quoteText: { type: 'string', source: 'html', selector: '.bc-quote-text' },
			citationSource: { type: 'string', default: '' },
		},
		save({ attributes }) {
			const {
				authorName,
				authorPhotoUrl,
				quoteText,
				citationSource,
			} = attributes;
			const blockProps = useBlockProps.save();
			return (
				<div {...blockProps}>
					<div className="bc-quote-card">
						<div className="bc-quote-main">
							{authorPhotoUrl && (
								<div className="bc-quote-photo">
									<img src={authorPhotoUrl} alt={authorName} />
								</div>
							)}
							<div className="bc-quote-text">
								<RichText.Content tagName="p" value={quoteText} />
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
			);
		},
		migrate(attributes) {
			const text = (attributes.quoteText || '')
				.replace(/<\/?p>/gi, '')
				.replace(/<\/?br\s*\/?>/gi, '')
				.trim();
			return { ...attributes, quoteText: text };
		},
	},
];

registerBlockType(metadata.name, {
	edit: Edit,
	save: Save,
	deprecated,
});
