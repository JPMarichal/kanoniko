import { useBlockProps, RichText } from '@wordpress/block-editor';

export default function Save({ attributes }) {
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
						<span className="bc-quote-open" aria-hidden="true">&#x201C;</span>
						<RichText.Content tagName="p" value={quoteText} />
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
	);
}
