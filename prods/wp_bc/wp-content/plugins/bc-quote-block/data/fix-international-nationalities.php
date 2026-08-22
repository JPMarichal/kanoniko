<?php
/**
 * Fixes incorrectly assigned "Estadounidense" for international general authorities
 * whose descriptions don't contain explicit nationality keywords.
 * Run: wp eval-file wp-content/plugins/bc-quote-block/data/fix-international-nationalities.php
 */

$fixes = array(
	// África
	'Adeyinka A. Ojediran'      => 'Nigeriana',
	'Alfred Kyungu'             => 'Congoleña',
	'Christian C. Chigbundu'    => 'Nigeriana',
	'Clement M. Matswagothata'  => 'Botsuana',
	'Edward Dube'               => 'Zimbabuense',
	'I. Raymond Egbo'           => 'Nigeriana',
	'Isaac K. Morrison'         => 'Ghanesa',
	'Thabo Lebethoa'            => 'Sudafricana',
	'Thierry K. Mutombo'        => 'Congoleña',

	// Alemania
	'Erich W. Kopischke'        => 'Alemana',
	'Jörg Klebingat'            => 'Alemana',
	'Mathias Held'              => 'Alemana',
	'Michael Cziesla'           => 'Alemana',

	// Argentina
	'Rubén V. Alliaud'          => 'Argentina',
	'Juan Pablo Villar'         => 'Argentina',
	'Ricardo P. Giménez'        => 'Argentina',

	// Bélgica
	'B. Corey Cuvelier'         => 'Belga',

	// Brasil
	'Adilson de Paula Parrella' => 'Brasileña',
	'Aroldo B. Cavalcante'      => 'Brasileña',
	'Ciro Schmeil'              => 'Brasileña',
	'Claudio R. M. Costa'       => 'Brasileña',
	'Denelson Silva'            => 'Brasileña',
	'Helio R. Camargo'          => 'Brasileña',
	'Helvécio Martins'          => 'Brasileña',
	'Jairo Mazzagardi'          => 'Brasileña',
	'Joni L. Koch'              => 'Brasileña',
	'Marcos A. Aidukaitis'      => 'Brasileña',
	'Milton Camargo'            => 'Brasileña',
	'Ozani Farias'              => 'Brasileña',

	// Chile
	'Enrique R. Falabella'      => 'Chilena',
	'Taylor G. Godoy'           => 'Chilena',

	// China / Hong Kong
	'Chi Hong (Sam) Wong'       => 'China',
	'Wan-Liang Wu'              => 'China',

	// Colombia
	'Cristina B. Franco'        => 'Colombiana',

	// España
	'Jose L. Alonso'            => 'Española',

	// Filipinas
	'Benjamin M. Z. Tai'        => 'Filipina',
	'Michael John U. Teh'       => 'Filipina',

	// Francia
	'Christophe G. Giraud-Carrier' => 'Francesa',
	'D. Martin Goury'           => 'Francesa',

	// Guatemala
	'Valeri V. Cordón'          => 'Guatemalteca',

	// Holanda
	'Peter F. Meurs'            => 'Holandesa',

	// Italia
	'Massimo De Feo'            => 'Italiana',

	// Japón
	'Kazuhiko Yamashita'        => 'Japonesa',
	'Koichi Aoyagi'             => 'Japonesa',
	'Takashi Wada'              => 'Japonesa',

	// México
	'Adrian Ochoa'              => 'Mexicana',
	'Arnulfo Valenzuela'        => 'Mexicana',
	'Benjamin De Hoyos'         => 'Mexicana',
	'Gregorio E. Casillas'      => 'Mexicana',
	'Lino Alvarez'              => 'Mexicana',
	'Moises Villanueva'         => 'Mexicana',

	// Nueva Zelanda
	'Ian S. Ardern'             => 'Neozelandesa',

	// Perú
	'Jorge F. Zeballos'         => 'Peruana',
	'Juan A. Uceda'             => 'Peruana',
	'Patricio M. Giuffra'       => 'Peruana',

	// Portugal
	'Horacio A. Tenorio'        => 'Portuguesa',

	// Samoa
	'O. Vincent Haleck'         => 'Samoa',

	// Sudáfrica
	'Christoffel Golden Jr.'    => 'Sudafricana',

	// Tonga
	'Taniela B. Wakolo'         => 'Tongana',
	'Vai Sikahema'              => 'Tongana',

	// Uruguay
	'Eduardo Gavarret'          => 'Uruguaya',
	'Walter F. González'        => 'Uruguaya',

	// Venezuela
	'Enrique E. del Toro'       => 'Venezolana',
	'Pedro X. Larreal'          => 'Venezolana',
	'Rafael E. Pino'            => 'Venezolana',
	'Sergio R. Vargas'          => 'Venezolana',

	// Varios América Latina
	'Eduardo F. Ortega'         => 'Ecuatoriana',
	'Joaquín E. Costa'          => 'Española',
	'Jorge M. Alvarado'         => 'Peruana',
	'Jorge T. Becerra'          => 'Colombiana',
	'Hugo E. Martinez'          => 'Salvadoreña',
	'Sandino Roman'             => 'Panameña',
);

$updated = 0;
$not_found = 0;

$query = new WP_Query( array(
	'post_type'      => 'bc_quote_author',
	'posts_per_page' => -1,
	'fields'         => 'ids',
) );

foreach ( $query->posts as $post_id ) {
	$title    = get_the_title( $post_id );
	$current  = get_post_meta( $post_id, '_author_nationality', true );

	if ( isset( $fixes[ $title ] ) ) {
		$correct = $fixes[ $title ];
		if ( $current !== $correct ) {
			update_post_meta( $post_id, '_author_nationality', $correct );
			$updated++;
			WP_CLI::line( "  {$title}: {$current} → {$correct}" );
		} else {
			WP_CLI::line( "  {$title}: ya correcto ({$current})" );
		}
	}
}

WP_CLI::success( sprintf( 'Corregidos: %d', $updated ) );
