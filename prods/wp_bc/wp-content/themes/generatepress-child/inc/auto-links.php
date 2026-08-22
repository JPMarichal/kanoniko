<?php

function bc_auto_link_glossary( $content ) {
  if ( ! in_the_loop() || ! is_main_query() ) {
    return $content;
  }

  $auto_link_types = apply_filters( 'bc_auto_link_post_types', [ 'post', 'bc_quote_author', 'glossary' ] );
  if ( ! is_singular( $auto_link_types ) ) {
    return $content;
  }

  static $terms = null;

  if ( $terms === null ) {
    $posts = get_posts( [
      'post_type'      => 'bc_quote_author',
      'posts_per_page' => -1,
      'post_status'    => 'publish',
      'orderby'        => 'title',
      'order'          => 'ASC',
    ] );

    $terms = [];
    foreach ( $posts as $p ) {
      $name = trim( $p->post_title );
      if ( $name !== '' ) {
        $terms[ $name ] = get_permalink( $p );
      }
    }

    uksort( $terms, function ( $a, $b ) {
      return strlen( $b ) - strlen( $a );
    } );
  }

  if ( empty( $terms ) ) {
    return $content;
  }

  $current_url = get_permalink( get_queried_object_id() );

  foreach ( $terms as $name => $url ) {
    if ( $url === $current_url ) {
      continue;
    }

    $content = preg_replace_callback(
      '/\b(' . preg_quote( $name, '/' ) . ')\b(?!\s+(?:padre|hijo|sr\.?|jr\.?))/iu',
      function ( $matches ) use ( $url, &$content ) {
        $pos    = mb_strpos( $content, $matches[0] );
        $before = mb_substr( $content, 0, $pos );
        $a_open  = mb_substr_count( $before, '<a ' );
        $a_close = mb_substr_count( $before, '</a>' );
        $bq_open  = mb_substr_count( $before, '<blockquote' );
        $bq_close = mb_substr_count( $before, '</blockquote>' );

        if ( $a_open > $a_close || $bq_open > $bq_close ) {
          return $matches[0];
        }

        return '<a href="' . esc_url( $url ) . '" class="bc-glossary-link">' . $matches[0] . '</a>';
      },
      $content,
      1
    );
  }

  return $content;
}
add_filter( 'the_content', 'bc_auto_link_glossary', 15 );
