<?php
/**
 * Template for the plugin Generate page.
 *
 * Two-column layout: Left column (Sidebar) with customization form,
 * right column (Main Content) with the editor or placeholder.
 *
 * @package Hura_AI_Content_Generator
 * @since   1.0.0
 */

// Prevent direct access.
defined( 'ABSPATH' ) || exit;

// Get default language from settings.
$hura_ai_default_lang = get_option( 'hura_ai_default_lang', 'English' );

// Get category list.
$hura_ai_categories = get_categories( array(
	'hide_empty' => false,
	'orderby'    => 'name',
	'order'      => 'ASC',
) );
?>

<div class="wrap">
	<h1><?php echo esc_html( get_admin_page_title() ); ?></h1>

	<div class="hura-ai-generator-wrapper">
		<!-- COLUMN 1: SIDEBAR FORM (33.333%) -->
		<div class="hura-ai-sidebar">
			<div class="postbox">
				<div class="postbox-header">
					<h2 class="hndle"><?php esc_html_e( 'Content Settings', 'hura-ai-content-generator' ); ?></h2>
				</div>
				<div class="inside">
					<form id="hura-ai-generate-form">
						<!-- Category -->
						<div class="hura-ai-field">
							<label for="hura-ai-category"><?php esc_html_e( 'Category', 'hura-ai-content-generator' ); ?></label>
							<select id="hura-ai-category" name="category">
								<option value=""><?php esc_html_e( '-- Select Category --', 'hura-ai-content-generator' ); ?></option>
								<?php foreach ( $hura_ai_categories as $hura_ai_cat ) : ?>
									<option value="<?php echo esc_attr( $hura_ai_cat->term_id ); ?>">
										<?php echo esc_html( $hura_ai_cat->name ); ?>
									</option>
								<?php endforeach; ?>
							</select>
						</div>

						<!-- Language -->
						<div class="hura-ai-field">
							<label for="hura-ai-language"><?php esc_html_e( 'Language', 'hura-ai-content-generator' ); ?></label>
							<select id="hura-ai-language" name="language">
								<option value="English" <?php selected( $hura_ai_default_lang, 'English' ); ?>><?php esc_html_e( 'English', 'hura-ai-content-generator' ); ?></option>
								<option value="Arabic" <?php selected( $hura_ai_default_lang, 'Arabic' ); ?>><?php esc_html_e( 'Arabic', 'hura-ai-content-generator' ); ?></option>
								<option value="Chinese" <?php selected( $hura_ai_default_lang, 'Chinese' ); ?>><?php esc_html_e( 'Chinese', 'hura-ai-content-generator' ); ?></option>
								<option value="Danish" <?php selected( $hura_ai_default_lang, 'Danish' ); ?>><?php esc_html_e( 'Danish', 'hura-ai-content-generator' ); ?></option>
								<option value="Dutch" <?php selected( $hura_ai_default_lang, 'Dutch' ); ?>><?php esc_html_e( 'Dutch', 'hura-ai-content-generator' ); ?></option>
								<option value="French" <?php selected( $hura_ai_default_lang, 'French' ); ?>><?php esc_html_e( 'French', 'hura-ai-content-generator' ); ?></option>
								<option value="German" <?php selected( $hura_ai_default_lang, 'German' ); ?>><?php esc_html_e( 'German', 'hura-ai-content-generator' ); ?></option>
								<option value="Hindi" <?php selected( $hura_ai_default_lang, 'Hindi' ); ?>><?php esc_html_e( 'Hindi', 'hura-ai-content-generator' ); ?></option>
								<option value="Indonesian" <?php selected( $hura_ai_default_lang, 'Indonesian' ); ?>><?php esc_html_e( 'Indonesian', 'hura-ai-content-generator' ); ?></option>
								<option value="Italian" <?php selected( $hura_ai_default_lang, 'Italian' ); ?>><?php esc_html_e( 'Italian', 'hura-ai-content-generator' ); ?></option>
								<option value="Japanese" <?php selected( $hura_ai_default_lang, 'Japanese' ); ?>><?php esc_html_e( 'Japanese', 'hura-ai-content-generator' ); ?></option>
								<option value="Korean" <?php selected( $hura_ai_default_lang, 'Korean' ); ?>><?php esc_html_e( 'Korean', 'hura-ai-content-generator' ); ?></option>
								<option value="Portuguese" <?php selected( $hura_ai_default_lang, 'Portuguese' ); ?>><?php esc_html_e( 'Portuguese', 'hura-ai-content-generator' ); ?></option>
								<option value="Russian" <?php selected( $hura_ai_default_lang, 'Russian' ); ?>><?php esc_html_e( 'Russian', 'hura-ai-content-generator' ); ?></option>
								<option value="Spanish" <?php selected( $hura_ai_default_lang, 'Spanish' ); ?>><?php esc_html_e( 'Spanish', 'hura-ai-content-generator' ); ?></option>
								<option value="Swedish" <?php selected( $hura_ai_default_lang, 'Swedish' ); ?>><?php esc_html_e( 'Swedish', 'hura-ai-content-generator' ); ?></option>
								<option value="Thai" <?php selected( $hura_ai_default_lang, 'Thai' ); ?>><?php esc_html_e( 'Thai', 'hura-ai-content-generator' ); ?></option>
								<option value="Turkish" <?php selected( $hura_ai_default_lang, 'Turkish' ); ?>><?php esc_html_e( 'Turkish', 'hura-ai-content-generator' ); ?></option>
								<option value="Vietnamese" <?php selected( $hura_ai_default_lang, 'Vietnamese' ); ?>><?php esc_html_e( 'Vietnamese', 'hura-ai-content-generator' ); ?></option>
							</select>
						</div>

						<!-- Tone -->
						<div class="hura-ai-field">
							<label for="hura-ai-tone"><?php esc_html_e( 'Writing Tone', 'hura-ai-content-generator' ); ?></label>
							<select id="hura-ai-tone" name="tone">
								<option value="Professional"><?php esc_html_e( 'Professional', 'hura-ai-content-generator' ); ?></option>
								<option value="Creative"><?php esc_html_e( 'Creative', 'hura-ai-content-generator' ); ?></option>
								<option value="Informative"><?php esc_html_e( 'Informative', 'hura-ai-content-generator' ); ?></option>
								<option value="Casual"><?php esc_html_e( 'Casual', 'hura-ai-content-generator' ); ?></option>
							</select>
						</div>

						<!-- Keywords -->
						<div class="hura-ai-field">
							<label for="hura-ai-keywords"><?php esc_html_e( 'Keywords', 'hura-ai-content-generator' ); ?></label>
							<textarea id="hura-ai-keywords" name="keywords" rows="3" placeholder="<?php esc_attr_e( 'Enter keywords, separated by commas...', 'hura-ai-content-generator' ); ?>"></textarea>
						</div>

						<!-- Post Length -->
						<div class="hura-ai-field">
							<label for="hura-ai-length"><?php esc_html_e( 'Post Length', 'hura-ai-content-generator' ); ?></label>
							<select id="hura-ai-length" name="length">
								<option value="Short (500-800 words)"><?php esc_html_e( 'Short (500-800 words)', 'hura-ai-content-generator' ); ?></option>
								<option value="Medium (800-1500 words)" selected><?php esc_html_e( 'Medium (800-1500 words)', 'hura-ai-content-generator' ); ?></option>
								<option value="Long (1500+ words)"><?php esc_html_e( 'Long (1500+ words)', 'hura-ai-content-generator' ); ?></option>
							</select>
						</div>

						<!-- Additional Description -->
						<div class="hura-ai-field">
							<label for="hura-ai-description"><?php esc_html_e( 'Additional Description', 'hura-ai-content-generator' ); ?></label>
							<textarea id="hura-ai-description" name="description" rows="4" placeholder="<?php esc_attr_e( 'Describe any additional requirements for the article...', 'hura-ai-content-generator' ); ?>"></textarea>
						</div>

						<!-- Generate Button -->
						<div class="hura-ai-field hura-ai-field-submit">
							<button type="button" id="hura-btn-generate" class="button button-primary button-large">
								<?php esc_html_e( 'Generate', 'hura-ai-content-generator' ); ?>
							</button>
						</div>
					</form>
				</div><!-- .inside -->
			</div><!-- .postbox -->
		</div><!-- .hura-ai-sidebar -->

		<!-- COLUMN 2: MAIN CONTENT (66.666%) -->
		<div class="hura-ai-main-content">
			<div class="postbox">
				<div class="postbox-header">
					<h2 class="hndle"><?php esc_html_e( 'Article Content', 'hura-ai-content-generator' ); ?></h2>
				</div>
				<div class="inside">
					<!-- Loading Area -->
					<div id="hura-ai-loading" class="hura-ai-loading" style="display: none;">
						<span class="spinner is-active"></span>
						<p><?php esc_html_e( 'Generating content, please wait...', 'hura-ai-content-generator' ); ?></p>
					</div>

					<!-- Default placeholder when no content -->
					<div id="hura-ai-placeholder" class="hura-ai-placeholder">
						<div class="hura-ai-placeholder-icon">
							<span class="dashicons dashicons-edit"></span>
						</div>
						<p><?php esc_html_e( 'Please fill in the parameters on the left and click "Generate" to create an article.', 'hura-ai-content-generator' ); ?></p>
					</div>

					<!-- Editor Area (hidden by default) -->
					<div id="hura-ai-editor-area" class="hura-ai-editor-area" style="display: none;">
						<div class="hura-ai-title-field">
							<label for="hura-ai-post-title"><?php esc_html_e( 'Article Title', 'hura-ai-content-generator' ); ?></label>
							<input type="text" id="hura-ai-post-title" class="large-text" />
						</div>

						<div class="hura-ai-content-field">
							<label><?php esc_html_e( 'Content', 'hura-ai-content-generator' ); ?></label>
							<?php
							// Initialize WordPress editor.
							wp_editor(
								'',
								'hura_ai_editor',
								array(
									'textarea_name' => 'hura_ai_content',
									'textarea_rows' => 25,
									'media_buttons' => true,
									'teeny'         => false,
									'quicktags'     => true,
									'tinymce'       => array(
										'toolbar1' => 'bold,italic,underline,separator,bullist,numlist,separator,link,unlink,separator,undo,redo,separator,wp_adv',
										'toolbar2' => 'formatselect,separator,forecolor,separator,alignleft,aligncenter,alignright,separator,removeformat',
									),
								)
							);
							?>
						</div>

						<!-- Action Buttons -->
						<div class="hura-ai-actions">
							<button type="button" id="hura-btn-copy" class="button button-secondary">
								<?php esc_html_e( 'Copy to Clipboard', 'hura-ai-content-generator' ); ?>
							</button>
							<button type="button" id="hura-btn-save" class="button button-primary">
								<?php esc_html_e( 'Save as Draft', 'hura-ai-content-generator' ); ?>
							</button>
						</div>
					</div><!-- .hura-ai-editor-area -->
				</div><!-- .inside -->
			</div><!-- .postbox -->

			<!-- Admin Notice Area (for Toast) -->
			<div id="hura-ai-notices"></div>
		</div><!-- .hura-ai-main-content -->
	</div><!-- .hura-ai-generator-wrapper -->
	<?php include HURA_AI_PLUGIN_DIR . 'admin/partials/footer-copyright.php'; ?>
</div><!-- .wrap -->
