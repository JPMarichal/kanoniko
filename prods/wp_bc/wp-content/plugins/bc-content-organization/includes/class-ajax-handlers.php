<?php

class BCCO_Ajax_Handlers {

    public function __construct() {
        add_action('wp_ajax_bcco_reorder_series', [$this, 'reorder_series']);
        add_action('wp_ajax_bcco_reorder_posts', [$this, 'reorder_posts']);
        add_action('wp_ajax_bcco_load_series_posts', [$this, 'load_series_posts']);
        add_action('wp_ajax_bcco_get_counts', [$this, 'get_counts']);
    }

    public function reorder_series() {
        check_ajax_referer('bcco_admin_nonce', 'nonce');
        if (!current_user_can('manage_categories')) {
            wp_send_json_error(__('No autorizado', 'bcco'));
        }

        $series_ids = isset($_POST['series_ids']) ? array_map('intval', $_POST['series_ids']) : [];
        $term_ids = [];

        foreach ($series_ids as $order => $term_id) {
            update_term_meta($term_id, '_series_order', $order + 1);
            $term_ids[] = $term_id;
        }

        if (!empty($term_ids)) {
            clean_term_cache($term_ids, 'collection');
        }

        wp_send_json_success();
    }

    public function reorder_posts() {
        check_ajax_referer('bcco_admin_nonce', 'nonce');
        if (!current_user_can('edit_posts')) {
            wp_send_json_error(__('No autorizado', 'bcco'));
        }

        $post_ids = isset($_POST['post_ids']) ? array_map('intval', $_POST['post_ids']) : [];

        foreach ($post_ids as $position => $post_id) {
            update_post_meta($post_id, '_series_position', $position + 1);
            clean_post_cache($post_id);
        }

        wp_send_json_success();
    }

    public function load_series_posts() {
        check_ajax_referer('bcco_admin_nonce', 'nonce');
        if (!current_user_can('edit_posts')) {
            wp_send_json_error(__('No autorizado', 'bcco'));
        }

        $series_id = isset($_POST['series_id']) ? intval($_POST['series_id']) : 0;
        $offset    = isset($_POST['offset']) ? intval($_POST['offset']) : 0;
        $per_page  = isset($_POST['per_page']) ? intval($_POST['per_page']) : 20;
        $search    = isset($_POST['search']) ? sanitize_text_field($_POST['search']) : '';
        $post_type = isset($_POST['post_type']) ? sanitize_key($_POST['post_type']) : '';

        if (!$series_id) wp_send_json_error();

        $post_types = bcco_get_post_types();
        if ($post_type && in_array($post_type, $post_types, true)) {
            $post_types = [$post_type];
        }

        $args = [
            'post_type'      => $post_types,
            'numberposts'    => $per_page,
            'offset'         => $offset,
            'tax_query'      => [[
                'taxonomy' => 'collection',
                'field'    => 'term_id',
                'terms'    => $series_id,
            ]],
            'meta_key'       => '_series_position',
            'orderby'        => 'meta_value_num',
            'order'          => 'ASC',
        ];

        if ($search) {
            $args['s'] = $search;
        }

        $posts = get_posts($args);

        $total_args = $args;
        unset($total_args['numberposts'], $total_args['offset']);
        $total_args['fields'] = 'ids';
        $total_query = new WP_Query($total_args);
        $total = $total_query->found_posts;

        ob_start();
        foreach ($posts as $p) :
            $pos = (int) get_post_meta($p->ID, '_series_position', true);
            ?>
            <li class="bcco-post" id="bcco-post-<?php echo $p->ID; ?>" data-post-id="<?php echo $p->ID; ?>">
                <span class="bcco-post-handle dashicons dashicons-menu"></span>
                <span class="bcco-post-order"><?php echo $pos; ?>.</span>
                <span class="bcco-post-type-label"><?php echo esc_html(get_post_type_object(get_post_type($p))->labels->singular_name); ?></span>
                <a href="<?php echo get_edit_post_link($p->ID); ?>" class="bcco-post-title">
                    <?php echo esc_html($p->post_title); ?>
                </a>
                <span class="bcco-post-status">— <?php echo get_post_status_object(get_post_status($p->ID))->label; ?></span>
            </li>
            <?php
        endforeach;
        $html = ob_get_clean();

        $has_more = ($offset + $per_page) < $total;

        wp_send_json_success([
            'html'     => $html,
            'total'    => $total,
            'has_more' => $has_more,
            'offset'   => $offset + $per_page,
        ]);
    }

    public function get_counts() {
        check_ajax_referer('bcco_admin_nonce', 'nonce');
        if (!current_user_can('edit_posts')) {
            wp_send_json_error(__('No autorizado', 'bcco'));
        }

        global $wpdb;

        $series_ids = isset($_POST['series_ids']) ? array_map('intval', $_POST['series_ids']) : [];
        if (empty($series_ids)) wp_send_json_error();

        $post_types = bcco_get_post_types();
        $selected_pt = isset($_POST['post_type']) ? sanitize_key($_POST['post_type']) : '';
        if ($selected_pt && in_array($selected_pt, $post_types, true)) {
            $post_types = [$selected_pt];
        }

        $tt_ids = [];
        foreach ($series_ids as $sid) {
            $term = get_term($sid, 'collection');
            if ($term) $tt_ids[$sid] = $term->term_taxonomy_id;
        }

        if (empty($tt_ids)) wp_send_json_success([]);

        $tt_placeholders = implode(',', array_fill(0, count($tt_ids), '%d'));
        $pt_placeholders = implode(',', array_fill(0, count($post_types), '%s'));

        $sql = "SELECT tr.term_taxonomy_id, COUNT(DISTINCT tr.object_id) as cnt
                FROM {$wpdb->term_relationships} tr
                INNER JOIN {$wpdb->posts} p ON p.ID = tr.object_id
                WHERE tr.term_taxonomy_id IN ({$tt_placeholders})
                AND p.post_type IN ({$pt_placeholders})
                AND p.post_status IN ('publish','draft','pending','future','private')
                GROUP BY tr.term_taxonomy_id";

        $params = array_merge(array_values($tt_ids), $post_types);
        $results = $wpdb->get_results($wpdb->prepare($sql, $params));

        $counts = [];
        foreach ($results as $r) {
            $sid = array_search((int) $r->term_taxonomy_id, $tt_ids);
            if ($sid) $counts[$sid] = (int) $r->cnt;
        }

        wp_send_json_success($counts);
    }
}

new BCCO_Ajax_Handlers();
