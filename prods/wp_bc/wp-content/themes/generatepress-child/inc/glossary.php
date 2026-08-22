<?php

add_action( 'pre_get_posts', function ( $query ) {
	if ( ! is_admin() && $query->is_main_query() && is_post_type_archive( 'bc_quote_author' ) ) {
		$query->set( 'orderby', 'title' );
		$query->set( 'order', 'ASC' );
		$query->set( 'posts_per_page', -1 );
	}
} );

add_action( 'after_setup_theme', function () {
	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}

	$menu_name = 'Menú Principal';
	$menu      = wp_get_nav_menu_object( $menu_name );

	if ( $menu ) {
		return;
	}

	$menu_id = wp_create_nav_menu( $menu_name );

	wp_update_nav_menu_item( $menu_id, 0, array(
		'menu-item-title'  => 'Inicio',
		'menu-item-url'    => home_url( '/' ),
		'menu-item-status' => 'publish',
	) );

	$glosarios_id = wp_update_nav_menu_item( $menu_id, 0, array(
		'menu-item-title'  => 'Glosarios',
		'menu-item-url'    => '#',
		'menu-item-status' => 'publish',
	) );

	wp_update_nav_menu_item( $menu_id, 0, array(
		'menu-item-title'    => 'Personas',
		'menu-item-url'      => get_post_type_archive_link( 'bc_quote_author' ),
		'menu-item-status'   => 'publish',
		'menu-item-parent-id' => $glosarios_id,
	) );

	$locations = get_theme_mod( 'nav_menu_locations', array() );
	$locations['primary'] = $menu_id;
	set_theme_mod( 'nav_menu_locations', $locations );
} );
