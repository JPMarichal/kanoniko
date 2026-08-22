<?php
/**
 * Template for the plugin Settings page.
 *
 * Displays the configuration form for API Key, Model and other options
 * using the WordPress Settings API.
 *
 * @package Hura_AI_Content_Generator
 * @since   1.0.0
 */

// Prevent direct access.
defined( 'ABSPATH' ) || exit;
?>

<div class="wrap">
	<h1><?php echo esc_html( get_admin_page_title() ); ?></h1>

	<?php settings_errors(); ?>

	<form action="options.php" method="post">
		<?php
		// Output security fields for the settings group.
		settings_fields( 'hura_ai_settings_group' );

		// Output setting sections and fields.
		do_settings_sections( 'hura-ai-settings' );

		// Standard WordPress submit button.
		submit_button( __( 'Save Settings', 'hura-ai-content-generator' ) );
		?>
	</form>
	<?php include HURA_AI_PLUGIN_DIR . 'admin/partials/footer-copyright.php'; ?>
</div>
