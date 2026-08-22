<?php
/**
 * Seeds bc_quote_author CPT from authors.json
 * Run: wp eval-file wp-content/plugins/bc-quote-block/data/seed-authors.php
 */

$json_path = __DIR__ . '/authors.json';

if ( ! file_exists( $json_path ) ) {
	WP_CLI::error( 'authors.json not found at: ' . $json_path );
}

$json    = file_get_contents( $json_path );
$authors = json_decode( $json, true );

if ( json_last_error() !== JSON_ERROR_NONE ) {
	WP_CLI::error( 'Error parsing JSON: ' . json_last_error_msg() );
}

WP_CLI::line( sprintf( 'Found %d authors in JSON.', count( $authors ) ) );

$created = 0;
$updated = 0;
$skipped = 0;

$three_witnesses = array( 'Oliver Cowdery', 'David Whitmer', 'Martin Harris' );
$eight_witnesses = array( 'Christian Whitmer', 'Jacob Whitmer', 'Peter Whitmer Jr.', 'John Whitmer', 'Hiram Page', 'Joseph Smith Sr.', 'Hyrum Smith', 'Samuel H. Smith' );

foreach ( $authors as $author ) {
	$name     = trim( $author['name'] );
	$raw_desc = trim( $author['description'] ?? '' );

	if ( empty( $name ) ) {
		WP_CLI::warning( 'Skipping entry with empty name.' );
		$skipped++;
		continue;
	}

	$existing = new WP_Query( array(
		'post_type'              => 'bc_quote_author',
		'title'                  => $name,
		'posts_per_page'         => 1,
		'no_found_rows'          => true,
		'ignore_sticky_posts'    => true,
		'update_post_meta_cache' => false,
		'update_post_term_cache' => false,
	) );
	$post     = $existing->have_posts() ? $existing->posts[0] : null;

	if ( ! $post ) {
		$post_id = wp_insert_post( array(
			'post_title'  => $name,
			'post_type'   => 'bc_quote_author',
			'post_status' => 'publish',
		) );

		if ( is_wp_error( $post_id ) ) {
			WP_CLI::warning( "Error creating {$name}: " . $post_id->get_error_message() );
			$skipped++;
			continue;
		}

		$created++;
	} else {
		$post_id = $post->ID;
		$updated++;
	}

	// Determine callings: use explicit field if present, else parse from description
	if ( isset( $author['callings'] ) && is_array( $author['callings'] ) && ! empty( $author['callings'] ) ) {
		$callings   = $author['callings'];
		$last       = $callings[ count( $callings ) - 1 ];
		$short_desc = $last['org'];
	} else {
		$short_desc = $raw_desc;
		$parts      = explode( ' — ', $raw_desc );
		if ( count( $parts ) > 1 ) {
			$short_desc = trim( end( $parts ) );
		}
		$callings = bc_parse_callings_from_description( $raw_desc );
	}

	update_post_meta( $post_id, '_author_description', $short_desc );

	if ( ! empty( $callings ) ) {
		update_post_meta( $post_id, '_author_callings', wp_json_encode( $callings, JSON_UNESCAPED_UNICODE ) );

		$term_slugs = array_unique( array_column( $callings, 'calling' ) );
		wp_set_object_terms( $post_id, $term_slugs, 'bc_author_calling', false );
	}

	// Witness type
	if ( in_array( $name, $three_witnesses, true ) ) {
		update_post_meta( $post_id, '_author_witness_type', 'three-witnesses' );
	} elseif ( in_array( $name, $eight_witnesses, true ) ) {
		update_post_meta( $post_id, '_author_witness_type', 'eight-witnesses' );
	} elseif ( preg_match( '/Testigo del Libro de Mormón/i', $raw_desc ) ) {
		update_post_meta( $post_id, '_author_witness_type', 'three-witnesses' );
	}

	// _author_is_ga (via description OR term slugs)
	$is_ga = false;

	if ( preg_match( '/Presidente de la Iglesia/i', $raw_desc ) && ! preg_match( '/Obispo Presidente|Patriarca Presidente/i', $raw_desc ) ) {
		$is_ga = true;
	}
	if ( preg_match( '/Consejero de (la )?Primera Presidencia/i', $raw_desc ) ) {
		$is_ga = true;
	}
	if ( preg_match( '/Apóstol/i', $raw_desc ) && ! preg_match( '/Asistente al Cuórum/i', $raw_desc ) ) {
		$is_ga = true;
	}
	if ( preg_match( '/Setenta/i', $raw_desc ) ) {
		$is_ga = true;
	}
	if ( preg_match( '/Obispo Presidente|Obispado Presidente/i', $raw_desc ) ) {
		$is_ga = true;
	}
	if ( preg_match( '/Patriarca/i', $raw_desc ) ) {
		$is_ga = true;
	}
	if ( preg_match( '/Presidente Asistente de la Iglesia|Consejero Asistente de la Primera Presidencia/i', $raw_desc ) ) {
		$is_ga = true;
	}

	// Also check assigned term slugs (more robust)
	if ( ! $is_ga && ! empty( $term_slugs ) ) {
		$ga_slugs = array( 'presidente-de-la-iglesia', 'consejero-primera-presidencia', 'apostol', 'setenta-autoridad-general', 'obispo-presidente', 'obispado-presidente', 'patriarca-general', 'consejero-asistente-pp', 'asistente-cuorum-doce' );
		foreach ( $term_slugs as $slug ) {
			if ( in_array( $slug, $ga_slugs, true ) ) {
				$is_ga = true;
				break;
			}
		}
	}

	update_post_meta( $post_id, '_author_is_ga', $is_ga );

	// Safety net: non-GA Witnesses must never use 'apostol' calling slug
	$witness_type = get_post_meta( $post_id, '_author_witness_type', true );
	if ( $witness_type && ! $is_ga && ! empty( $callings ) ) {
		$fixed = false;
		foreach ( $callings as $i => $c ) {
			if ( $c['calling'] === 'apostol' ) {
				$callings[ $i ]['calling'] = 'testigo';
				$fixed = true;
			}
		}
		if ( $fixed ) {
			update_post_meta( $post_id, '_author_callings', wp_json_encode( $callings, JSON_UNESCAPED_UNICODE ) );
			$term_slugs = array_unique( array_column( $callings, 'calling' ) );
			wp_set_object_terms( $post_id, $term_slugs, 'bc_author_calling', false );
		}
	}
}

WP_CLI::success( "Done. Created: {$created}, Updated: {$updated}, Skipped: {$skipped}" );

/**
 * Parses a description string into an array of calling entries.
 */
function bc_parse_callings_from_description( $desc ) {
	if ( empty( $desc ) ) {
		return array();
	}

	$start = null;
	$end   = null;

	if ( preg_match( '/(\d{4})[–\-](\d{4})/u', $desc, $m ) ) {
		$start = (int) $m[1];
		$end   = (int) $m[2];
	} elseif ( preg_match( '/\((\d{4})\)/', $desc, $m ) ) {
		$start = (int) $m[1];
	} elseif ( preg_match( '/a partir del \d+ de \w+ de (\d{4})/', $desc, $m ) ) {
		$start = (int) $m[1];
	}

	$slug = 'otro';

	if ( preg_match( '/Presidente de la Iglesia/i', $desc ) && ! preg_match( '/Obispo Presidente|Patriarca Presidente/i', $desc ) ) {
		$slug = 'presidente-de-la-iglesia';
	} elseif ( preg_match( '/Consejero de (la )?Primera Presidencia/i', $desc ) && ! preg_match( '/Consejero Asistente de la Primera Presidencia/i', $desc ) ) {
		$slug = 'consejero-primera-presidencia';
	} elseif ( preg_match( '/Apóstol/i', $desc ) && ! preg_match( '/Asistente al Cuórum/i', $desc ) ) {
		$slug = 'apostol';
	} elseif ( preg_match( '/Setenta/i', $desc ) ) {
		$slug = 'setenta-autoridad-general';
	} elseif ( preg_match( '/Asistente al Cuórum de los Doce/i', $desc ) ) {
		$slug = 'asistente-cuorum-doce';
	} elseif ( preg_match( '/^Obispo Presidente/i', $desc ) ) {
		$slug = 'obispo-presidente';
	} elseif ( preg_match( '/(Primer|Segundo) Consejero del Obispado Presidente|Asistente del Obispo Presidente/i', $desc ) ) {
		$slug = 'obispado-presidente';
	} elseif ( preg_match( '/Patriarca/i', $desc ) ) {
		$slug = 'patriarca-general';
	} elseif ( preg_match( '/Sociedad de Socorro/i', $desc ) && preg_match( '/Presidenta General|Presidencia General|Presidente General/i', $desc ) ) {
		$slug = 'presidencia-sociedad-socorro';
	} elseif ( preg_match( '/Escuela Dominical/i', $desc ) && preg_match( '/Presidenta General|Presidencia General|Presidente General/i', $desc ) ) {
		$slug = 'presidencia-escuela-dominical';
	} elseif ( preg_match( '/Hombres Jóvenes/i', $desc ) && preg_match( '/Presidenta General|Presidencia General|Presidente General/i', $desc ) ) {
		$slug = 'presidencia-hombres-jovenes';
	} elseif ( preg_match( '/Mujeres Jóvenes/i', $desc ) && preg_match( '/Presidenta General|Presidencia General|Presidente General/i', $desc ) ) {
		$slug = 'presidencia-mujeres-jovenes';
	} elseif ( preg_match( '/Primaria/i', $desc ) && preg_match( '/Presidenta General|Presidencia General|Presidente General/i', $desc ) ) {
		$slug = 'presidencia-primaria';
	} elseif ( preg_match( '/Consejero Asistente de la Primera Presidencia/i', $desc ) ) {
		$slug = 'consejero-asistente-pp';
	}

	return array( array(
		'calling' => $slug,
		'org'     => $desc,
		'start'   => $start,
		'end'     => $end,
	) );
}
