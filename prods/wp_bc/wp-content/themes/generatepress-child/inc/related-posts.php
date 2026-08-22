<?php

function bc_related_posts() {
  if ( ! is_singular( 'post' ) || ! in_the_loop() || ! is_main_query() ) {
    return;
  }

  $post_id = get_the_ID();
  $cats    = wp_get_post_categories( $post_id );

  if ( empty( $cats ) ) {
    return;
  }

  $related = new WP_Query( [
    'category__in'   => $cats,
    'post__not_in'   => [ $post_id ],
    'posts_per_page' => 4,
    'ignore_sticky_posts' => true,
    'no_found_rows'  => true,
  ] );

  if ( ! $related->have_posts() ) {
    return;
  }

  echo '<div class="bc-related-posts">';
  echo '<h3 class="bc-related-posts-title">' . __( 'Artículos relacionados' ) . '</h3>';
  echo '<div class="bc-related-posts-grid">';

  while ( $related->have_posts() ) {
    $related->the_post();
    ?>
    <article class="bc-related-post">
      <a href="<?php the_permalink(); ?>" class="bc-related-post-link">
        <?php if ( has_post_thumbnail() ) : ?>
          <div class="bc-related-post-thumb">
            <?php the_post_thumbnail( 'bc-hero' ); ?>
          </div>
        <?php endif; ?>
        <h4 class="bc-related-post-title"><?php the_title(); ?></h4>
      </a>
    </article>
    <?php
  }

  echo '</div></div>';
  wp_reset_postdata();
}
add_action( 'generate_after_content', 'bc_related_posts' );
