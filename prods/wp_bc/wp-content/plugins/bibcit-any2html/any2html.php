<?php

/**
 * Plugin Name:       Bibcit Any2HTML
 * Description:       Convert Markdown or file (pdf/image) to HTML inside the WordPress post editor using the Bibcit API. Requires a Bibcit API key obtained from bibcit.com. Your post content is sent to the Bibcit external API for conversion.
 * Version:           1.2.3
 * Requires at least: 6.5
 * Requires PHP:      8.0
 * Author:            Rakesh Kumar
 * Author URI:        https://profiles.wordpress.org/bibcithelp/
 * License:           GPL-2.0-or-later
 * License URI:       https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain:       bibcit-any2html
 */

if (!defined('ABSPATH')) {
    http_response_code(403);
    exit;
}

define('ANY2HTML_VERSION',        '1.2.3');
define('ANY2HTML_OPTION_KEY',     'any2html_api_key');
define('ANY2HTML_OPTION_STATUS',  'any2html_api_status');
define('ANY2HTML_OPTION_ENABLED', 'any2html_enabled');
define('BIBCIT_BASE_URL', 'https://www.bibcit.com');
define('ANY2HTML_API_BASE',       'https://api.bibcit.com');
define('ANY2HTML_PRIVACY_URL',    'https://www.bibcit.com/en/privacy');
define('ANY2HTML_TERMS_URL',      'https://www.bibcit.com/en/terms');

/* ── Settings page ─────────────────────────────────────────────────────── */

add_action('admin_menu', 'any2html_add_settings_page');
function any2html_add_settings_page()
{
    add_options_page(
        esc_html__('Bibcit Any2HTML', 'bibcit-any2html'),
        esc_html__('Bibcit Any2HTML', 'bibcit-any2html'),
        'manage_options',
        'any2html',
        'any2html_render_settings'
    );
}

/* Remove the auto-injected WP "Settings saved." notice on our page —
   we handle saving via AJAX and show our own inline message. */
add_action('admin_head', function () {
    $screen = get_current_screen();
    if ($screen && 'settings_page_any2html' === $screen->id) {
        remove_all_actions('admin_notices');
    }
});

function any2html_render_settings()
{
    if (! current_user_can('manage_options')) return;

    $key      = get_option(ANY2HTML_OPTION_KEY, '');
    $status   = get_option(ANY2HTML_OPTION_STATUS, '');
    $enabled  = get_option(ANY2HTML_OPTION_ENABLED, '0');
    $is_valid = ('valid' === $status);
?>
    <div class="wrap any2html-wrap">

        <div class="any2html-page-header">
            <div class="any2html-logo-badge" aria-hidden="true"><img src="<?php echo esc_url(plugin_dir_url(__FILE__) . 'blogo.png'); ?>"
                    width="50" height="50"
                    alt="<?php esc_attr_e('Bibcit Any2HTML', 'bibcit-any2html'); ?>"
                    class="any2html-logo-badge-img" /></div>
            <div class="any2html-header-text">
                <div class="any2html-page-title">
                    <?php esc_html_e('Bibcit Any2HTML', 'bibcit-any2html'); ?>
                    <span class="any2html-version-badge">v<?php echo esc_html(ANY2HTML_VERSION); ?></span>
                </div>
                <p class="any2html-page-subtitle"><?php esc_html_e('Convert Markdown and files (PDF/images) to HTML inside the post editor via the Bibcit API.', 'bibcit-any2html'); ?></p>
            </div>
        </div>

        <div class="any2html-notice">
            <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M18 10A8 8 0 1 1 2 10a8 8 0 0 1 16 0zm-7-4a1 1 0 1 0-2 0v4a1 1 0 0 0 2 0V6zm-1 8a1 1 0 1 0 0-2 1 1 0 0 0 0 2z" clip-rule="evenodd" />
            </svg>
            <span>
                <?php esc_html_e('Post content is transmitted to api.bibcit.com for conversion.', 'bibcit-any2html'); ?>
                <a href="<?php echo esc_url(ANY2HTML_PRIVACY_URL); ?>" target="_blank" rel="noopener noreferrer"><?php esc_html_e('Privacy Policy', 'bibcit-any2html'); ?></a>
                &middot;
                <a href="<?php echo esc_url(ANY2HTML_TERMS_URL); ?>" target="_blank" rel="noopener noreferrer"><?php esc_html_e('Terms of Service', 'bibcit-any2html'); ?></a>
            </span>
        </div>

        <form id="any2html-settings-form">
            <?php wp_nonce_field('any2html_save_settings', 'any2html_save_nonce'); ?>

            <div class="any2html-card">
                <div class="any2html-card-header">
                    <h2><?php esc_html_e('API Configuration', 'bibcit-any2html'); ?></h2>
                </div>
                <div class="any2html-card-body">

                    <div class="any2html-field">
                        <label class="any2html-label" for="any2html_api_key">
                            <?php esc_html_e('API Key', 'bibcit-any2html'); ?>
                        </label>
                        <p class="any2html-description">
                            <?php esc_html_e('Enter your Bibcit API key. Click Validate to verify it before saving.', 'bibcit-any2html'); ?>
                            <a href="https://www.bibcit.com/en" target="_blank" rel="noopener noreferrer"><?php esc_html_e('Get a key →', 'bibcit-any2html'); ?></a>
                        </p>
                        <div class="any2html-input-row">
                            <div class="any2html-input-wrap">
                                <input type="password"
                                    id="any2html_api_key"
                                    name="<?php echo esc_attr(ANY2HTML_OPTION_KEY); ?>"
                                    value="<?php echo esc_attr($key); ?>"
                                    class="any2html-input"
                                    autocomplete="off"
                                    placeholder="Enter your api key here" />
                                <button type="button" class="any2html-eye" id="any2html-toggle-eye" aria-label="<?php esc_attr_e('Show/hide key', 'bibcit-any2html'); ?>">
                                    <!-- eye: shown when input is password -->
                                    <svg id="any2html-icon-show" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                                        <circle cx="12" cy="12" r="3" />
                                    </svg>
                                    <!-- eye-off: shown when input is text -->
                                    <svg id="any2html-icon-hide" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="display:none">
                                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
                                        <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
                                        <line x1="1" y1="1" x2="23" y2="23" />
                                    </svg>
                                </button>
                            </div>
                            <button type="button" id="any2html-validate-key" class="any2html-btn any2html-btn-outline">
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                    <polyline points="20 6 9 17 4 12" />
                                </svg>
                                <?php esc_html_e('Validate Key', 'bibcit-any2html'); ?>
                            </button>
                        </div>
                        <div id="any2html-key-status-wrap">
                            <?php if ($is_valid) : ?>
                                <span class="any2html-status-pill any2html-status-valid">
                                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                        <polyline points="20 6 9 17 4 12" />
                                    </svg>
                                    <?php esc_html_e('Key validated', 'bibcit-any2html'); ?>
                                </span>
                            <?php elseif ('invalid' === $status) : ?>
                                <span class="any2html-status-pill any2html-status-invalid">
                                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                        <line x1="18" y1="6" x2="6" y2="18" />
                                        <line x1="6" y1="6" x2="18" y2="18" />
                                    </svg>
                                    <?php esc_html_e('Invalid key', 'bibcit-any2html'); ?>
                                </span>
                            <?php endif; ?>
                        </div>
                        <input type="hidden" id="any2html_api_status"
                            name="<?php echo esc_attr(ANY2HTML_OPTION_STATUS); ?>"
                            value="<?php echo esc_attr($status); ?>" />
                    </div>

                </div>
            </div>

            <div class="any2html-form-footer" id="any2html-form-footer" <?php if (! $is_valid) echo 'style="display:none"'; ?>>
                <button type="button" id="any2html-save-btn" class="any2html-btn any2html-btn-primary any2html-save-btn">
                    <?php esc_html_e('Save Settings', 'bibcit-any2html'); ?>
                </button>
                <span id="any2html-save-status"></span>
            </div>

        </form>
    </div><!-- /.any2html-wrap -->
<?php
}

add_action('admin_init', 'any2html_register_settings');
function any2html_register_settings()
{
    register_setting('any2html_settings', ANY2HTML_OPTION_KEY,     ['sanitize_callback' => 'sanitize_text_field']);
    register_setting('any2html_settings', ANY2HTML_OPTION_STATUS,  ['sanitize_callback' => 'sanitize_text_field']);
    register_setting('any2html_settings', ANY2HTML_OPTION_ENABLED, ['sanitize_callback' => 'sanitize_text_field']);
}

/* ── AJAX: save settings ───────────────────────────────────────────────── */

add_action('wp_ajax_any2html_save_settings', 'any2html_ajax_save_settings');
function any2html_ajax_save_settings()
{
    check_ajax_referer('any2html_save_settings', 'nonce');
    if (! current_user_can('manage_options')) wp_send_json_error(null, 403);

    update_option(ANY2HTML_OPTION_KEY,     sanitize_text_field(wp_unslash($_POST['api_key']  ?? '')), false);
    update_option(ANY2HTML_OPTION_STATUS,  sanitize_text_field(wp_unslash($_POST['api_status'] ?? '')), false);
    update_option(ANY2HTML_OPTION_ENABLED, sanitize_text_field(wp_unslash($_POST['enabled']  ?? '0')), false);

    wp_send_json_success();
}

/* ── AJAX: validate key ────────────────────────────────────────────────── */

add_action('wp_ajax_any2html_validate_key', 'any2html_ajax_validate_key');
function any2html_ajax_validate_key()
{
    check_ajax_referer('any2html_validate');
    if (! current_user_can('manage_options')) wp_send_json_error(null, 403);

    $key      = sanitize_text_field(wp_unslash($_POST['api_key'] ?? ''));
    $response = wp_remote_get(ANY2HTML_API_BASE . '/validator/ckeyValidate?ckey=' . $key, [
        'timeout' => 10,
    ]);

    $valid = ! is_wp_error($response) && 200 === wp_remote_retrieve_response_code($response);
    update_option(ANY2HTML_OPTION_STATUS, $valid ? 'valid' : 'invalid', false);
    wp_send_json_success(['valid' => json_decode(wp_remote_retrieve_body($response), true)]);
}

/* ── AJAX: convert file (PDF/image → markdown → HTML) ─────────────────── */

add_action('wp_ajax_any2html_file_convert', 'any2html_ajax_file_convert');
function any2html_ajax_file_convert()
{
    check_ajax_referer('any2html_file_convert');
    if (! current_user_can('edit_posts')) wp_send_json_error(['message' => 'Unauthorized'], 403);

    if ('valid' !== get_option(ANY2HTML_OPTION_STATUS)) {
        wp_send_json_error(['message' => 'API key is invalid.']);
    }

    if (empty($_FILES['file']['tmp_name'])) {
        wp_send_json_error(['message' => 'No file uploaded.']);
    }

    if (isset($_FILES['file']['size']) && $_FILES['file']['size'] > 5 * 1024 * 1024) {
        wp_send_json_error(['message' => 'File exceeds the 5 MB limit.']);
    }

    $allowed_mimes = ['application/pdf', 'image/jpeg', 'image/png'];
    if (!in_array($_FILES['file']['type'] ?? '', $allowed_mimes, true)) {
        wp_send_json_error(['message' => 'Invalid file type.']);
    }

    $key = get_option(ANY2HTML_OPTION_KEY, '');
    if (empty($key)) {
        wp_send_json_error(['message' => 'Invalid API key. Please set and validate your API key first.']);
    }

    // Generate a boundary string
    $boundary = wp_generate_password(24, false);

    $file_tmp_name = (sanitize_text_field($_FILES['file']['tmp_name']) ?? ''); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput.InputNotSanitized

    $filename = empty($_FILES['file']['name']) ? 'temp' : basename(sanitize_file_name(wp_unslash($_FILES['file']['name'])));
    $file_type = wp_check_filetype_and_ext($file_tmp_name, sanitize_file_name(wp_unslash($file['name'] ?? '')));

    // Prepare the multipart body
    $body = '';
    $body .= '--' . $boundary . "\r\n";
    $body .= 'Content-Disposition: form-data; name="file"; filename="' . $filename . '"' . "\r\n";
    $body .= 'Content-Type: ' . $file_type . "\r\n\r\n";
    $body .= file_get_contents($file_tmp_name) . "\r\n";
    $body .= '--' . $boundary . '--' . "\r\n";


    $pix_response = wp_remote_post(ANY2HTML_API_BASE . '/api/massivepix/ftom', [
        'headers' => [
            'Bibcit-Key'   => $key,
            'Content-Type' => 'multipart/form-data; boundary=' . $boundary,
        ],
        'body'    => $body,
        'timeout' => 60,
    ]);

    if (is_wp_error($pix_response)) {
        wp_send_json_error(['message' => $pix_response->get_error_message()]);
    }

    $pix_code = wp_remote_retrieve_response_code($pix_response);
    $markdown = $pix_response['body'] ?? '';

    if (in_array($pix_code, [401, 403], true)) {
        update_option(ANY2HTML_OPTION_STATUS, 'invalid', false);
        wp_send_json_error([
            'message'      => 'API key is unauthorized. Please re-validate your key.',
            'key_invalid'  => true,
            'settings_url' => admin_url('options-general.php?page=any2html'),
        ]);
    }

    if (200 !== $pix_code || empty($markdown)) {
        wp_send_json_error(['message' => $pix_body['message'] ?? 'File conversion failed.']);
    }


    $mark_response = wp_remote_post(ANY2HTML_API_BASE . '/api/massivemark/mtoh', [
        'headers' => [
            'Bibcit-Key'   => $key,
            'Content-Type' => 'text/plain;charset=UTF-8',
        ],
        'body'    => $markdown,
        'timeout' => 15,
    ]);

    if (is_wp_error($mark_response)) {
        wp_send_json_error(['message' => $mark_response->get_error_message()]);
    }

    $mark_code = wp_remote_retrieve_response_code($mark_response);
    $mark_body = json_decode(wp_remote_retrieve_body($mark_response), true);

    if (in_array($mark_code, [401, 403], true)) {
        update_option(ANY2HTML_OPTION_STATUS, 'invalid', false);
        wp_send_json_error([
            'message'      => 'API key is unauthorized. Please re-validate your key.',
            'key_invalid'  => true,
            'settings_url' => admin_url('options-general.php?page=any2html'),
        ]);
    }

    if (200 !== $mark_code || empty($mark_body['htmlContent'])) {
        wp_send_json_error(['message' => $mark_body['message'] ?? 'Markdown to HTML conversion failed.']);
    }

    wp_send_json_success(['html' => $mark_body['htmlContent']]);
}

/* ── AJAX: classify diagram code ───────────────────────────────────────── */

add_action('wp_ajax_any2html_diag_classify', 'any2html_ajax_diag_classify');
function any2html_ajax_diag_classify()
{
    check_ajax_referer('any2html_diag_convert');
    if (! current_user_can('edit_posts')) wp_send_json_error(null, 403);

    $diag_code = ($_POST['diag_code'] ?? ''); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput.InputNotSanitized, WordPress.Security.ValidatedSanitizedInput.MissingUnslash
    if (empty($diag_code)) {
        wp_send_json_error(['message' => 'Diagram code is required.']);
    }

    $key = get_option(ANY2HTML_OPTION_KEY, '');

    $response = wp_remote_post(ANY2HTML_API_BASE . '/api/mdiag/classify', [
        'headers' => [
            'Bibcit-Key'   => $key,
            'Content-Type' => 'text/plain',
        ],
        'body'    => $diag_code,
        'timeout' => 10,
    ]);

    if (is_wp_error($response)) {
        wp_send_json_error(['message' => $response->get_error_message()]);
    }
    $code = wp_remote_retrieve_response_code($response);
    $body = json_decode(wp_remote_retrieve_body($response), true);

    if (200 !== $code || empty($body['type'])) {
        wp_send_json_error(['message' => 'Could not classify diagram.']);
    }

    wp_send_json_success(['diag_type' => sanitize_text_field($body['type'])]);
}

/* ── AJAX: convert diagram code ───────────────────────────────────────── */

add_action('wp_ajax_any2html_diag_convert', 'any2html_ajax_diag_convert');
function any2html_ajax_diag_convert()
{
    check_ajax_referer('any2html_diag_convert');
    if (! current_user_can('edit_posts')) wp_send_json_error(['message' => 'Unauthorized'], 403);

    if ('valid' !== get_option(ANY2HTML_OPTION_STATUS)) {
        wp_send_json_error(['message' => 'API key is invalid.']);
    }

    $diag_type = sanitize_text_field(wp_unslash($_REQUEST['diag_type'] ?? ''));
    $diag_code = file_get_contents('php://input');

    $key       = get_option(ANY2HTML_OPTION_KEY, '');
    // error_log('Converting diagram with type: ' . $diag_type . ' and code: ' . $diag_code); // Debug log for input values
    if ($diag_type === 'unknown') {
        $diag_type = '';
        wp_send_json_error(['message' => 'Unable to autodetect Diagram type. Please select a type manually..']);
    }
    //if (empty($diag_code)) {
    if (empty($diag_type) || empty($diag_code)) {
        wp_send_json_error(['message' => 'Diagram type and code are required.']);
    }

    $response = wp_remote_post(ANY2HTML_API_BASE . '/api/mdiag/code2Svg', [
        'headers' => [
            'Bibcit-Key'   => $key,
            'Content-Type' => 'text/plain;charset=UTF-8',
            'x-diag-type' => $diag_type,
        ],
        'body'    => $diag_code,
        'timeout' => 30,
    ]);

    if (is_wp_error($response)) {
        wp_send_json_error(['message' => $response->get_error_message()]);
    }

    $code = wp_remote_retrieve_response_code($response);

    // error_log('API response code: ' . $code . ' => ' . print_r($response, true)); // Debug log for API response code

    if (in_array($code, [401, 403, 500, 504], true)) {
        if (401 === $code) {
            update_option(ANY2HTML_OPTION_STATUS, 'invalid', false);
        }
        wp_send_json_error([
            'code'         => $code,
            'message'      => 401 === $code ? 'API key is unauthorized. Please re-validate your key.' : wp_remote_retrieve_body($response),
            'key_invalid'  => true,
            'settings_url' => admin_url('options-general.php?page=any2html'),
        ]);
    }
    if ($code !== 200) {
        wp_send_json_error(['message' => 'Something went wrong. Please make sure your diagram code and type is correct.']);
    }

    $body = json_decode(wp_remote_retrieve_body($response), true);

    wp_send_json_success(['html' => $body]);
}

/* ── AJAX: convert markdown ────────────────────────────────────────────── */

add_action('wp_ajax_any2html_convert', 'any2html_ajax_convert');
function any2html_ajax_convert()
{
    check_ajax_referer('any2html_convert');
    if (! current_user_can('edit_posts')) wp_send_json_error(['message' => 'Unauthorized'], 403);

    if ('valid' !== get_option(ANY2HTML_OPTION_STATUS)) {
        wp_send_json_error(['message' => 'API key is invalid.']);
    }

    $markdown = sanitize_textarea_field(wp_unslash($_POST['markdown'] ?? ''));
    $key      = get_option(ANY2HTML_OPTION_KEY, '');

    $response = wp_remote_post(ANY2HTML_API_BASE . '/api/massivemark/mtoh', [
        'headers' => [
            'Bibcit-Key'   => $key,
            'Content-Type' => 'text/plain;charset=UTF-8',
        ],
        'body'    => $markdown,
        'timeout' => 15,
    ]);

    if (is_wp_error($response)) {
        wp_send_json_error(['message' => $response->get_error_message()]);
    }
    $code = wp_remote_retrieve_response_code($response);

    if (in_array($code, [401, 403], true)) {
        if ($code === 401) {
            update_option(ANY2HTML_OPTION_STATUS, 'invalid', false);
        }
        wp_send_json_error([
            'code'         => $code,
            'message'      => ($code === 403) ? $response['body'] : 'API key is unauthorized. Please re-validate your key.',
            'key_invalid'  => true,
            'settings_url' => admin_url('options-general.php?page=any2html'),
        ]);
    }

    $body = json_decode(wp_remote_retrieve_body($response), true);

    if (200 !== $code || empty($body['htmlContent'])) {
        wp_send_json_error(['message' => $body['message'] ?? 'Conversion failed.']);
    }

    wp_send_json_success(['html' => $body['htmlContent']]);
}

/* ── Post editor meta box ──────────────────────────────────────────────── */

add_action('add_meta_boxes', 'any2html_add_meta_box');
function any2html_add_meta_box()
{
    if ('valid' !== get_option(ANY2HTML_OPTION_STATUS)) return;

    foreach (get_post_types() as $post_type) {
        if (post_type_supports($post_type, 'editor')) {
            add_meta_box(
                'any2html_box',
                esc_html__('Bibcit Any2HTML', 'bibcit-any2html'),
                'any2html_render_meta_box',
                $post_type
            );
        }
    }
}

function any2html_render_meta_box()
{
?>
    <div id="any2html-panel">

        <div class="a2h-tabs" role="tablist">
            <button type="button" class="a2h-tab a2h-tab--active" id="a2h-tab-md" role="tab" aria-selected="true" aria-controls="a2h-pane-md">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                    <line x1="16" y1="13" x2="8" y2="13" />
                    <line x1="16" y1="17" x2="8" y2="17" />
                </svg>
                <?php esc_html_e('Markdown', 'bibcit-any2html'); ?>
            </button>
            <button type="button" class="a2h-tab" id="a2h-tab-file" role="tab" aria-selected="false" aria-controls="a2h-pane-file">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                <?php esc_html_e('Upload File', 'bibcit-any2html'); ?>
            </button>
            <button type="button" class="a2h-tab" id="a2h-tab-diag" role="tab" aria-selected="false" aria-controls="a2h-pane-diag">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <rect x="3" y="3" width="7" height="7" />
                    <rect x="14" y="3" width="7" height="7" />
                    <rect x="14" y="14" width="7" height="7" />
                    <rect x="3" y="14" width="7" height="7" />
                </svg>
                <?php esc_html_e('Diagram Code', 'bibcit-any2html'); ?>
            </button>
        </div>

        <div id="a2h-pane-md" role="tabpanel" aria-labelledby="a2h-tab-md">
            <div class="a2h-md-toolbar">
                <span class="a2h-md-hint"><?php esc_html_e('Paste Markdown below', 'bibcit-any2html'); ?></span>
                <button type="button" class="a2h-clear-btn" id="any2html-md-clear">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <line x1="18" y1="6" x2="6" y2="18" />
                        <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                    <?php esc_html_e('Clear', 'bibcit-any2html'); ?>
                </button>
            </div>
            <textarea id="any2html-input"
                placeholder="# Heading&#10;&#10;Paste your **Markdown** here&hellip;"
                spellcheck="false"></textarea>
        </div>

        <div id="a2h-pane-diag" role="tabpanel" aria-labelledby="a2h-tab-diag" hidden>
            <div class="a2h-diag-toolbar">
                <label for="a2h-diag-type" class="a2h-diag-label"><?php esc_html_e('Diagram type', 'bibcit-any2html'); ?></label>
                <div class="a2h-diag-select-wrap hidden">
                    <select id="a2h-diag-type">
                        <option value=""><?php esc_html_e('— select type —', 'bibcit-any2html'); ?></option>
                        <option value="unknown"><?php esc_html_e('Unknown', 'bibcit-any2html'); ?></option>
                        <optgroup label="<?php esc_attr_e('UML &amp; Software Architecture', 'bibcit-any2html'); ?>">
                            <option value="plantuml">PlantUML</option>
                            <option value="c4plantuml">C4 PlantUML</option>
                            <option value="mermaid">Mermaid</option>
                            <option value="nomnoml">Nomnoml</option>
                            <option value="dbml">DBML</option>
                            <option value="structurizr">Structurizr</option>
                            <option value="umlet">UMLet</option>
                        </optgroup>
                        <optgroup label="<?php esc_attr_e('Graphs &amp; Networks', 'bibcit-any2html'); ?>">
                            <option value="graphviz">Graphviz</option>
                            <option value="d2">D2</option>
                            <option value="erd">ERD</option>
                            <option value="smiles">SMILES</option>
                        </optgroup>
                        <optgroup label="<?php esc_attr_e('Block &amp; Flow Diagrams', 'bibcit-any2html'); ?>">
                            <option value="blockdiag">BlockDiag</option>
                            <option value="actdiag">ActDiag</option>
                            <option value="nwdiag">NwDiag</option>
                            <option value="packetdiag">PacketDiag</option>
                            <option value="rackdiag">RackDiag</option>
                            <option value="seqdiag">SeqDiag</option>
                            <option value="bpmn">BPMN</option>
                            <option value="ditaa">Ditaa</option>
                            <option value="pikchr">Pikchr</option>
                        </optgroup>
                        <optgroup label="<?php esc_attr_e('Technical &amp; Specialized', 'bibcit-any2html'); ?>">
                            <option value="wavedrom">WaveDrom</option>
                            <option value="bytefield">Bytefield</option>
                            <option value="svgbob">SVGBob</option>
                            <option value="tikz">TikZ</option>
                            <option value="symbolator">Symbolator</option>
                            <option value="wireviz">WireViz</option>
                        </optgroup>
                        <optgroup label="<?php esc_attr_e('Data &amp; Mind Visualization', 'bibcit-any2html'); ?>">
                            <option value="vega">Vega</option>
                            <option value="Vegalite">Vega-Lite</option>
                            <option value="excalidraw">Excalidraw</option>
                            <option value="markmap">Markmap</option>
                        </optgroup>
                        <optgroup label="<?php esc_attr_e('Vector Graphics', 'bibcit-any2html'); ?>">
                            <option value="svg">SVG</option>
                        </optgroup>
                    </select>
                    <svg class="a2h-select-chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <polyline points="6 9 12 15 18 9" />
                    </svg>
                </div>
            </div>
            <div class="a2h-diag-body">
                <textarea id="any2html-diag-input"
                    placeholder="<?php esc_attr_e('Paste your diagram code here…', 'bibcit-any2html'); ?>"
                    spellcheck="false"></textarea>
                <button type="button" class="a2h-diag-clear" id="any2html-diag-clear" aria-label="<?php esc_attr_e('Clear', 'bibcit-any2html'); ?>">
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <line x1="18" y1="6" x2="6" y2="18" />
                        <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                </button>
            </div>
        </div>

        <div id="a2h-pane-file" role="tabpanel" aria-labelledby="a2h-tab-file" hidden>
            <input type="file" id="any2html-file-input" accept=".pdf,image/*" style="display:none" />
            <div class="a2h-dropzone" id="any2html-upload-area">
                <div class="a2h-dropzone-icon">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <polyline points="17 8 12 3 7 8" />
                        <line x1="12" y1="3" x2="12" y2="15" />
                    </svg>
                </div>
                <p class="a2h-dropzone-title"><?php esc_html_e('Drop your file here', 'bibcit-any2html'); ?></p>
                <p class="a2h-dropzone-sub"><?php esc_html_e('or click to browse &mdash; PDF or image, max 5 MB', 'bibcit-any2html'); ?></p>
            </div>
            <div class="a2h-file-chip" id="a2h-file-chip" hidden>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                </svg>
                <span id="a2h-file-name"></span>
                <span id="a2h-file-size" class="a2h-file-size"></span>
                <button type="button" class="a2h-chip-remove" id="a2h-file-remove" aria-label="<?php esc_attr_e('Remove file', 'bibcit-any2html'); ?>">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <line x1="18" y1="6" x2="6" y2="18" />
                        <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                </button>
            </div>
        </div>

        <div class="a2h-footer">
            <button type="button" id="any2html-convert" class="any2html-btn any2html-btn-primary">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <polyline points="5 12 12 5 19 12" />
                    <polyline points="5 19 12 12 19 19" />
                </svg>
                <span class="a2h-btn-label"><?php esc_html_e('Convert to HTML', 'bibcit-any2html'); ?></span>
            </button>
            <div class="a2h-status-wrap">
                <div class="a2h-progress" id="a2h-progress" hidden>
                    <div class="a2h-progress-bar" id="a2h-progress-bar"></div>
                </div>
                <span id="any2html-status"></span>
            </div>
        </div>

    </div>
<?php
}

/* ── Enqueue assets ────────────────────────────────────────────────────── */

add_action('admin_enqueue_scripts', 'any2html_enqueue');
function any2html_enqueue($hook)
{
    $base = plugin_dir_url(__FILE__);

    wp_enqueue_style('any2html-style', $base . 'any2html.css', [], ANY2HTML_VERSION);

    if ('settings_page_any2html' === $hook) {
        wp_enqueue_script('any2html-settings', $base . 'any2html-settings.js', ['jquery'], ANY2HTML_VERSION, true);
        wp_localize_script('any2html-settings', 'any2htmlSettings', [
            'ajaxUrl'    => admin_url('admin-ajax.php'),
            'nonce'      => wp_create_nonce('any2html_validate'),
            'saveNonce'  => wp_create_nonce('any2html_save_settings'),
        ]);
    }

    if (in_array($hook, ['post.php', 'post-new.php'], true)) {
        wp_enqueue_script('any2html-editor', $base . 'any2html-editor.js', ['jquery'], ANY2HTML_VERSION, true);
        wp_localize_script('any2html-editor', 'any2htmlEditor', [
            'ajaxUrl'   => admin_url('admin-ajax.php'),
            'nonce'     => wp_create_nonce('any2html_convert'),
            'fileNonce' => wp_create_nonce('any2html_file_convert'),
            'diagNonce' => wp_create_nonce('any2html_diag_convert'),
        ]);
    }
}
