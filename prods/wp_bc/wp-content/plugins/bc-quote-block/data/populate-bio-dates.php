<?php
/**
 * Populates _author_birth_date and _author_death_date from corpus data.
 * Run: wp eval-file wp-content/plugins/bc-quote-block/data/populate-bio-dates.php
 *
 * Sources (in order):
 *   1. authors-enriched.json → birthYear / deathYear
 *   2. personajes/<slug>/wikidata.json → birthDate / deathDate
 */

$json_path = __DIR__ . '/../../../../bin/authors-enriched.json';

if ( ! file_exists( $json_path ) ) {
	WP_CLI::error( 'authors-enriched.json not found at: ' . $json_path );
}

$enriched     = json_decode( file_get_contents( $json_path ), true );
$enriched_idx = array();

foreach ( $enriched as $author ) {
	$enriched_idx[ trim( $author['name'] ) ] = $author;
}

$updated_birth = 0;
$updated_death = 0;
$skipped       = 0;

$query = new WP_Query( array(
	'post_type'      => 'bc_quote_author',
	'posts_per_page' => -1,
	'fields'         => 'ids',
) );

WP_CLI::line( sprintf( 'Found %d posts.', $query->post_count ) );

foreach ( $query->posts as $post_id ) {
	$title       = get_the_title( $post_id );
	$birth_val   = null;
	$death_val   = null;

	// Source 1: authors-enriched.json
	if ( isset( $enriched_idx[ $title ] ) ) {
		$item = $enriched_idx[ $title ];
		if ( ! empty( $item['birthYear'] ) ) {
			$birth_val = $item['birthYear'];
		}
		if ( ! empty( $item['deathYear'] ) ) {
			$death_val = $item['deathYear'];
		}
	}

	// Source 2: wikidata-bio.json (flattened)
	if ( ! $birth_val || ! $death_val ) {
		$wd_bio_path = __DIR__ . '/../../../../bin/wikidata-bio.json';
		if ( file_exists( $wd_bio_path ) ) {
			$wd_bio = json_decode( file_get_contents( $wd_bio_path ), true );
			if ( isset( $wd_bio[ $title ] ) ) {
				$entry = $wd_bio[ $title ];
				if ( ! $birth_val && ! empty( $entry['birthDate'] ) ) {
					$birth_val = $entry['birthDate'];
				}
				if ( ! $death_val && ! empty( $entry['deathDate'] ) ) {
					$death_val = $entry['deathDate'];
				}
			}
		}
	}

	if ( $birth_val ) {
		$current = get_post_meta( $post_id, '_author_birth_date', true );
		if ( ! $current ) {
			update_post_meta( $post_id, '_author_birth_date', (string) $birth_val );
			$updated_birth++;
		}
	}

	if ( $death_val ) {
		$current = get_post_meta( $post_id, '_author_death_date', true );
		if ( ! $current ) {
			update_post_meta( $post_id, '_author_death_date', (string) $death_val );
			$updated_death++;
		}
	}
}

WP_CLI::success( sprintf( 'Birth dates updated: %d, Death dates updated: %d', $updated_birth, $updated_death ) );
