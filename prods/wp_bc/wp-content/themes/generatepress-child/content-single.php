<?php
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
?>
<article id="post-<?php the_ID(); ?>" <?php post_class(); ?> <?php generate_do_microdata( 'article' ); ?>>
	<div class="inside-article">
		<?php
		do_action( 'generate_before_content' );

		if ( has_post_thumbnail() && is_singular() ) :
			bc_render_share_bar( 'top' );
			?><div class="page-hero">
				<?php the_post_thumbnail( 'bc-hero', array( 'class' => 'page-hero-image', 'fetchpriority' => 'high' ) ); ?>
				<div class="page-hero-content">
					<header class="page-hero-header">
						<?php
						do_action( 'generate_before_entry_title' );
						if ( generate_show_title() ) {
							echo '<div class="page-hero-title-bar">';
							the_title( '<h1 class="entry-title" itemprop="headline">', '</h1>' );
							echo '</div>';
						}
						echo '<div class="page-hero-meta-bar">';
						do_action( 'generate_after_entry_title' );
						echo '</div>';
						?>
					</header>
				</div>
			</div>
			<?php if ( has_excerpt() ) : ?>
				<div class="page-hero-excerpt"><?php the_excerpt(); ?></div>
			<?php endif; ?>
			<?php
		endif;

		if ( generate_show_entry_header() && ! has_post_thumbnail() ) :
			?>
			<header <?php generate_do_attr( 'entry-header' ); ?>>
				<?php
				do_action( 'generate_before_entry_title' );

				if ( generate_show_title() ) {
					$params = generate_get_the_title_parameters();
					the_title( $params['before'], $params['after'] );
				}

				do_action( 'generate_after_entry_title' );
				?>
			</header>
			<?php
		endif;

		do_action( 'generate_after_entry_header' );

		$itemprop = '';
		if ( 'microdata' === generate_get_schema_type() ) {
			$itemprop = ' itemprop="text"';
		}
		?>
		<div class="entry-content"<?php echo $itemprop; ?>>
			<?php
			the_content();

			wp_link_pages(
				array(
					'before' => '<div class="page-links">' . __( 'Pages:', 'generatepress' ),
					'after'  => '</div>',
				)
			);
			?>
		</div>
		<?php
		bc_render_share_bar( 'bottom' );
		do_action( 'generate_after_entry_content' );
		do_action( 'generate_after_content' );
		?>
	</div>
</article>
