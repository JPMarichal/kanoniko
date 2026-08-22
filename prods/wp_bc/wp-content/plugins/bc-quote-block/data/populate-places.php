<?php
/**
 * Populates _author_birth_place, _author_death_place, _author_spouses
 * from Wikidata P19/P20/P26 data.
 * Run: wp eval-file wp-content/plugins/bc-quote-block/data/populate-places.php
 *
 * Source: bin/wikidata-places.json (fetched via Wikidata API)
 * Matching: corpus/index.json (slug → name) → post_title
 */

$places_path  = __DIR__ . '/../../../../bin/wikidata-places.json';
$index_path   = __DIR__ . '/../../../../bin/index.json';

if ( ! file_exists( $places_path ) ) {
	WP_CLI::error( 'wikidata-places.json not found at: ' . $places_path );
}
if ( ! file_exists( $index_path ) ) {
	WP_CLI::error( 'index.json not found at: ' . $index_path );
}

$places_data = json_decode( file_get_contents( $places_path ), true );
$index_data  = json_decode( file_get_contents( $index_path ), true );

// Build slug → entry map from wikidata-places
$slug_map = array();
foreach ( $places_data as $entry ) {
	if ( ! empty( $entry['slug'] ) ) {
		$slug_map[ $entry['slug'] ] = $entry;
	}
}

// Build name → slug map from index.json (name is post_title)
$name_to_slug = array();
foreach ( $index_data as $slug => $name ) {
	$name_to_slug[ $name ] = $slug;
}

WP_CLI::line( sprintf( 'Loaded %d slug entries from wikidata-places.json', count( $slug_map ) ) );

$updated_birth_place = 0;
$updated_death_place = 0;
$updated_spouses     = 0;
$skipped             = 0;
$not_found           = 0;

$query = new WP_Query( array(
	'post_type'      => 'bc_quote_author',
	'posts_per_page' => -1,
	'fields'         => 'ids',
) );

WP_CLI::line( sprintf( 'Found %d bc_quote_author posts.', $query->post_count ) );

foreach ( $query->posts as $post_id ) {
	$title = get_the_title( $post_id );

	if ( ! isset( $name_to_slug[ $title ] ) ) {
		$not_found++;
		continue;
	}

	$slug = $name_to_slug[ $title ];

	if ( ! isset( $slug_map[ $slug ] ) ) {
		$skipped++;
		continue;
	}

	$data = $slug_map[ $slug ];

	// Birth place
	if ( ! empty( $data['birthPlace'] ) ) {
		$current = get_post_meta( $post_id, '_author_birth_place', true );
		if ( empty( $current ) ) {
			update_post_meta( $post_id, '_author_birth_place', $data['birthPlace'] );
			$updated_birth_place++;
		}
	}

	// Death place
	if ( ! empty( $data['deathPlace'] ) ) {
		$current = get_post_meta( $post_id, '_author_death_place', true );
		if ( empty( $current ) ) {
			update_post_meta( $post_id, '_author_death_place', $data['deathPlace'] );
			$updated_death_place++;
		}
	}

	// Spouses
	if ( ! empty( $data['spouses'] ) && is_array( $data['spouses'] ) ) {
		$current_spouses = get_post_meta( $post_id, '_author_spouses', true );
		if ( empty( $current_spouses ) ) {
			$spouse_entries = array();
			foreach ( $data['spouses'] as $sp ) {
				$entry = array(
					'name' => isset( $sp['spouseName'] ) ? $sp['spouseName'] : ( isset( $sp['spouseQid'] ) ? $sp['spouseQid'] : '' ),
				);
				if ( empty( $entry['name'] ) ) {
					continue;
				}
				if ( ! empty( $sp['marriageDate'] ) ) {
					// Extract year from Wikidata date format: +1841-00-00T00:00:00Z
					if ( preg_match( '/^\+?(\d{4})/', $sp['marriageDate'], $m ) ) {
						$entry['marriage_year'] = (int) $m[1];
					}
				}
				if ( ! empty( $sp['endDate'] ) ) {
					if ( preg_match( '/^\+?(\d{4})/', $sp['endDate'], $m ) ) {
						$entry['end_year'] = (int) $m[1];
					}
				}
				if ( isset( $sp['childrenCount'] ) ) {
					$entry['children_count'] = (int) $sp['childrenCount'];
				}
				$spouse_entries[] = $entry;
			}
			if ( ! empty( $spouse_entries ) ) {
				update_post_meta( $post_id, '_author_spouses', wp_json_encode( $spouse_entries, JSON_UNESCAPED_UNICODE ) );
				$updated_spouses++;
			}
		}
	}
}

WP_CLI::success( sprintf(
	'Birth places: %d | Death places: %d | Spouses: %d | Skipped (no data): %d | Not found in index: %d',
	$updated_birth_place,
	$updated_death_place,
	$updated_spouses,
	$skipped,
	$not_found
) );
