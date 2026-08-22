<?php
// Runs only when the plugin is deleted via WP Admin → Plugins → Delete.
if (! defined('WP_UNINSTALL_PLUGIN')) {
    http_response_code(404);
    exit;
}

delete_option('any2html_api_key');
delete_option('any2html_api_status');
delete_option('any2html_enabled');
