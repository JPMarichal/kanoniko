<?php get_header(); ?>

<main id="main" class="bc-glossary-archive">
	<div class="grid-container">
		<header class="bc-glossary-header">
			<h1 class="bc-glossary-title">Glosario de Personas</h1>
		</header>

		<?php if ( have_posts() ) : ?>

			<?php
			$entries = array();
			while ( have_posts() ) {
				the_post();
				$pid   = get_the_ID();
				$first = strtoupper( mb_substr( get_the_title(), 0, 1 ) );
				if ( ! preg_match( '/[A-ZÁÉÍÓÚÑ]/u', $first ) ) {
					$first = '#';
				}
				$entries[ $first ][] = array(
					'pid'       => $pid,
					'title'     => get_the_title(),
					'permalink' => get_permalink(),
					'is_ga'     => (int) get_post_meta( $pid, '_author_is_ga', true ),
					'witness'   => get_post_meta( $pid, '_author_witness_type', true ),
					'callings'  => wp_get_post_terms( $pid, 'bc_author_calling', array( 'fields' => 'slugs' ) ),
				);
			}
			ksort( $entries );

			$all_callings = get_terms( array(
				'taxonomy'   => 'bc_author_calling',
				'hide_empty' => true,
				'orderby'    => 'name',
				'order'      => 'ASC',
			) );
			?>

			<div class="bc-glossary-filters">
				<input type="text" id="bc-filter-search" class="bc-filter-input" placeholder="🔍 Buscar persona…" autocomplete="off">
				<select id="bc-filter-calling" class="bc-filter-select">
					<option value="">Llamamiento: Todos</option>
					<?php foreach ( $all_callings as $term ) : ?>
						<option value="<?php echo esc_attr( $term->slug ); ?>"><?php echo esc_html( $term->name ); ?></option>
					<?php endforeach; ?>
				</select>
				<select id="bc-filter-ga" class="bc-filter-select">
					<option value="">Autoridad General: Todos</option>
					<option value="1">Es Autoridad General</option>
					<option value="0">No es Autoridad General</option>
				</select>
				<select id="bc-filter-witness" class="bc-filter-select">
					<option value="">Testigo: Todos</option>
					<option value="three-witnesses">Uno de los tres testigos</option>
					<option value="eight-witnesses">Uno de los ocho testigos</option>
				</select>
			</div>

			<nav class="bc-glossary-nav" aria-label="Saltar a letra">
				<?php foreach ( array_keys( $entries ) as $letter ) : ?>
					<a href="#glosario-letra-<?php echo esc_attr( $letter ); ?>" class="bc-glossary-nav-link"><?php echo esc_html( $letter ); ?></a>
				<?php endforeach; ?>
			</nav>

			<div id="bc-glossary-no-results" class="bc-glossary-no-results" style="display:none;">
				<p>No se encontraron personas con los filtros seleccionados.</p>
			</div>

			<?php foreach ( $entries as $letter => $items ) : ?>
				<section id="glosario-letra-<?php echo esc_attr( $letter ); ?>" class="bc-glossary-letter-group">
					<h2 class="bc-glossary-letter-heading"><?php echo esc_html( $letter ); ?></h2>
					<div class="row row-cols-1 row-cols-sm-2 row-cols-lg-3">
						<?php foreach ( $items as $item ) : ?>
							<div class="col bc-glossary-entry"
								data-name="<?php echo esc_attr( mb_strtolower( $item['title'] ) ); ?>"
								data-ga="<?php echo esc_attr( $item['is_ga'] ); ?>"
								data-witness="<?php echo esc_attr( $item['witness'] ); ?>"
								data-callings="<?php echo esc_attr( implode( ',', $item['callings'] ) ); ?>">
								<a href="<?php echo esc_url( $item['permalink'] ); ?>" class="bc-glossary-entry-link"><?php echo esc_html( $item['title'] ); ?></a>
							</div>
						<?php endforeach; ?>
					</div>
				</section>
			<?php endforeach; ?>

			<script>
			(function() {
				var search  = document.getElementById('bc-filter-search');
				var calling = document.getElementById('bc-filter-calling');
				var ga      = document.getElementById('bc-filter-ga');
				var witness = document.getElementById('bc-filter-witness');
				var groups  = document.querySelectorAll('.bc-glossary-letter-group');
				var noResults = document.getElementById('bc-glossary-no-results');

				function filter() {
					var sv = search.value.toLowerCase().trim();
					var cv = calling.value;
					var gv = ga.value;
					var wv = witness.value;
					var totalVisible = 0;

					groups.forEach(function(g) {
						var entries = g.querySelectorAll('.bc-glossary-entry');
						var groupVisible = false;

						entries.forEach(function(e) {
							var show = true;
							if (sv && e.getAttribute('data-name').indexOf(sv) === -1) show = false;
							if (cv && e.getAttribute('data-callings').indexOf(cv) === -1) show = false;
							if (gv !== '' && e.getAttribute('data-ga') !== gv) show = false;
							if (wv && e.getAttribute('data-witness') !== wv) show = false;
							e.style.display = show ? '' : 'none';
							if (show) groupVisible = true;
						});

						g.style.display = groupVisible ? '' : 'none';
						if (groupVisible) totalVisible++;
					});

					noResults.style.display = totalVisible === 0 ? '' : 'none';
				}

				search.addEventListener('input', filter);
				calling.addEventListener('change', filter);
				ga.addEventListener('change', filter);
				witness.addEventListener('change', filter);
			})();
			</script>

		<?php else : ?>
			<p><?php esc_html_e( 'No se encontraron personas.', 'generatepress' ); ?></p>
		<?php endif; ?>
	</div>
</main>

<?php get_footer(); ?>
