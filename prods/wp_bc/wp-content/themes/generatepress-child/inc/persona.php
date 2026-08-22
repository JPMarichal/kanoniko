<?php

function bc_persona_biography_title( $post_id = 0 ) {
	if ( ! $post_id ) {
		$post_id = get_the_ID();
	}
	$name = get_the_title( $post_id );
	return 'La biografía de ' . $name;
}

function bc_persona_document_title( $parts ) {
	if ( is_singular( 'bc_quote_author' ) ) {
		$parts['title'] = bc_persona_biography_title();
	}
	return $parts;
}
add_filter( 'document_title_parts', 'bc_persona_document_title' );

add_action( 'widgets_init', function () {
	register_sidebar( array(
		'name'          => 'Sidebar de Persona',
		'id'            => 'persona-sidebar',
		'description'   => 'Widgets que aparecen en la página de detalle de cada persona (bc_quote_author).',
		'before_widget' => '<section id="%1$s" class="bc-persona-widget %2$s">',
		'after_widget'  => '</section>',
		'before_title'  => '<h3 class="bc-persona-widget-title">',
		'after_title'   => '</h3>',
	) );
} );

function bc_render_persona_infobox() {
	$post_id = get_the_ID();
	if ( ! $post_id || 'bc_quote_author' !== get_post_type( $post_id ) ) {
		return;
	}

	$desc         = get_post_meta( $post_id, '_author_description', true );
	$is_ga        = get_post_meta( $post_id, '_author_is_ga', true );
	$witness      = get_post_meta( $post_id, '_author_witness_type', true );
	$terms        = wp_get_post_terms( $post_id, 'bc_author_calling', array( 'fields' => 'names' ) );
	$callings     = function_exists( 'carbon_get_post_meta' ) ? carbon_get_post_meta( $post_id, '_author_callings' ) : array();
	if ( empty( $callings ) || ! is_array( $callings ) ) {
		$callings_json = get_post_meta( $post_id, '_author_callings', true );
		$callings      = $callings_json ? json_decode( $callings_json, true ) : array();
	}
	$birth_date   = get_post_meta( $post_id, '_author_birth_date', true );
	$birth_place  = get_post_meta( $post_id, '_author_birth_place', true );
	$death_date   = get_post_meta( $post_id, '_author_death_date', true );
	$death_place  = get_post_meta( $post_id, '_author_death_place', true );
	$nationality  = get_post_meta( $post_id, '_author_nationality', true );
	$father       = get_post_meta( $post_id, '_author_father', true );
	$mother       = get_post_meta( $post_id, '_author_mother', true );
	$spouses      = function_exists( 'carbon_get_post_meta' ) ? carbon_get_post_meta( $post_id, '_author_spouses' ) : array();
	if ( empty( $spouses ) || ! is_array( $spouses ) ) {
		$spouses_json = get_post_meta( $post_id, '_author_spouses', true );
		$spouses      = $spouses_json ? json_decode( $spouses_json, true ) : array();
	}
	?>
	<div class="bc-infobox">
		<?php if ( has_post_thumbnail() ) : ?>
			<div class="bc-infobox-photo">
				<?php the_post_thumbnail( 'bc_quote_photo', array(
					'class' => 'bc-infobox-img',
					'alt'   => get_the_title(),
				) ); ?>
			</div>
		<?php endif; ?>

		<h2 class="bc-infobox-name"><?php the_title(); ?></h2>

		<?php if ( $desc ) : ?>
			<p class="bc-infobox-desc"><?php echo esc_html( $desc ); ?></p>
		<?php endif; ?>

		<ul class="bc-infobox-details">
			<?php if ( $birth_date || $birth_place ) : ?>
				<li>
					<i class="fa-solid fa-cake-candles" aria-hidden="true"></i>
					<span>
						<?php echo esc_html( $birth_date ?: '' ); ?>
						<?php if ( $birth_date && $birth_place ) : ?>, <?php endif; ?>
						<?php echo esc_html( $birth_place ?: '' ); ?>
					</span>
				</li>
			<?php endif; ?>

			<?php if ( $death_date || $death_place ) : ?>
				<li>
					<i class="fa-solid fa-cross" aria-hidden="true"></i>
					<span>
						<?php echo esc_html( $death_date ?: '' ); ?>
						<?php if ( $death_date && $death_place ) : ?>, <?php endif; ?>
						<?php echo esc_html( $death_place ?: '' ); ?>
					</span>
				</li>
			<?php endif; ?>

			<?php if ( $nationality ) : ?>
				<li><i class="fa-solid fa-flag" aria-hidden="true"></i> <span><?php echo esc_html( $nationality ); ?></span></li>
			<?php endif; ?>

		<?php if ( $father ) : ?>
			<li><i class="fa-solid fa-person" aria-hidden="true"></i> <span>Padre: <?php echo esc_html( $father ); ?></span></li>
		<?php endif; ?>
		<?php if ( $mother ) : ?>
			<li><i class="fa-solid fa-person-dress" aria-hidden="true"></i> <span>Madre: <?php echo esc_html( $mother ); ?></span></li>
		<?php endif; ?>

			<?php if ( ! empty( $spouses ) ) : ?>
				<li>
					<i class="fa-solid fa-ring" aria-hidden="true"></i>
					<span>
						<?php foreach ( $spouses as $i => $s ) : ?>
							<?php if ( $i > 0 ) : ?><br><?php endif; ?>
							<?php echo esc_html( $s['name'] ); ?>
							<?php if ( ! empty( $s['marriage_year'] ) ) : ?>
								<span class="bc-infobox-years">(<?php echo esc_html( $s['marriage_year'] ); ?>
								<?php if ( ! empty( $s['end_year'] ) ) : ?>
									&ndash;<?php echo esc_html( $s['end_year'] ); ?>
								<?php endif; ?>)</span>
							<?php endif; ?>
							<?php if ( ! empty( $s['children_count'] ) ) : ?>
								<span class="bc-infobox-children">— <?php echo esc_html( $s['children_count'] ); ?> hijos</span>
							<?php endif; ?>
						<?php endforeach; ?>
					</span>
				</li>
			<?php endif; ?>

			<?php if ( $is_ga ) : ?>
				<li><i class="fa-solid fa-star" aria-hidden="true"></i> <span>Autoridad General</span></li>
			<?php endif; ?>

			<?php if ( 'three-witnesses' === $witness ) : ?>
				<li><i class="fa-solid fa-book-bible" aria-hidden="true"></i> <span>Uno de los tres testigos</span></li>
			<?php elseif ( 'eight-witnesses' === $witness ) : ?>
				<li><i class="fa-solid fa-book-bible" aria-hidden="true"></i> <span>Uno de los ocho testigos</span></li>
			<?php endif; ?>

			<?php if ( $terms ) : ?>
				<li><i class="fa-solid fa-church" aria-hidden="true"></i> <span><?php echo esc_html( implode( ', ', $terms ) ); ?></span></li>
			<?php endif; ?>

			<?php if ( count( $callings ) > 0 ) : ?>
				<li>
					<i class="fa-solid fa-timeline" aria-hidden="true"></i>
					<span>
						<strong>Llamamientos:</strong>
						<ol class="bc-infobox-callings">
								<?php foreach ( $callings as $c ) : ?>
								<li>
									<?php
									$c_org  = $c['org'] ?? '';
									$c_start = $c['start'] ?? '';
									$c_end   = $c['end'] ?? '';
									if ( $c_start || $c_end ) {
										$c_org = preg_replace( '/\s*\(.*?\d{4}.*?\)\s*$/', '', $c_org );
									}
									echo esc_html( trim( $c_org ) );
									?>
									<?php if ( $c_start || $c_end ) : ?>
										<span class="bc-infobox-years">
											(<?php echo esc_html( $c_start ?: '…' ); ?>&ndash;<?php echo esc_html( $c_end ?: 'presente' ); ?>)
										</span>
									<?php endif; ?>
								</li>
							<?php endforeach; ?>
						</ol>
					</span>
				</li>
			<?php endif; ?>
		</ul>
	</div>
	<?php
}
