<?php
/**
 * Populates _author_nationality for bc_quote_author posts from corpus data.
 * Run: wp eval-file wp-content/plugins/bc-quote-block/data/populate-nationality.php
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

$index_path = __DIR__ . '/../../index.json';
$name_to_slug = array();

if ( file_exists( $index_path ) ) {
	$index = json_decode( file_get_contents( $index_path ), true );
	if ( $index ) {
		$name_to_slug = array_flip( $index );
	}
}

function extract_nationality( $text, $map ) {
	if ( ! $text ) {
		return null;
	}

	// Try multi-word nationalities first (e.g. "Costa Rican", "Puerto Rican", "South African", "New Zealand")
	$multi = array( 'Costa Rican', 'Puerto Rican', 'South African', 'New Zealand' );
	foreach ( $multi as $m ) {
		if ( stripos( $text, $m ) !== false ) {
			return $map[ $m ] ?? null;
		}
	}

	// Extract first word and check
	$first = strtok( $text, ' ' );
	if ( $first && isset( $map[ $first ] ) ) {
		return $map[ $first ];
	}

	// Search for any nationality word embedded in text
	foreach ( $map as $en => $es ) {
		if ( in_array( $en, $multi, true ) ) {
			continue; // Already handled
		}
		if ( preg_match( '/\b' . preg_quote( $en, '/' ) . '\b/i', $text ) ) {
			return $es;
		}
	}

	return null;
}

$updated = 0;
$skipped = 0;
$found   = 0;

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

	// Source 2: wikidata descriptions (flat file)
	$wd_descs = array();
	if ( ! $nationality ) {
		$wd_desc_path = __DIR__ . '/../../../../bin/wikidata-descriptions.json';
		if ( file_exists( $wd_desc_path ) ) {
			$wd_descs = json_decode( file_get_contents( $wd_desc_path ), true ) ?: array();
			if ( isset( $wd_descs[ $title ] ) ) {
				$nationality = extract_nationality( $wd_descs[ $title ], $map );
			}
		}
	}

	// Source 3: fallback — infer from description_en/wikidata
	// If no explicit non-US nationality is found, assign Estadounidense.
	// Non-US persons consistently include nationality in their descriptions.
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

	// Source 4: Name-based heuristic mapping for people without Wikidata/Wikipedia presence
	$name_nationality = array(
		'Won Yong Ko'              => 'Surcoreana',
		'Han In Sang'              => 'Surcoreana',
		'Kwok Yuen Tai'            => 'China',
		'Wolfgang H. Paul'         => 'Alemana',
		'Adhemar Damiani'          => 'Brasileña',
		'Milton da Rocha Camargo'  => 'Brasileña',
		'Michele G. Pisanu'        => 'Italiana',
		'Augusto A. Lim'           => 'Filipina',
		'Carlos G. Revillo Jr.'    => 'Filipina',
		'Christoffel Golden Jr.'   => 'Sudafricana',
		'Derek A. Cuthbert'        => 'Británica',
		'Charles A. Didier'        => 'Belga',
		'Gerald E. Melchin'        => 'Canadiense',
		'Alexander D. Acheson'     => 'Canadiense',
		'José A. Teixeira'         => 'Portuguesa',
		'Angel Abrea'              => 'Argentina',
		'Claudio D. Zivic'         => 'Argentina',
		'Carlos H. Amado'          => 'Venezolana',
		'Francisco J. Viñas'       => 'Uruguaya',
		'Eduardo Ayala'            => 'Chilena',
		'Sergio E. Muñoz'          => 'Chilena',
		'Hector Barrero'           => 'Colombiana',
		'Julio E. Dávila'          => 'Mexicana',
		'Rosemary K. Chibota'      => 'Zimbabuense',
		'Benjamin De Hoyos'        => 'Mexicana',
		'Horacio A. Tenorio'       => 'Mexicana',
		'Enrique R. Falabella'     => 'Guatemalteca',
		'Joaquín E. Costa'         => 'Argentina',
		'Cristina B. Franco'       => 'Argentina',
		'Eduardo F. Ortega'        => 'Argentina',
		'Jorge F. Zeballos'        => 'Chilena',
		'Taylor G. Godoy'          => 'Peruana',
		'Sandino Roman'            => 'Mexicana',
		'Jorge M. Alvarado'        => 'Puertorriqueña',
		'Hugo E. Martinez'         => 'Puertorriqueña',
		'Adilson de Paula Parrella' => 'Brasileña',
		'Adeyinka A. Ojediran'     => 'Nigeriana',
		'Alfred Kyungu'            => 'Congoleña',
		'Arnulfo Valenzuela'       => 'Mexicana',
		'Aroldo B. Cavalcante'     => 'Brasileña',
		'B. Corey Cuvelier'        => 'Belga',
		'Benjamin M. Z. Tai'       => 'Filipina',
		'Chi Hong (Sam) Wong'      => 'China',
		'Christian C. Chigbundu'   => 'Nigeriana',
		'Christophe G. Giraud-Carrier' => 'Francesa',
		'Ciro Schmeil'             => 'Brasileña',
		'Claudio R. M. Costa'      => 'Brasileña',
		'Clement M. Matswagothata' => 'Botsuana',
		'Denelson Silva'           => 'Brasileña',
		'D. Martin Goury'          => 'Francesa',
		'Edward Dube'              => 'Zimbabuense',
		'Erich W. Kopischke'       => 'Alemana',
		'Gregorio E. Casillas'     => 'Mexicana',
		'Helio R. Camargo'         => 'Brasileña',
		'Helvécio Martins'         => 'Brasileña',
		'I. Raymond Egbo'          => 'Nigeriana',
		'Ian S. Ardern'            => 'Neozelandesa',
		'Isaac K. Morrison'        => 'Ghanesa',
		'Jairo Mazzagardi'         => 'Brasileña',
		'Joni L. Koch'             => 'Brasileña',
		'Jörg Klebingat'           => 'Alemana',
		'Jose L. Alonso'           => 'Mexicana',
		'Juan A. Uceda'            => 'Peruana',
		'Juan Pablo Villar'        => 'Argentina',
		'Kazuhiko Yamashita'       => 'Japonesa',
		'Koichi Aoyagi'            => 'Japonesa',
		'Lino Alvarez'             => 'Mexicana',
		'Marcos A. Aidukaitis'     => 'Brasileña',
		'Massimo De Feo'           => 'Italiana',
		'Mathias Held'             => 'Alemana',
		'Michael Cziesla'          => 'Alemana',
		'Michael John U. Teh'      => 'Filipina',
		'Milton Camargo'           => 'Brasileña',
		'Moises Villanueva'        => 'Mexicana',
		'O. Vincent Haleck'        => 'Samoa',
		'Ozani Farias'             => 'Brasileña',
		'Patricio M. Giuffra'      => 'Peruana',
		'Pedro X. Larreal'         => 'Venezolana',
		'Peter F. Meurs'           => 'Holandesa',
		'Rafael E. Pino'           => 'Venezolana',
		'Ricardo P. Giménez'       => 'Argentina',
		'Rubén V. Alliaud'         => 'Argentina',
		'Sergio R. Vargas'         => 'Venezolana',
		'Takashi Wada'             => 'Japonesa',
		'Taniela B. Wakolo'        => 'Tongana',
		'Thabo Lebethoa'           => 'Sudafricana',
		'Thierry K. Mutombo'       => 'Congoleña',
		'Valeri V. Cordón'         => 'Guatemalteca',
		'Vai Sikahema'             => 'Tongana',
		'Wan-Liang Wu'             => 'China',
		'Walter F. González'       => 'Uruguaya',
		'Yoon Hwan Choi'           => 'Surcoreana',
	);
	if ( ! $nationality && isset( $name_nationality[ $title ] ) ) {
		$nationality = $name_nationality[ $title ];
	}

	if ( $nationality ) {
		update_post_meta( $post_id, '_author_nationality', $nationality );
		$updated++;
		WP_CLI::line( "  {$title} → {$nationality}" );
	} else {
		// Source 5: If all else fails, default to Estadounidense
		update_post_meta( $post_id, '_author_nationality', 'Estadounidense' );
		$updated++;
		WP_CLI::line( "  {$title} → Estadounidense (default)" );
	}
}

WP_CLI::success( sprintf( 'Updated: %d, Already had nationality: %d, Not found: %d', $updated, $skipped, $found ) );
