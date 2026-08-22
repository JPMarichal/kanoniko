<?php

function bc_og_tags() {
  if ( ! is_singular() ) {
    return;
  }

  $post      = get_queried_object();
  $title     = esc_attr( is_singular( 'bc_quote_author' ) ? bc_persona_biography_title( $post->ID ) : get_the_title( $post ) );
  $url       = esc_url( get_permalink( $post ) );
  $site_name = esc_attr( get_bloginfo( 'name' ) );

  $excerpt = get_the_excerpt( $post );
  if ( empty( $excerpt ) ) {
    $excerpt = wp_trim_words( strip_shortcodes( get_the_content( $post ) ), 30, '…' );
  }
  $description = esc_attr( $excerpt );

  $image      = '';
  $image_w    = '';
  $image_h    = '';
  $image_alt  = '';
  if ( has_post_thumbnail( $post ) ) {
    $image    = esc_url( get_the_post_thumbnail_url( $post, 'bc-hero' ) );
    $image_id = get_post_thumbnail_id( $post );
    $src      = wp_get_attachment_image_src( $image_id, 'bc-hero' );
    if ( $src ) {
      $image_w = $src[1];
      $image_h = $src[2];
    }
    $alt_text = get_post_meta( $image_id, '_wp_attachment_image_alt', true );
    if ( $alt_text ) {
      $image_alt = esc_attr( $alt_text );
    }
  }

  if ( empty( $image ) ) {
    $logo_id = get_theme_mod( 'custom_logo' );
    if ( $logo_id ) {
      $image    = esc_url( wp_get_attachment_image_url( $logo_id, 'full' ) );
      $src      = wp_get_attachment_image_src( $logo_id, 'full' );
      if ( $src ) {
        $image_w = $src[1];
        $image_h = $src[2];
      }
      $image_alt = esc_attr( get_bloginfo( 'name' ) );
    } else {
      $icon_url = get_site_icon_url();
      if ( $icon_url ) {
        $image = esc_url( $icon_url );
        $image_alt = esc_attr( get_bloginfo( 'name' ) );
      }
    }
  }

  $twitter_site    = esc_attr( apply_filters( 'bc_twitter_site', '' ) );
  $author_twitter  = get_the_author_meta( 'twitter', $post->post_author );
  $twitter_creator = esc_attr( apply_filters( 'bc_twitter_creator', $author_twitter ) );
  ?>
<meta name="description" content="<?php echo $description; ?>">
<meta property="og:title" content="<?php echo $title; ?>">
<meta property="og:description" content="<?php echo $description; ?>">
<meta property="og:url" content="<?php echo $url; ?>">
<meta property="og:type" content="article">
<meta property="og:site_name" content="<?php echo $site_name; ?>">
<meta property="og:locale" content="<?php echo esc_attr( get_locale() ); ?>">
<meta property="article:published_time" content="<?php echo esc_attr( get_the_date( 'c', $post ) ); ?>">
<meta property="article:modified_time" content="<?php echo esc_attr( get_the_modified_date( 'c', $post ) ); ?>">
<?php if ( $image ) : ?>
<meta property="og:image" content="<?php echo $image; ?>">
<meta property="og:image:width" content="<?php echo $image_w; ?>">
<meta property="og:image:height" content="<?php echo $image_h; ?>">
<?php if ( $image_alt ) : ?>
<meta property="og:image:alt" content="<?php echo $image_alt; ?>">
<?php endif; ?>
<meta name="thumbnail" content="<?php echo $image; ?>">
<?php endif; ?>
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="<?php echo $title; ?>">
<meta name="twitter:description" content="<?php echo $description; ?>">
<?php if ( $twitter_site ) : ?>
<meta name="twitter:site" content="<?php echo $twitter_site; ?>">
<?php endif; ?>
<?php if ( $twitter_creator ) : ?>
<meta name="twitter:creator" content="<?php echo $twitter_creator; ?>">
<?php endif; ?>
<?php if ( $image ) : ?>
<meta name="twitter:image" content="<?php echo $image; ?>">
<?php endif; ?>
  <?php
}
add_action( 'wp_head', 'bc_og_tags' );

function bc_user_twitter_field( $user ) {
  $value = esc_attr( get_user_meta( $user->ID, 'twitter', true ) );
  ?>
  <h3><?php _e( 'Redes Sociales' ); ?></h3>
  <table class="form-table">
    <tr>
      <th><label for="twitter"><?php _e( 'Twitter / X Username' ); ?></label></th>
      <td>
        <input type="text" name="twitter" id="twitter" value="<?php echo $value; ?>" class="regular-text" placeholder="@usuario">
        <p class="description"><?php _e( 'Sin incluir la URL, solo el @username.' ); ?></p>
      </td>
    </tr>
  </table>
  <?php
}
add_action( 'show_user_profile', 'bc_user_twitter_field' );
add_action( 'edit_user_profile', 'bc_user_twitter_field' );

function bc_save_user_twitter_field( $user_id ) {
  if ( ! current_user_can( 'edit_user', $user_id ) ) {
    return;
  }
  update_user_meta( $user_id, 'twitter', sanitize_text_field( $_POST['twitter'] ?? '' ) );
}
add_action( 'personal_options_update', 'bc_save_user_twitter_field' );
add_action( 'edit_user_profile_update', 'bc_save_user_twitter_field' );
