<?php
/**
 * Populates _author_nationality for bc_quote_author posts — v2.
 * Sources in order:
 *   1. authors-enriched.json description_en (existing logic)
 *   2. wikidata descriptions (existing logic)
 *   3. Name-based heuristic mapping (new)
 *   4. Default "Estadounidense"
 * Run: wp eval-file wp-content/plugins/bc-quote-block/data/populate-nationality-v2.php
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

$map = array(
	'American'     => 'Estadounidense',
	'Mexican'      => 'Mexicana',
	'Canadian'     => 'Canadiense',
	'British'      => 'Británica',
	'English'      => 'Inglesa',
	'Welsh'        => 'Galesa',
	'Scottish'     => 'Escocesa',
	'Irish'        => 'Irlandesa',
	'German'       => 'Alemana',
	'French'       => 'Francesa',
	'Italian'      => 'Italiana',
	'Swiss'        => 'Suiza',
	'Dutch'        => 'Holandesa',
	'Belgian'      => 'Belga',
	'Austrian'     => 'Austriaca',
	'Danish'       => 'Danesa',
	'Swedish'      => 'Sueca',
	'Norwegian'    => 'Noruega',
	'Finnish'      => 'Finlandesa',
	'Icelandic'    => 'Islandesa',
	'Polish'       => 'Polaca',
	'Czech'        => 'Checa',
	'Hungarian'    => 'Húngara',
	'Greek'        => 'Griega',
	'Russian'      => 'Rusa',
	'Ukrainian'    => 'Ucraniana',
	'Australian'   => 'Australiana',
	'New Zealand'  => 'Neozelandesa',
	'Japanese'     => 'Japonesa',
	'Korean'       => 'Surcoreana',
	'Chinese'      => 'China',
	'Filipino'     => 'Filipina',
	'Brazilian'    => 'Brasileña',
	'Argentine'    => 'Argentina',
	'Chilean'      => 'Chilena',
	'Peruvian'     => 'Peruana',
	'Uruguayan'    => 'Uruguaya',
	'Paraguayan'   => 'Paraguaya',
	'Bolivian'     => 'Boliviana',
	'Ecuadorian'   => 'Ecuatoriana',
	'Colombian'    => 'Colombiana',
	'Venezuelan'   => 'Venezolana',
	'Guatemalan'   => 'Guatemalteca',
	'Honduran'     => 'Hondureña',
	'Salvadoran'   => 'Salvadoreña',
	'Nicaraguan'   => 'Nicaragüense',
	'Costa Rican'  => 'Costarricense',
	'Panamanian'   => 'Panameña',
	'Cuban'        => 'Cubana',
	'Dominican'    => 'Dominicana',
	'Puerto Rican' => 'Puertorriqueña',
	'Haitian'      => 'Haitiana',
	'Jamaican'     => 'Jamaicana',
	'South African' => 'Sudafricana',
	'Nigerian'     => 'Nigeriana',
	'Ghanaian'     => 'Ghanesa',
	'Kenyan'       => 'Keniana',
	'Ethiopian'    => 'Etíope',
	'Egyptian'     => 'Egipcia',
	'Moroccan'     => 'Marroquí',
	'Algerian'     => 'Argelina',
	'Tunisian'     => 'Tunecina',
	'Libyan'       => 'Libia',
	'Sudanese'     => 'Sudanesa',
	'Zimbabwean'   => 'Zimbabuense',
	'Mozambican'   => 'Mozambiqueña',
	'Angolan'      => 'Angoleña',
	'Congolese'    => 'Congoleña',
	'Samoan'       => 'Samoa',
	'Tongan'       => 'Tongana',
	'Fijian'       => 'Fiyiana',
	'Tahitian'     => 'Tahitiana',
	'Israeli'      => 'Israelí',
	'Lebanese'     => 'Libanesa',
	'Syrian'       => 'Siria',
	'Iraqi'        => 'Iraquí',
	'Iranian'      => 'Iraní',
	'Afghan'       => 'Afgana',
	'Pakistani'    => 'Pakistaní',
	'Indonesian'   => 'Indonesia',
	'Malaysian'    => 'Malasia',
	'Thai'         => 'Tailandesa',
	'Vietnamese'   => 'Vietnamita',
	'Burmese'      => 'Birmana',
	'Cambodian'    => 'Camboyana',
	'Nepalese'     => 'Nepalesa',
	'Bangladeshi'  => 'Bangladesí',
	'Sri Lankan'   => 'Ceilandesa',
	'Mongolian'    => 'Mongola',
	'Gibraltarian' => 'Gibraltareña',
);

function extract_nationality( $text, $map ) {
	if ( ! $text ) {
		return null;
	}
	$multi = array( 'Costa Rican', 'Puerto Rican', 'South African', 'New Zealand' );
	foreach ( $multi as $m ) {
		if ( stripos( $text, $m ) !== false ) {
			return $map[ $m ] ?? null;
		}
	}
	$first = strtok( $text, ' ' );
	if ( $first && isset( $map[ $first ] ) ) {
		return $map[ $first ];
	}
	foreach ( $map as $en => $es ) {
		if ( in_array( $en, $multi, true ) ) {
			continue;
		}
		if ( preg_match( '/\b' . preg_quote( $en, '/' ) . '\b/i', $text ) ) {
			return $es;
		}
	}
	return null;
}

$date_loaded = false;
$wd_descs    = array();

// Known non-US LDS general authorities — mapped by name
$name_nationality = array(
	// Korea
	'Won Yong Ko'       => 'Surcoreana',
	'Han In Sang'       => 'Surcoreana',

	// China / Hong Kong
	'Kwok Yuen Tai'     => 'China',

	// Alemania
	'Wolfgang H. Paul'  => 'Alemana',

	// Brasil
	'Adhemar Damiani'   => 'Brasileña',
	'Milton da Rocha Camargo' => 'Brasileña',

	// Italia
	'Michele G. Pisanu' => 'Italiana',

	// Filipinas
	'Augusto A. Lim'    => 'Filipina',
	'Carlos G. Revillo Jr.' => 'Filipina',

	// Sudáfrica
	'Christoffel Golden Jr.' => 'Sudafricana',

	// Reino Unido
	'Derek A. Cuthbert' => 'Británica',

	// Bélgica
	'Charles A. Didier' => 'Belga',

	// Canadá
	'Gerald E. Melchin' => 'Canadiense',
	'Alexander D. Acheson' => 'Canadiense',

	// Portugal
	'José A. Teixeira'  => 'Portuguesa',

	// Argentina
	'Angel Abrea'       => 'Argentina',
	'Claudio D. Zivic'  => 'Argentina',

	// Venezuela
	'Carlos H. Amado'   => 'Venezolana',

	// Uruguay
	'Francisco J. Viñas' => 'Uruguaya',

	// Chile
	'Eduardo Ayala'     => 'Chilena',
	'Sergio E. Muñoz'   => 'Chilena',

	// Colombia
	'Hector Barrero'    => 'Colombiana',

	// México
	'Enrique E. del Toro' => 'Mexicana',
	'Julio E. Dávila'   => 'Mexicana',

	// Zimbabue
	'Rosemary K. Chibota' => 'Zimbabuense',
);

$updated = 0;
$skipped = 0;
$found   = 0;
$heuristic = 0;

$query = new WP_Query( array(
	'post_type'      => 'bc_quote_author',
	'posts_per_page' => -1,
	'fields'         => 'ids',
) );

WP_CLI::line( sprintf( 'Found %d posts.', $query->post_count ) );

foreach ( $query->posts as $post_id ) {
	$title   = get_the_title( $post_id );
	$current = get_post_meta( $post_id, '_author_nationality', true );

	if ( $current ) {
		$skipped++;
		continue;
	}

	$nationality = null;

	// Source 1: authors-enriched.json description_en
	if ( isset( $enriched_idx[ $title ]['description_en'] ) ) {
		$nationality = extract_nationality( $enriched_idx[ $title ]['description_en'], $map );
	}

	// Source 2: wikidata descriptions
	if ( ! $nationality ) {
		if ( ! $date_loaded ) {
			$wd_desc_path = __DIR__ . '/../../../../bin/wikidata-descriptions.json';
			if ( file_exists( $wd_desc_path ) ) {
				$wd_descs = json_decode( file_get_contents( $wd_desc_path ), true ) ?: array();
			}
			$date_loaded = true;
		}
		if ( isset( $wd_descs[ $title ] ) ) {
			$nationality = extract_nationality( $wd_descs[ $title ], $map );
		}
	}

	// Source 3: infer from description_en/wikidata (existing fallback)
	if ( ! $nationality ) {
		$text = '';
		if ( isset( $enriched_idx[ $title ]['description_en'] ) ) {
			$text = $enriched_idx[ $title ]['description_en'];
		} elseif ( isset( $wd_descs[ $title ] ) ) {
			$text = $wd_descs[ $title ];
		}
		if ( $text ) {
			$has_non_us = false;
			foreach ( $map as $en => $es ) {
				if ( 'Estadounidense' !== $es && preg_match( '/\b' . preg_quote( $en, '/' ) . '\b/i', $text ) ) {
					$has_non_us = true;
					break;
				}
			}
			if ( ! $has_non_us ) {
				$nationality = 'Estadounidense';
			}
		}
	}

	// Source 4: Name-based heuristic mapping
	if ( ! $nationality && isset( $name_nationality[ $title ] ) ) {
		$nationality = $name_nationality[ $title ];
		$heuristic++;
	}

	// Source 5: Default — Estadounidense
	if ( ! $nationality ) {
		$nationality = 'Estadounidense';
	}

	update_post_meta( $post_id, '_author_nationality', $nationality );
	$updated++;
	WP_CLI::line( "  {$title} → {$nationality}" );
}

WP_CLI::success( sprintf(
	'Updated: %d, Already had: %d, Heuristic: %d',
	$updated, $skipped, $heuristic
) );
