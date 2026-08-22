<?php
/**
 * Plugin Name: BC Content Organization
 * Description: Organiza posts en series y colecciones con ordenamiento drag-and-drop. Taxonomía jerárquica única: colecciones (padres) contienen series (hijos).
 * Version: 1.0.0
 */

defined('ABSPATH') || exit;

define('BCCO_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('BCCO_PLUGIN_URL', plugin_dir_url(__FILE__));

if (!function_exists('bcco_get_post_types')) {
    function bcco_get_post_types() {
        $types = get_post_types(['public' => true], 'names');
        $types = array_diff($types, ['attachment']);
        return array_values(apply_filters('bcco_post_types', $types));
    }
}

add_action('wp_enqueue_scripts', function () {
    if (is_singular(bcco_get_post_types())) {
        wp_enqueue_style('bcco-widget', BCCO_PLUGIN_URL . 'assets/css/widget.css', [], '1.0.0');
    }
});

require_once BCCO_PLUGIN_DIR . 'includes/class-taxonomies.php';
require_once BCCO_PLUGIN_DIR . 'includes/class-post-meta.php';
require_once BCCO_PLUGIN_DIR . 'includes/class-admin-page.php';
require_once BCCO_PLUGIN_DIR . 'includes/class-ajax-handlers.php';
require_once BCCO_PLUGIN_DIR . 'includes/class-frontend-widget.php';
