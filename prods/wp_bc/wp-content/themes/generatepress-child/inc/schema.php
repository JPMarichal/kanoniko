<?php

function bc_json_ld_article() {
  if ( ! is_singular() ) {
    return;
  }

  $post    = get_queried_object();
  $excerpt = get_the_excerpt( $post );
  if ( empty( $excerpt ) ) {
    $excerpt = wp_trim_words( strip_shortcodes( get_the_content( $post ) ), 30, '…' );
  }

  $schema = [
    '@context'         => 'https://schema.org',
    '@type'            => 'Article',
    'headline'         => get_the_title( $post ),
    'description'      => $excerpt,
    'datePublished'    => get_the_date( 'c', $post ),
    'dateModified'     => get_the_modified_date( 'c', $post ),
    'author'           => [
      '@type' => 'Person',
      'name'  => get_the_author_meta( 'display_name', $post->post_author ),
      'url'   => get_author_posts_url( $post->post_author ),
    ],
    'url'              => get_permalink( $post ),
    'mainEntityOfPage' => [
      '@type' => 'WebPage',
      '@id'   => get_permalink( $post ),
    ],
  ];

  $logo_id  = get_theme_mod( 'custom_logo' );
  $logo_url = $logo_id ? wp_get_attachment_image_url( $logo_id, 'full' ) : '';
  $schema['publisher'] = [
    '@type' => 'Organization',
    'name'  => get_bloginfo( 'name' ),
  ];

  if ( $logo_id ) {
    $logo_src = wp_get_attachment_image_src( $logo_id, 'full' );
    $schema['publisher']['logo'] = [
      '@type' => 'ImageObject',
      'url'   => $logo_url,
      'width' => $logo_src[1],
      'height'=> $logo_src[2],
    ];
  } elseif ( get_site_icon_url() ) {
    $schema['publisher']['logo'] = [
      '@type' => 'ImageObject',
      'url'   => get_site_icon_url(),
    ];
  }

  $same_as = bc_social_profiles();
  if ( ! empty( $same_as ) ) {
    $schema['publisher']['sameAs'] = $same_as;
  }

  if ( has_post_thumbnail( $post ) ) {
    $image_id  = get_post_thumbnail_id( $post );
    $schema['image'] = [
      '@type' => 'ImageObject',
      'url'   => get_the_post_thumbnail_url( $post, 'full' ),
      'width' => wp_get_attachment_image_src( $image_id, 'full' )[1],
      'height'=> wp_get_attachment_image_src( $image_id, 'full' )[2],
    ];
  } elseif ( get_theme_mod( 'custom_logo' ) ) {
    $logo_id = get_theme_mod( 'custom_logo' );
    $schema['image'] = [
      '@type' => 'ImageObject',
      'url'   => wp_get_attachment_image_url( $logo_id, 'full' ),
      'width' => wp_get_attachment_image_src( $logo_id, 'full' )[1],
      'height'=> wp_get_attachment_image_src( $logo_id, 'full' )[2],
    ];
  } elseif ( get_site_icon_url() ) {
    $schema['image'] = [
      '@type' => 'ImageObject',
      'url'   => get_site_icon_url(),
    ];
  }

  echo '<script type="application/ld+json">' . "\n";
  echo wp_json_encode( $schema, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT ) . "\n";
  echo '</script>' . "\n";
}
add_action( 'wp_head', 'bc_json_ld_article' );

function bc_json_ld_search_box() {
  ?>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "<?php echo esc_attr( get_bloginfo( 'name' ) ); ?>",
  "url": "<?php echo esc_url( home_url() ); ?>",
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "<?php echo esc_url( home_url( '/?s={search_term_string}' ) ); ?>"
    },
    "query-input": "required name=search_term_string"
  }
}
</script>
  <?php
}
add_action( 'wp_head', 'bc_json_ld_search_box' );

function bc_json_ld_webpage() {
  if ( is_singular() ) {
    return;
  }
  if ( ! is_archive() && ! is_home() && ! is_search() ) {
    return;
  }

  $schema = [
    '@context'  => 'https://schema.org',
    '@type'     => 'WebPage',
    'name'      => wp_get_document_title(),
    'url'       => home_url( add_query_arg( [] ) ),
    'isPartOf'  => [
      '@type' => 'WebSite',
      'name'  => get_bloginfo( 'name' ),
      'url'   => home_url(),
    ],
  ];

  echo '<script type="application/ld+json">' . "\n";
  echo wp_json_encode( $schema, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT ) . "\n";
  echo '</script>' . "\n";
}
add_action( 'wp_head', 'bc_json_ld_webpage' );

function bc_json_ld_profile() {
  if ( ! is_singular( 'bc_quote_author' ) ) {
    return;
  }

  $post = get_queried_object();
  $desc = get_post_meta( $post->ID, '_author_description', true );

  $schema = [
    '@context'  => 'https://schema.org',
    '@type'     => 'ProfilePage',
    'name'      => bc_persona_biography_title( $post->ID ),
    'url'       => get_permalink( $post ),
    'mainEntity' => [
      '@type' => 'Person',
      'name'  => get_the_title( $post ),
    ],
  ];

  if ( $desc ) {
    $schema['mainEntity']['description'] = $desc;
  }

  if ( has_post_thumbnail( $post ) ) {
    $image_id = get_post_thumbnail_id( $post );
    $schema['mainEntity']['image'] = [
      '@type' => 'ImageObject',
      'url'   => get_the_post_thumbnail_url( $post, 'full' ),
      'width' => wp_get_attachment_image_src( $image_id, 'full' )[1],
      'height'=> wp_get_attachment_image_src( $image_id, 'full' )[2],
    ];
  }

  echo '<script type="application/ld+json">' . "\n";
  echo wp_json_encode( $schema, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT ) . "\n";
  echo '</script>' . "\n";
}
add_action( 'wp_head', 'bc_json_ld_profile' );

function bc_json_ld_breadcrumbs() {
  if ( ! is_singular() && ! is_archive() && ! is_home() && ! is_search() ) {
    return;
  }

  $items   = [];
  $items[] = [
    '@type' => 'ListItem',
    'position' => 1,
    'name'  => get_bloginfo( 'name' ),
    'item'  => home_url(),
  ];

  if ( is_singular() ) {
    $post     = get_queried_object();
    $taxonomy = 'category';
    $terms    = get_the_terms( $post, $taxonomy );

    if ( ! empty( $terms ) && ! is_wp_error( $terms ) ) {
      $term = $terms[0];
      $items[] = [
        '@type' => 'ListItem',
        'position' => 2,
        'name'  => $term->name,
        'item'  => get_term_link( $term ),
      ];
    }

    $items[] = [
      '@type' => 'ListItem',
      'position' => count( $items ) + 1,
      'name'  => get_the_title( $post ),
    ];
  } elseif ( is_category() ) {
    $items[] = [
      '@type' => 'ListItem',
      'position' => 2,
      'name'  => single_cat_title( '', false ),
    ];
  } elseif ( is_tag() ) {
    $items[] = [
      '@type' => 'ListItem',
      'position' => 2,
      'name'  => single_tag_title( '', false ),
    ];
  } elseif ( is_search() ) {
    $items[] = [
      '@type' => 'ListItem',
      'position' => 2,
      'name'  => sprintf( __( 'Search: %s' ), get_search_query( false ) ),
    ];
  } elseif ( is_home() ) {
    $items[] = [
      '@type' => 'ListItem',
      'position' => 2,
      'name'  => __( 'Blog' ),
    ];
  }

  $schema = [
    '@context'        => 'https://schema.org',
    '@type'           => 'BreadcrumbList',
    'itemListElement' => $items,
  ];

  echo '<script type="application/ld+json">' . "\n";
  echo wp_json_encode( $schema, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT ) . "\n";
  echo '</script>' . "\n";
}
add_action( 'wp_head', 'bc_json_ld_breadcrumbs' );

function bc_social_profiles() {
  return apply_filters( 'bc_social_profiles', [] );
}
