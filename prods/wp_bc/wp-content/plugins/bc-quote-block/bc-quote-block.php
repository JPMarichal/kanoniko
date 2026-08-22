<?php
/**
 * Plugin Name: BC Quote Block
 * Description: Un bloque de Gutenberg para mostrar citas SUD con autor y foto opcional.
 * Version: 1.0.0
 * Requires at least: 6.1
 * Requires PHP: 7.4
 * License: GPL-2.0-or-later
 * Text Domain: bc-quote-block
 */

defined( 'ABSPATH' ) || exit;

define( 'BC_QUOTE_BLOCK_VERSION', '1.0.0' );
define( 'BC_QUOTE_BLOCK_DIR', plugin_dir_path( __FILE__ ) );
define( 'BC_QUOTE_BLOCK_URL', plugin_dir_url( __FILE__ ) );

add_image_size( 'bc_quote_photo', 160, 160, true );

function bc_quote_register_author_cpt() {
	register_post_type( 'bc_quote_author', array(
		'labels' => array(
			'name'               => __( 'Personas', 'bc-quote-block' ),
			'singular_name'      => __( 'Persona', 'bc-quote-block' ),
			'add_new'            => __( 'Añadir Nueva', 'bc-quote-block' ),
			'add_new_item'       => __( 'Añadir Nueva Persona', 'bc-quote-block' ),
			'edit_item'          => __( 'Editar Persona', 'bc-quote-block' ),
			'view_item'          => __( 'Ver Persona', 'bc-quote-block' ),
			'search_items'       => __( 'Buscar Personas', 'bc-quote-block' ),
			'not_found'          => __( 'No se encontraron personas', 'bc-quote-block' ),
			'not_found_in_trash' => __( 'No hay personas en la papelera', 'bc-quote-block' ),
		),
		'public'             => true,
		'publicly_queryable' => true,
		'show_ui'            => true,
		'show_in_menu'       => true,
		'menu_icon'          => 'dashicons-businessman',
		'supports'           => array( 'title', 'editor', 'thumbnail', 'comments' ),
		'show_in_rest'       => true,
		'rest_base'          => 'quote-authors',
		'menu_position'      => 25,
		'has_archive'        => true,
		'rewrite'            => array( 'slug' => 'glosario/persona', 'with_front' => false ),
	) );

	register_taxonomy( 'bc_author_calling', 'bc_quote_author', array(
		'labels' => array(
			'name'                       => __( 'Llamamientos', 'bc-quote-block' ),
			'singular_name'              => __( 'Llamamiento', 'bc-quote-block' ),
			'search_items'               => __( 'Buscar Llamamientos', 'bc-quote-block' ),
			'popular_items'              => __( 'Llamamientos Populares', 'bc-quote-block' ),
			'all_items'                  => __( 'Todos los Llamamientos', 'bc-quote-block' ),
			'edit_item'                  => __( 'Editar Llamamiento', 'bc-quote-block' ),
			'update_item'                => __( 'Actualizar Llamamiento', 'bc-quote-block' ),
			'add_new_item'               => __( 'Añadir Nuevo Llamamiento', 'bc-quote-block' ),
			'new_item_name'              => __( 'Nuevo Llamamiento', 'bc-quote-block' ),
			'separate_items_with_commas' => __( 'Separa los llamamientos con comas', 'bc-quote-block' ),
			'add_or_remove_items'        => __( 'Añadir o eliminar llamamientos', 'bc-quote-block' ),
			'choose_from_most_used'      => __( 'Elegir de los más usados', 'bc-quote-block' ),
			'not_found'                  => __( 'No se encontraron llamamientos.', 'bc-quote-block' ),
			'menu_name'                  => __( 'Llamamientos', 'bc-quote-block' ),
		),
		'public'            => false,
		'show_ui'           => true,
		'show_in_menu'      => true,
		'show_in_rest'      => true,
		'rest_base'         => 'author-callings',
		'show_admin_column' => true,
		'hierarchical'      => false,
		'rewrite'           => false,
	) );

	$term_data = array(
		'presidente-de-la-iglesia'      => __( 'Presidente de la Iglesia', 'bc-quote-block' ),
		'consejero-primera-presidencia' => __( 'Consejero en la Primera Presidencia', 'bc-quote-block' ),
		'apostol'                        => __( 'Apóstol', 'bc-quote-block' ),
		'setenta-autoridad-general'      => __( 'Setenta Autoridad General', 'bc-quote-block' ),
		'asistente-cuorum-doce'          => __( 'Asistente al Cuórum de los Doce', 'bc-quote-block' ),
		'obispo-presidente'              => __( 'Obispo Presidente', 'bc-quote-block' ),
		'obispado-presidente'            => __( 'Obispado Presidente', 'bc-quote-block' ),
		'patriarca-general'              => __( 'Patriarca General', 'bc-quote-block' ),
		'presidencia-sociedad-socorro'   => __( 'Presidencia General de la Sociedad de Socorro', 'bc-quote-block' ),
		'presidencia-escuela-dominical'  => __( 'Presidencia General de la Escuela Dominical', 'bc-quote-block' ),
		'presidencia-hombres-jovenes'    => __( 'Presidencia General de los Hombres Jóvenes', 'bc-quote-block' ),
		'presidencia-mujeres-jovenes'    => __( 'Presidencia General de las Mujeres Jóvenes', 'bc-quote-block' ),
		'presidencia-primaria'           => __( 'Presidencia General de la Primaria', 'bc-quote-block' ),
		'consejero-asistente-pp'         => __( 'Consejero Asistente de la Primera Presidencia', 'bc-quote-block' ),
		'otro'                           => __( 'Otro', 'bc-quote-block' ),
		'testigo'                        => __( 'Testigo', 'bc-quote-block' ),
	);

	foreach ( $term_data as $slug => $label ) {
		if ( ! term_exists( $slug, 'bc_author_calling' ) ) {
			wp_insert_term( $label, 'bc_author_calling', array( 'slug' => $slug ) );
		}
	}
}
add_action( 'init', 'bc_quote_register_author_cpt' );

function bc_quote_block_init() {
	register_block_type( BC_QUOTE_BLOCK_DIR . 'block.json' );
}
add_action( 'init', 'bc_quote_block_init' );

function bc_quote_author_columns( $columns ) {
	$new = array();
	foreach ( $columns as $key => $value ) {
		if ( 'title' === $key ) {
			$new['photo'] = __( 'Foto', 'bc-quote-block' );
		}
		$new[ $key ] = $value;
		if ( 'title' === $key ) {
			$new['description'] = __( 'Descripción', 'bc-quote-block' );
		}
		if ( 'description' === $key ) {
			$new['is_ga'] = __( 'GA', 'bc-quote-block' );
		}
	}
	return $new;
}
add_filter( 'manage_bc_quote_author_posts_columns', 'bc_quote_author_columns' );

function bc_quote_author_columns_content( $column, $post_id ) {
	if ( 'photo' === $column ) {
		if ( has_post_thumbnail( $post_id ) ) {
			echo get_the_post_thumbnail( $post_id, array( 40, 40 ), array(
				'style' => 'border-radius:50%;object-fit:cover;width:40px;height:40px',
				'alt'   => get_the_title( $post_id ),
			) );
		} else {
			echo '<span style="color:#999">—</span>';
		}
	}
	if ( 'description' === $column ) {
		$desc = get_post_meta( $post_id, '_author_description', true );
		echo esc_html( $desc ) ?: '<span style="color:#999">—</span>';
	}
	if ( 'is_ga' === $column ) {
		$is_ga = get_post_meta( $post_id, '_author_is_ga', true );
		echo $is_ga ? '✅' : '<span style="color:#999">—</span>';
	}
	if ( 'taxonomy-bc_author_calling' === $column ) {
		$terms = wp_get_post_terms( $post_id, 'bc_author_calling', array( 'fields' => 'names' ) );
		echo $terms ? esc_html( implode( ', ', $terms ) ) : '<span style="color:#999">—</span>';
	}
}
add_action( 'manage_bc_quote_author_posts_custom_column', 'bc_quote_author_columns_content', 10, 2 );

function bc_quote_author_admin_head() {
	$screen = get_current_screen();
	if ( ! $screen || 'bc_quote_author' !== $screen->post_type ) {
		return;
	}
	?>
	<style>
		#postimagediv h2 .dashicons-format-image {
			display: none;
		}
		#postimagediv h2 {
			font-size: 14px;
		}
		.fixed .column-photo {
			width: 60px;
			text-align: center;
		}
	</style>
	<script>
	document.addEventListener( 'DOMContentLoaded', function() {
		var h2 = document.querySelector( '#postimagediv h2' );
		if ( h2 ) h2.textContent = 'Foto del Autor';
		var btn = document.querySelector( '#set-post-thumbnail' );
		if ( btn && btn.innerHTML.indexOf( 'Set featured image' ) !== -1 ) {
			btn.innerHTML = btn.innerHTML.replace( 'Set featured image', 'Seleccionar foto' );
		}
		var del = document.querySelector( '#remove-post-thumbnail' );
		if ( del ) del.textContent = 'Eliminar foto';
	} );
	</script>
	<?php
}
add_action( 'admin_head-post.php', 'bc_quote_author_admin_head' );
add_action( 'admin_head-post-new.php', 'bc_quote_author_admin_head' );
