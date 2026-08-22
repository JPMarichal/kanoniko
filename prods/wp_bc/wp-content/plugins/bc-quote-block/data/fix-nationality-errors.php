<?php
/**
 * Fixes confirmed nationality assignment errors.
 * Run: wp eval-file wp-content/plugins/bc-quote-block/data/fix-nationality-errors.php
 */

$fixes = array(
	// Horacio Tenorio: born in Mexico City, Mexico (NOT Portuguese)
	'Horacio A. Tenorio'     => 'Mexicana',

	// Enrique Falabella: born in Guatemala City, Guatemala (NOT Chilean)
	'Enrique R. Falabella'   => 'Guatemalteca',

	// Joaquín Costa: born in Concordia, Argentina (NOT Spanish)
	'Joaquín E. Costa'       => 'Argentina',

	// Cristina Franco: born in Buenos Aires, Argentina (NOT Colombian)
	'Cristina B. Franco'     => 'Argentina',

	// Eduardo Ortega: born in Godoy Cruz, Mendoza, Argentina (NOT Ecuadorian)
	'Eduardo F. Ortega'      => 'Argentina',

	// Jorge Zeballos: born in Ovalle, Chile (NOT Peruvian)
	'Jorge F. Zeballos'      => 'Chilena',

	// Taylor Godoy: born in Lima, Peru (NOT Chilean)
	'Taylor G. Godoy'        => 'Peruana',

	// Sandino Roman: born in Iguala, Guerrero, Mexico (NOT Panamanian)
	'Sandino Roman'          => 'Mexicana',

	// Jorge Alvarado: born in Ponce, Puerto Rico (NOT Peruvian)
	'Jorge M. Alvarado'      => 'Puertorriqueña',

	// Jorge Becerra: born in Salt Lake City, Utah, US (NOT Colombian)
	'Jorge T. Becerra'       => 'Estadounidense',

	// Hugo Martinez: born in Puerto Rico (NOT Salvadoran)
	'Hugo E. Martinez'       => 'Puertorriqueña',
);

$updated = 0;

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
		}
	}
}

WP_CLI::success( sprintf( 'Corregidos: %d', $updated ) );
