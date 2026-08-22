<?php
/**
 * Admin management class for Hura AI Content Generator plugin.
 *
 * Responsible for creating menus, registering settings, enqueuing scripts/styles,
 * and handling AJAX actions from the client.
 *
 * @package Hura_AI_Content_Generator
 * @since   1.0.0
 */

// Prevent direct access.
defined( 'ABSPATH' ) || exit;

/**
 * Class Hura_AI_Admin.
 *
 * @since 1.0.0
 */
class Hura_AI_Admin {

	/**
	 * Initialize Admin hooks.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function init() {
		add_action( 'admin_menu', array( $this, 'hura_ai_add_admin_menu' ) );
		add_action( 'admin_init', array( $this, 'hura_ai_register_settings' ) );
		add_action( 'admin_enqueue_scripts', array( $this, 'hura_ai_enqueue_scripts' ) );

		// Handle AJAX for Generate Content.
		add_action( 'wp_ajax_hura_ai_generate_content', array( $this, 'hura_ai_handle_generate_content' ) );

		// Handle AJAX for Save as Draft.
		add_action( 'wp_ajax_hura_ai_save_as_draft', array( $this, 'hura_ai_handle_save_as_draft' ) );
	}

	/**
	 * Add main menu and submenus to WordPress Admin.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function hura_ai_add_admin_menu() {
		// Main menu.
		add_menu_page(
			__( 'AI Content Generator', 'hura-ai-content-generator' ), // Page title.
			__( 'AI Content Generator', 'hura-ai-content-generator' ), // Menu title.
			'edit_posts',                                                // Capability.
			'hura-ai-content-generator',                                 // Menu slug.
			array( $this, 'hura_ai_display_generate_page' ),             // Callback.
			'dashicons-superhero',                                       // Icon.
			99                                                           // Position.
		);

		// Submenu: Generate (default page).
		add_submenu_page(
			'hura-ai-content-generator',
			__( 'Generate Content', 'hura-ai-content-generator' ),
			__( 'Generate', 'hura-ai-content-generator' ),
			'edit_posts',
			'hura-ai-content-generator',
			array( $this, 'hura_ai_display_generate_page' )
		);

		// Submenu: Settings.
		add_submenu_page(
			'hura-ai-content-generator',
			__( 'AI Content Generator Settings', 'hura-ai-content-generator' ),
			__( 'Settings', 'hura-ai-content-generator' ),
			'manage_options',
			'hura-ai-settings',
			array( $this, 'hura_ai_display_settings_page' )
		);
	}

	/**
	 * Register plugin settings using WordPress Settings API.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function hura_ai_register_settings() {
		// Register settings group.
		register_setting( 'hura_ai_settings_group', 'hura_ai_default_lang', array( 'sanitize_callback' => 'sanitize_text_field' ) );
		register_setting( 'hura_ai_settings_group', 'hura_ai_openrouter_key', array( 'sanitize_callback' => 'sanitize_text_field' ) );
		register_setting( 'hura_ai_settings_group', 'hura_ai_openrouter_model', array( 'sanitize_callback' => 'sanitize_text_field' ) );

		// Add section.
		add_settings_section(
			'hura_ai_main_section',
			__( 'OpenRouter API Configuration', 'hura-ai-content-generator' ),
			array( $this, 'hura_ai_settings_section_callback' ),
			'hura-ai-settings'
		);

		// Add fields.
		add_settings_field(
			'hura_ai_default_lang',
			__( 'Default Language', 'hura-ai-content-generator' ),
			array( $this, 'hura_ai_render_field_default_lang' ),
			'hura-ai-settings',
			'hura_ai_main_section'
		);

		add_settings_field(
			'hura_ai_openrouter_key',
			__( 'OpenRouter API Key', 'hura-ai-content-generator' ),
			array( $this, 'hura_ai_render_field_api_key' ),
			'hura-ai-settings',
			'hura_ai_main_section'
		);

		add_settings_field(
			'hura_ai_openrouter_model',
			__( 'AI Model', 'hura-ai-content-generator' ),
			array( $this, 'hura_ai_render_field_model' ),
			'hura-ai-settings',
			'hura_ai_main_section'
		);
	}

	/**
	 * Callback for settings section.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function hura_ai_settings_section_callback() {
		echo '<p>' . esc_html__( 'Configure your API Key and Model to use the automatic content generation feature.', 'hura-ai-content-generator' ) . '</p>';
	}

	/**
	 * Render field: Default Language.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function hura_ai_render_field_default_lang() {
		$value = get_option( 'hura_ai_default_lang', 'English' );
		?>
		<select name="hura_ai_default_lang" id="hura_ai_default_lang" style="min-width: 250px;">
			<option value="English" <?php selected( $value, 'English' ); ?>><?php esc_html_e( 'English', 'hura-ai-content-generator' ); ?></option>
			<option value="Arabic" <?php selected( $value, 'Arabic' ); ?>><?php esc_html_e( 'Arabic', 'hura-ai-content-generator' ); ?></option>
			<option value="Chinese" <?php selected( $value, 'Chinese' ); ?>><?php esc_html_e( 'Chinese', 'hura-ai-content-generator' ); ?></option>
			<option value="Danish" <?php selected( $value, 'Danish' ); ?>><?php esc_html_e( 'Danish', 'hura-ai-content-generator' ); ?></option>
			<option value="Dutch" <?php selected( $value, 'Dutch' ); ?>><?php esc_html_e( 'Dutch', 'hura-ai-content-generator' ); ?></option>
			<option value="French" <?php selected( $value, 'French' ); ?>><?php esc_html_e( 'French', 'hura-ai-content-generator' ); ?></option>
			<option value="German" <?php selected( $value, 'German' ); ?>><?php esc_html_e( 'German', 'hura-ai-content-generator' ); ?></option>
			<option value="Hindi" <?php selected( $value, 'Hindi' ); ?>><?php esc_html_e( 'Hindi', 'hura-ai-content-generator' ); ?></option>
			<option value="Indonesian" <?php selected( $value, 'Indonesian' ); ?>><?php esc_html_e( 'Indonesian', 'hura-ai-content-generator' ); ?></option>
			<option value="Italian" <?php selected( $value, 'Italian' ); ?>><?php esc_html_e( 'Italian', 'hura-ai-content-generator' ); ?></option>
			<option value="Japanese" <?php selected( $value, 'Japanese' ); ?>><?php esc_html_e( 'Japanese', 'hura-ai-content-generator' ); ?></option>
			<option value="Korean" <?php selected( $value, 'Korean' ); ?>><?php esc_html_e( 'Korean', 'hura-ai-content-generator' ); ?></option>
			<option value="Portuguese" <?php selected( $value, 'Portuguese' ); ?>><?php esc_html_e( 'Portuguese', 'hura-ai-content-generator' ); ?></option>
			<option value="Russian" <?php selected( $value, 'Russian' ); ?>><?php esc_html_e( 'Russian', 'hura-ai-content-generator' ); ?></option>
			<option value="Spanish" <?php selected( $value, 'Spanish' ); ?>><?php esc_html_e( 'Spanish', 'hura-ai-content-generator' ); ?></option>
			<option value="Swedish" <?php selected( $value, 'Swedish' ); ?>><?php esc_html_e( 'Swedish', 'hura-ai-content-generator' ); ?></option>
			<option value="Thai" <?php selected( $value, 'Thai' ); ?>><?php esc_html_e( 'Thai', 'hura-ai-content-generator' ); ?></option>
			<option value="Turkish" <?php selected( $value, 'Turkish' ); ?>><?php esc_html_e( 'Turkish', 'hura-ai-content-generator' ); ?></option>
			<option value="Vietnamese" <?php selected( $value, 'Vietnamese' ); ?>><?php esc_html_e( 'Vietnamese', 'hura-ai-content-generator' ); ?></option>
		</select>
		<?php
	}

	/**
	 * Render field: API Key.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function hura_ai_render_field_api_key() {
		$value = get_option( 'hura_ai_openrouter_key', '' );
		?>
		<input type="password" name="hura_ai_openrouter_key" id="hura_ai_openrouter_key"
			value="<?php echo esc_attr( $value ); ?>" class="regular-text" style="min-width: 350px;" />
		<p class="description">
			<?php esc_html_e( 'Enter your OpenRouter API Key. Sign up at https://openrouter.ai/keys', 'hura-ai-content-generator' ); ?>
		</p>
		<?php
	}

	/**
	 * Render field: AI Model.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function hura_ai_render_field_model() {
		$value = get_option( 'hura_ai_openrouter_model', 'openrouter/free' );
		?>
		<input type="text" name="hura_ai_openrouter_model" id="hura_ai_openrouter_model"
			value="<?php echo esc_attr( $value ); ?>" class="regular-text" style="min-width: 350px;" />
		<p class="description">
			<?php esc_html_e( 'Enter the AI Model name from OpenRouter. E.g., meta-llama/llama-3.3-70b-instruct:free, google/gemma-4-31b-it:free,...', 'hura-ai-content-generator' ); ?>
		</p>
		<?php
	}

	/**
	 * Enqueue scripts and styles for admin.
	 *
	 * @since 1.0.0
	 *
	 * @param string $hook Current admin page slug.
	 * @return void
	 */
	public function hura_ai_enqueue_scripts( $hook ) {
		// Only load on plugin pages.
		if ( false === strpos( $hook, 'hura-ai' ) ) {
			return;
		}

		// CSS.
		wp_enqueue_style(
			'hura-ai-admin',
			HURA_AI_PLUGIN_URL . 'admin/css/hura-ai-admin.css',
			array(),
			HURA_AI_VERSION,
			'all'
		);

		// JavaScript.
		wp_enqueue_script(
			'hura-ai-admin',
			HURA_AI_PLUGIN_URL . 'admin/js/hura-ai-admin.js',
			array( 'jquery' ),
			HURA_AI_VERSION,
			true
		);

		// Localize script to pass data from PHP to JS.
		wp_localize_script(
			'hura-ai-admin',
			'hura_ai_ajax',
			array(
				'ajax_url' => admin_url( 'admin-ajax.php' ),
				'nonce'    => wp_create_nonce( 'hura_ai_ajax_nonce' ),
			)
		);
	}

	/**
	 * Display the Generate page.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function hura_ai_display_generate_page() {
		include_once HURA_AI_PLUGIN_DIR . 'admin/partials/page-generate.php';
	}

	/**
	 * Display the Settings page.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function hura_ai_display_settings_page() {
		include_once HURA_AI_PLUGIN_DIR . 'admin/partials/page-settings.php';
	}

	/**
	 * Handle AJAX: Generate Content.
	 *
	 * Receives data from the Generate form, calls the OpenRouter API,
	 * and returns JSON result to the client.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function hura_ai_handle_generate_content() {
		// Verify security nonce.
		check_ajax_referer( 'hura_ai_ajax_nonce', 'nonce' );

		// Check user capabilities.
		if ( ! current_user_can( 'edit_posts' ) ) {
			wp_send_json_error( array( 'message' => __( 'You do not have permission to perform this action.', 'hura-ai-content-generator' ) ) );
		}

		// Get and sanitize data from $_POST.
		$prompt_data = array(
			'language'    => isset( $_POST['language'] ) ? sanitize_text_field( wp_unslash( $_POST['language'] ) ) : '',
			'tone'        => isset( $_POST['tone'] ) ? sanitize_text_field( wp_unslash( $_POST['tone'] ) ) : '',
			'keywords'    => isset( $_POST['keywords'] ) ? sanitize_textarea_field( wp_unslash( $_POST['keywords'] ) ) : '',
			'length'      => isset( $_POST['length'] ) ? sanitize_text_field( wp_unslash( $_POST['length'] ) ) : '',
			'description' => isset( $_POST['description'] ) ? sanitize_textarea_field( wp_unslash( $_POST['description'] ) ) : '',
			'category'    => isset( $_POST['category'] ) ? absint( $_POST['category'] ) : 0,
		);

		// Gọi API.
		$api = new Hura_AI_API();
		$result = $api->hura_ai_call_openrouter( $prompt_data );

		if ( true === $result['success'] ) {
			wp_send_json_success( array(
				'title'   => $result['data']['title'],
				'content' => $result['data']['content'],
			) );
		} else {
			wp_send_json_error( array(
				'message' => $result['data'],
			) );
		}
	}

	/**
	 * Handle AJAX: Save as Draft.
	 *
	 * Gets title, content from wp_editor and category,
	 * creates a new post with post_status = 'draft'.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function hura_ai_handle_save_as_draft() {
		// Verify security nonce.
		check_ajax_referer( 'hura_ai_ajax_nonce', 'nonce' );

		// Check user capabilities.
		if ( ! current_user_can( 'edit_posts' ) ) {
			wp_send_json_error( array( 'message' => __( 'You do not have permission to perform this action.', 'hura-ai-content-generator' ) ) );
		}

		// Get and sanitize data.
		$title   = isset( $_POST['title'] ) ? sanitize_text_field( wp_unslash( $_POST['title'] ) ) : '';
		$content = isset( $_POST['content'] ) ? wp_kses_post( wp_unslash( $_POST['content'] ) ) : '';
		$category = isset( $_POST['category'] ) ? absint( $_POST['category'] ) : 0;

		if ( empty( $title ) || empty( $content ) ) {
			wp_send_json_error( array(
				'message' => __( 'Title and content cannot be empty.', 'hura-ai-content-generator' ),
			) );
		}

		// Prepare post data.
		$post_data = array(
			'post_title'   => $title,
			'post_content' => $content,
			'post_status'  => 'draft',
			'post_type'    => 'post',
			'post_category' => array( $category ),
		);

		// Create new post.
		$post_id = wp_insert_post( $post_data );

		if ( is_wp_error( $post_id ) ) {
			wp_send_json_error( array(
				'message' => $post_id->get_error_message(),
			) );
		}

		// Return success with edit link.
		$edit_link = get_edit_post_link( $post_id, 'raw' );
		wp_send_json_success( array(
			'post_id'  => $post_id,
			'edit_url' => $edit_link,
			'message'  => __( 'Draft post created successfully!', 'hura-ai-content-generator' ),
		) );
	}
}
