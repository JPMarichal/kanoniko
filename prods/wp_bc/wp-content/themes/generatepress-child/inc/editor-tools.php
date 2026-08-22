<?php

add_action('enqueue_block_editor_assets', function () {
  $screen = get_current_screen();
  if (!$screen || 'post' !== $screen->base) {
    return;
  }
  wp_enqueue_script(
    'bc-editor',
    get_stylesheet_directory_uri() . '/assets/editor.js',
    [],
    '1.0',
    true
  );
});

add_action('admin_bar_menu', function ($wp_admin_bar) {
  if (!is_admin()) {
    return;
  }
  $screen = get_current_screen();
  if (!$screen || 'post' !== $screen->base) {
    return;
  }
  $wp_admin_bar->add_node([
    'id'    => 'bc-new-post',
    'title' => '<span class="ab-icon dashicons dashicons-plus-alt2"></span><span class="ab-label">Nuevo Artículo</span>',
    'href'  => admin_url('post-new.php'),
    'meta'  => ['target' => '_blank'],
  ]);
}, 80);
