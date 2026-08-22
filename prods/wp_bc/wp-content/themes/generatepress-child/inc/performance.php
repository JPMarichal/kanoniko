<?php

function bc_minify_html( $buffer ) {
  $search = [
    '/\>[^\S ]+/s',
    '/[^\S ]+\</s',
    '/(\s)+/s',
    '/<!--(.|\s)*?-->/',
  ];
  $replace = [ '>', '<', '\\1', '' ];
  return preg_replace( $search, $replace, $buffer );
}

function bc_start_html_minify() {
  ob_start( 'bc_minify_html' );
}
add_action( 'after_setup_theme', 'bc_start_html_minify' );

function bc_preconnect_origins() {
  $hostname = '';
  if ( class_exists( 'Indigetal\BunnyNet\Settings\BunnyConfigurationStore' ) ) {
    $hostname = Indigetal\BunnyNet\Settings\BunnyConfigurationStore::getStoragePullZoneHostname();
  }

  $hostname = apply_filters( 'bc_preconnect_cdn', $hostname );

  if ( $hostname ) {
    echo '<link rel="preconnect" href="//' . esc_attr( $hostname ) . '">' . "\n";
  }

  echo '<link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>' . "\n";
  echo '<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>' . "\n";
}
add_action( 'wp_head', 'bc_preconnect_origins', -1 );

function bc_lazy_load_iframes( $content ) {
  return str_replace( '<iframe ', '<iframe loading="lazy" ', $content );
}
add_filter( 'the_content', 'bc_lazy_load_iframes', 20 );

function bc_preload_fonts() {
  $font_url = get_stylesheet_directory_uri() . '/fonts/merriweather-latin.woff2';
  echo '<link rel="preload" as="font" href="' . esc_url( $font_url ) . '" type="font/woff2" crossorigin>' . "\n";
}
add_action( 'wp_head', 'bc_preload_fonts', 1 );

function bc_preload_hero_image() {
  if ( ! is_singular() || ! has_post_thumbnail() ) {
    return;
  }

  $post      = get_queried_object();
  $image_url = get_the_post_thumbnail_url( $post, 'bc-hero' );

  if ( ! $image_url ) {
    return;
  }

  echo '<link rel="preload" as="image" href="' . esc_url( $image_url ) . '">' . "\n";
}
add_action( 'wp_head', 'bc_preload_hero_image', 2 );
