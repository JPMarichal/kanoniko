<?php

function bc_compiled_css_handle() {
  return 'generatepress-child';
}

function bc_enqueue_compiled_styles() {
  $compiled_uri  = get_stylesheet_directory_uri() . '/style-compiled.css';
  $compiled_path = get_stylesheet_directory() . '/style-compiled.css';
  $version = file_exists($compiled_path) ? md5_file($compiled_path) : '1.0';

  wp_enqueue_style(
    bc_compiled_css_handle(),
    $compiled_uri,
    ['generate-style'],
    $version
  );

  wp_enqueue_style(
    'bc-fonts',
    get_stylesheet_directory_uri() . '/fonts/bc-fonts.css',
    [],
    '1.0'
  );
}
add_action('wp_enqueue_scripts', 'bc_enqueue_compiled_styles', 20);

add_filter('style_loader_tag', function ($html, $handle) {
  if (bc_compiled_css_handle() === $handle) {
    $html = str_replace(
      "media='all'",
      "media='print' onload=\"this.media='all'\"",
      $html
    );
  }
  return $html;
}, 10, 2);

function bc_enqueue_global_assets() {
  wp_enqueue_style(
    'fontawesome',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css',
    [],
    '6.7.2'
  );

  wp_enqueue_style(
    'bootstrap',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
    [],
    '5.3.3'
  );

  wp_enqueue_script(
    'bootstrap-bundle',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js',
    [],
    '5.3.3',
    true
  );
}
add_action('wp_enqueue_scripts', 'bc_enqueue_global_assets');

add_filter('style_loader_tag', function ($html, $handle) {
  if (in_array($handle, ['fontawesome', 'bootstrap'], true)) {
    $html = str_replace(
      "media='all'",
      "media='print' onload=\"this.media='all'\"",
      $html
    );
  }
  return $html;
}, 11, 2);

function bc_inline_critical_css_bg() {
  if ( ! is_front_page() ) {
    return '';
  }
  $featured = new WP_Query( [
    'posts_per_page'      => 1,
    'ignore_sticky_posts' => true,
  ] );
  if ( ! $featured->have_posts() ) {
    return '';
  }
  $featured->the_post();
  $url = has_post_thumbnail() ? get_the_post_thumbnail_url( null, 'bc-hero' ) : '';
  wp_reset_postdata();
  return $url ? '.bc-fp-featured-image-wrap{background:#1a1a2e;min-height:300px}.bc-fp-featured-image{background-image:url(' . esc_url( $url ) . ')}' : '';
}

function bc_inline_critical_css() {
  $css = '';

  if ( is_singular() || is_category() || is_tag() ) {
    $css .= '
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Oxygen-Sans,Ubuntu,Cantarell,"Helvetica Neue",sans-serif}
.grid-container{max-width:100%;padding-left:20px;padding-right:20px}
@media(min-width:768px){.grid-container{padding-left:30px;padding-right:30px}}
@media(min-width:1024px){.grid-container{padding-left:40px;padding-right:40px}}';
  }

  if ( is_front_page() ) {
    $css .= '
.bc-front-page{max-width:100%;padding:30px 20px 50px}
.bc-fp-ticker-wrap{display:flex;align-items:center;background:#fff;border-bottom:2px solid #e8e4db;overflow:hidden;height:40px}
.bc-fp-ticker-label{flex-shrink:0;background:#c00;color:#fff;font-size:.72em;font-weight:800;text-transform:uppercase;letter-spacing:.5px;padding:0 14px;height:100%;display:flex;align-items:center;gap:6px}
.bc-fp-ticker-track-wrap{flex:1;overflow:hidden;padding:0 16px}
.bc-fp-featured{border-radius:8px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.08);margin-bottom:40px}
.bc-fp-featured-image-wrap{position:relative;overflow:hidden;max-height:480px}
.bc-fp-featured-image{width:100%;height:450px;object-fit:cover;display:block}
.bc-fp-featured-overlay{position:absolute;inset:0;background:linear-gradient(to top,rgba(0,0,0,.8) 0,rgba(0,0,0,.1) 60%,transparent 100%)}
.bc-fp-featured-body{position:absolute;bottom:0;left:0;right:0;padding:30px;z-index:1}
.bc-fp-featured-title{font-family:Merriweather,Georgia,"Times New Roman",serif;font-size:2em;font-weight:900;color:#fff;margin:12px 0 8px;line-height:1.2;text-shadow:0 1px 4px rgba(0,0,0,.3)}
.bc-fp-cat-label{display:inline-block;padding:4px 12px;font-size:.75em;font-weight:700;color:#fff;text-transform:uppercase;letter-spacing:.5px;border-radius:3px}
.bc-fp-featured-excerpt{color:rgba(255,255,255,.85);font-size:1em;line-height:1.5;margin:0 0 10px;max-width:700px}
.bc-fp-featured-meta{color:rgba(255,255,255,.7);font-size:.85em}';

    $bg = bc_inline_critical_css_bg();
    if ( $bg ) {
      $css .= $bg;
    }
  }

  if ( ! $css ) {
    return;
  }
  ?>
<style id="bc-critical-css"><?php echo $css; ?></style>
  <?php
}
add_action('wp_head', 'bc_inline_critical_css', 0);
