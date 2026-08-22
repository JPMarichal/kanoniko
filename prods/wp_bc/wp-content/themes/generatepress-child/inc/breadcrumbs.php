<?php

function bc_render_breadcrumbs() {
  if ( ! is_singular( 'post' ) ) {
    return;
  }

  $post = get_queried_object();
  $cats = get_the_category( $post );

  echo '<div class="bc-breadcrumbs-wrap">';
  echo '<nav class="bc-breadcrumbs" aria-label="Breadcrumb">';
  echo '<a href="' . esc_url( home_url( '/' ) ) . '"><i class="fas fa-home"></i> ' . esc_html( get_bloginfo( 'name' ) ) . '</a>';

  if ( ! empty( $cats ) ) {
    $term = $cats[0];
    echo '<span class="bc-breadcrumbs-sep"><i class="fas fa-chevron-right"></i></span>';
    echo '<a href="' . esc_url( get_category_link( $term ) ) . '">' . esc_html( $term->name ) . '</a>';
  }

  echo '<span class="bc-breadcrumbs-sep"><i class="fas fa-chevron-right"></i></span>';
  echo '<span class="bc-breadcrumbs-current">' . esc_html( get_the_title( $post ) ) . '</span>';
  echo '</nav>';
  echo '</div>';
}
add_action( 'generate_before_content', 'bc_render_breadcrumbs', 5 );
