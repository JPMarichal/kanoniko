<?php
/**
 * Plugin Name:       Hura AI Content Generator
 * Description:       Automatically generate SEO-optimized articles using optimized Prompt structure via OpenRouter API.
 * Version:           1.0.0
 * Author:            Hura Apps
 * Author URI:        https://www.huraapps.com
 * License:           GPL v2 or later
 * License URI:       https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain:       hura-ai-content-generator
 *
 * @package           Hura_AI_Content_Generator
 */

// Prevent direct access.
defined( 'ABSPATH' ) || exit;

// Define plugin constants.
define( 'HURA_AI_VERSION', '1.0.0' );
define( 'HURA_AI_PLUGIN_DIR', plugin_dir_path( __FILE__ ) );
define( 'HURA_AI_PLUGIN_URL', plugin_dir_url( __FILE__ ) );
define( 'HURA_AI_PLUGIN_BASENAME', plugin_basename( __FILE__ ) );

/**
 * Load required dependencies.
 */
require_once HURA_AI_PLUGIN_DIR . 'includes/class-hura-ai-api.php';
require_once HURA_AI_PLUGIN_DIR . 'admin/class-hura-ai-admin.php';

/**
 * Run the plugin.
 *
 * This function is called after all dependency files have been included.
 * It initializes the Admin and i18n components.
 *
 * @since 1.0.0
 * @return void
 */
function hura_ai_run() {
	// Initialize Admin object (only in wp-admin area).
	if ( is_admin() ) {
		$plugin_admin = new Hura_AI_Admin();
		$plugin_admin->init();
	}
}
add_action( 'plugins_loaded', 'hura_ai_run' );
