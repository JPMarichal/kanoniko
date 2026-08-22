<?php
/**
 * Plugin Name: BC Carbon Fields
 * Description: Carbon Fields integration for BC Quote Block CPTs
 * Version: 1.0.0
 * Requires at least: 5.0
 * Requires PHP: 7.4
 * License: GPL-2.0-or-later
 */

defined( 'ABSPATH' ) || exit;

define( 'BC_CF_DIR', plugin_dir_path( __FILE__ ) );
define( 'BC_CF_URL', plugin_dir_url( __FILE__ ) );

// Load Carbon Fields
require_once BC_CF_DIR . 'vendor/autoload.php';

use Carbon_Fields\Carbon_Fields;

add_action( 'after_setup_theme', function () {
    Carbon_Fields::boot();
} );

// Register fields after Carbon Fields has booted
add_action( 'carbon_fields_register_fields', function () {
    require_once BC_CF_DIR . 'inc/cpt-bc-quote-author.php';
} );