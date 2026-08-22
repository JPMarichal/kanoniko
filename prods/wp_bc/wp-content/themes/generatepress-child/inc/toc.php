<?php

function bc_wrap_tables( $content ) {
  if ( ! is_singular() || ! in_the_loop() || ! is_main_query() ) {
    return $content;
  }

  return preg_replace_callback(
    '/<table[^>]*>.*?<\/table>/is',
    function ( $matches ) {
      return '<div class="bc-table-wrap">' . $matches[0] . '</div>';
    },
    $content
  );
}
add_filter( 'the_content', 'bc_wrap_tables', 5 );

function bc_inject_table_of_contents( $content ) {
  if ( ! is_singular() || ! in_the_loop() || ! is_main_query() ) {
    return $content;
  }

  $post_type = get_post_type();
  if ( ! in_array( $post_type, [ 'post', 'page' ], true ) ) {
    return $content;
  }

  $toc_items = [];
  $used_ids  = [];

  $content = preg_replace_callback(
    '/<h2([^>]*)>(.*?)<\/h2>/i',
    function ( $matches ) use ( &$toc_items, &$used_ids ) {
      $attrs = $matches[1];
      $title = strip_tags( $matches[2] );
      $id    = sanitize_title( $title );

      $unique_id = $id;
      $counter   = 1;
      while ( in_array( $unique_id, $used_ids, true ) ) {
        $unique_id = $id . '-' . $counter;
        $counter++;
      }
      $used_ids[] = $unique_id;

      $toc_items[] = [
        'title' => $title,
        'id'    => $unique_id,
      ];

      return "<h2 id=\"{$unique_id}\"{$attrs}>{$matches[2]}</h2>";
    },
    $content
  );

  if ( count( $toc_items ) < 2 ) {
    return $content;
  }

  $toc = '<div class="bc-toc">';
  $toc .= '<h3 class="bc-toc-title">En este artículo</h3>';
  $toc .= '<nav class="bc-toc-nav"><ul>';

  foreach ( $toc_items as $item ) {
    $toc .= '<li><a href="#' . esc_attr( $item['id'] ) . '">' . esc_html( $item['title'] ) . '</a></li>';
  }

  $toc .= '</ul></nav></div>';

  $pos = strpos( $content, '<h2' );
  if ( false !== $pos ) {
    $content = substr_replace( $content, $toc, $pos, 0 );
  }

  return $content;
}
add_filter( 'the_content', 'bc_inject_table_of_contents', 20 );
