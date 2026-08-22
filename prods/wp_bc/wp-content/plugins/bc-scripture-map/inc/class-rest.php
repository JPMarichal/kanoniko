<?php

function bc_scripture_map_register_routes() {
	register_rest_route( 'bc-scripture-map/v1', '/locations', array(
		'methods'             => 'GET',
		'callback'            => 'bc_scripture_map_get_locations',
		'permission_callback' => function () {
			return current_user_can( 'edit_posts' );
		},
	) );
	register_rest_route( 'bc-scripture-map/v1', '/locations/(?P<id>\d+)', array(
		'methods'             => 'GET',
		'callback'            => 'bc_scripture_map_get_single_location',
		'permission_callback' => function () {
			return current_user_can( 'edit_posts' );
		},
	) );
}
add_action( 'rest_api_init', 'bc_scripture_map_register_routes' );

function bc_scripture_map_get_locations( $request ) {
	$type   = $request->get_param( 'type' );
	$source = $request->get_param( 'source' );
	$search = $request->get_param( 'search' );
	$page   = max( 1, (int) $request->get_param( 'page' ) );
	$per_page = min( 100, max( 1, (int) $request->get_param( 'per_page' ) ?: 50 ) );

	$args = array(
		'post_type'      => 'bc_location',
		'posts_per_page' => $per_page,
		'paged'          => $page,
		'orderby'        => 'title',
		'order'          => 'ASC',
	);

	$meta_query = array();
	if ( $type ) {
		$meta_query[] = array(
			'key'   => '_bc_loc_type',
			'value' => sanitize_text_field( $type ),
		);
	}
	if ( $source ) {
		$meta_query[] = array(
			'key'   => '_bc_loc_source',
			'value' => sanitize_text_field( $source ),
		);
	}
	if ( count( $meta_query ) > 1 ) {
		$meta_query['relation'] = 'AND';
	}
	if ( ! empty( $meta_query ) ) {
		$args['meta_query'] = $meta_query;
	}

	if ( $search ) {
		$args['s'] = sanitize_text_field( $search );
	}

	$query = new WP_Query( $args );
	$items = array();

	foreach ( $query->posts as $post ) {
		$scriptures = get_post_meta( $post->ID, '_bc_loc_scriptures', true );
		$items[] = array(
			'id'          => $post->ID,
			'title'       => get_the_title( $post ),
			'lat'         => (float) get_post_meta( $post->ID, '_bc_loc_lat', true ),
			'lng'         => (float) get_post_meta( $post->ID, '_bc_loc_lng', true ),
			'type'        => get_post_meta( $post->ID, '_bc_loc_type', true ),
			'icon'        => get_post_meta( $post->ID, '_bc_loc_icon', true ),
			'scriptures'  => $scriptures ? json_decode( $scriptures, true ) : array(),
			'description' => get_post_meta( $post->ID, '_bc_loc_description', true ),
			'dateFrom'    => (int) get_post_meta( $post->ID, '_bc_loc_date_from', true ),
			'dateTo'      => (int) get_post_meta( $post->ID, '_bc_loc_date_to', true ),
			'source'      => get_post_meta( $post->ID, '_bc_loc_source', true ),
			'confidence'  => get_post_meta( $post->ID, '_bc_loc_confidence', true ),
		);
	}

	$response = rest_ensure_response( $items );
	$response->header( 'X-WP-Total', (int) $query->found_posts );
	$response->header( 'X-WP-TotalPages', (int) $query->max_num_pages );
	return $response;
}

function bc_scripture_map_get_single_location( $request ) {
	$id = (int) $request->get_param( 'id' );
	$post = get_post( $id );
	if ( ! $post || $post->post_type !== 'bc_location' ) {
		return new WP_Error( 'not_found', __( 'Ubicación no encontrada.', 'bc-scripture-map' ), array( 'status' => 404 ) );
	}

	$scriptures = get_post_meta( $post->ID, '_bc_loc_scriptures', true );
	return rest_ensure_response( array(
		'id'          => $post->ID,
		'title'       => get_the_title( $post ),
		'lat'         => (float) get_post_meta( $post->ID, '_bc_loc_lat', true ),
		'lng'         => (float) get_post_meta( $post->ID, '_bc_loc_lng', true ),
		'type'        => get_post_meta( $post->ID, '_bc_loc_type', true ),
		'icon'        => get_post_meta( $post->ID, '_bc_loc_icon', true ),
		'scriptures'  => $scriptures ? json_decode( $scriptures, true ) : array(),
		'description' => get_post_meta( $post->ID, '_bc_loc_description', true ),
		'dateFrom'    => (int) get_post_meta( $post->ID, '_bc_loc_date_from', true ),
		'dateTo'      => (int) get_post_meta( $post->ID, '_bc_loc_date_to', true ),
		'source'      => get_post_meta( $post->ID, '_bc_loc_source', true ),
		'confidence'  => get_post_meta( $post->ID, '_bc_loc_confidence', true ),
	) );
}
