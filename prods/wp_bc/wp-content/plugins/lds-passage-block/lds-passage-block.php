<?php
/**
 * Plugin Name: LDS Passage Block
 * Description: Inserta pasajes de las Escrituras SUD (Biblia RV 1960, Libro de Mormón, Doctrina y Convenios, Perla de Gran Precio)
 * Version: 0.1.0
 * Requires at least: 6.1
 * Requires PHP: 7.4
 * License: GPL-2.0-or-later
 * Text Domain: lds-passage-block
 */

defined( 'ABSPATH' ) || exit;

define( 'LDS_PASSAGE_BLOCK_VERSION', '0.1.0' );
define( 'LDS_PASSAGE_BLOCK_DIR', plugin_dir_path( __FILE__ ) );
define( 'LDS_PASSAGE_BLOCK_URL', plugin_dir_url( __FILE__ ) );

require_once LDS_PASSAGE_BLOCK_DIR . 'includes/class-data-loader.php';
require_once LDS_PASSAGE_BLOCK_DIR . 'includes/class-rest-controller.php';
require_once LDS_PASSAGE_BLOCK_DIR . 'includes/class-block-renderer.php';

function lds_passage_block_init() {
    $renderer = new LDS_Passage_Block_Renderer();

    register_block_type( LDS_PASSAGE_BLOCK_DIR . 'block.json', array(
        'render_callback' => array( $renderer, 'render' ),
    ) );
}
add_action( 'init', 'lds_passage_block_init' );

function lds_passage_block_rest_init() {
    $controller = new LDS_Passage_REST_Controller();
    $controller->register_routes();
}
add_action( 'rest_api_init', 'lds_passage_block_rest_init' );
