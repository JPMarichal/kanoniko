<?php

class BCCO_Admin_Page {

    public function __construct() {
        add_action('admin_menu', [$this, 'add_admin_page']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_assets']);
    }

    public function add_admin_page() {
        $hook = add_submenu_page(
            'edit.php',
            __('Organizar Colecciones y Series', 'bcco'),
            __('Organizar series', 'bcco'),
            'manage_categories',
            'bcco-organize',
            [$this, 'render_admin_page']
        );
    }

    public function enqueue_assets($hook) {
        if (strpos($hook, 'bcco-organize') === false) return;

        wp_enqueue_style('bcco-admin', BCCO_PLUGIN_URL . 'assets/css/admin.css', [], '1.0.0');
        wp_enqueue_script('jquery-ui-sortable');
        wp_enqueue_script('bcco-admin', BCCO_PLUGIN_URL . 'assets/js/admin.js', ['jquery', 'jquery-ui-sortable'], '1.0.0', true);
        wp_localize_script('bcco-admin', 'bcco_admin', [
            'ajax_url'  => admin_url('admin-ajax.php'),
            'nonce'     => wp_create_nonce('bcco_admin_nonce'),
            'post_types' => $this->get_post_type_options(),
            'selected_pt' => isset($_GET['ptype']) ? sanitize_key($_GET['ptype']) : '',
            'per_page'  => 20,
            'strings'   => [
                'empty_series'   => __('No hay series en esta colección.', 'bcco'),
                'no_posts'       => __('Sin artículos', 'bcco'),
                'saved'          => __('Guardado', 'bcco'),
                'error'          => __('Error al guardar el orden. Intente de nuevo.', 'bcco'),
                'loading'        => __('Cargando…', 'bcco'),
                'load_more'      => __('Cargar más', 'bcco'),
                'all_types'      => __('Todos los tipos', 'bcco'),
                'search_placeholder' => __('Buscar artículos…', 'bcco'),
                'series_count'   => __('%d series', 'bcco'),
            ],
        ]);
    }

    private function get_post_type_options() {
        $options = [];
        $options[''] = __('Todos los tipos', 'bcco');
        foreach (bcco_get_post_types() as $pt) {
            $pto = get_post_type_object($pt);
            $options[$pt] = $pto ? $pto->labels->singular_name : $pt;
        }
        return $options;
    }

    public function render_admin_page() {
        $selected_pt = isset($_GET['ptype']) ? sanitize_key($_GET['ptype']) : '';

        $collections = get_terms([
            'taxonomy'   => 'collection',
            'hide_empty' => false,
            'parent'     => 0,
        ]);
        ?>
        <div class="wrap">
            <h1><?php _e('Organizar Colecciones y Series', 'bcco'); ?></h1>

            <div class="bcco-toolbar">
                <select id="bcco-filter-ptype">
                    <?php foreach ($this->get_post_type_options() as $val => $label) : ?>
                        <option value="<?php echo esc_attr($val); ?>" <?php selected($selected_pt, $val); ?>><?php echo esc_html($label); ?></option>
                    <?php endforeach; ?>
                </select>
                <input type="text" id="bcco-global-search" placeholder="<?php esc_attr_e('Buscar series o artículos…', 'bcco'); ?>">
                <span class="bcco-toolbar-desc"><?php _e('Arrastre y suelte para reordenar. Los cambios se guardan automáticamente.', 'bcco'); ?></span>
            </div>

            <?php if (empty($collections)) : ?>
                <div class="notice notice-info">
                    <p><?php _e('Aún no hay colecciones. Vaya a <a href="' . admin_url('edit-tags.php?taxonomy=collection&post_type=post') . '">Colecciones</a> para crear la primera.', 'bcco'); ?></p>
                </div>
            <?php endif; ?>

            <div id="bcco-collections-container">
                <?php foreach ($collections as $collection) :
                    $series_list = get_terms([
                        'taxonomy'   => 'collection',
                        'hide_empty' => false,
                        'parent'     => $collection->term_id,
                    ]);
                    usort($series_list, function($a, $b) {
                        $oa = (int) get_term_meta($a->term_id, '_series_order', true);
                        $ob = (int) get_term_meta($b->term_id, '_series_order', true);
                        return $oa - $ob;
                    });
                    $series_counts = $this->get_batch_counts($series_list, $selected_pt);
                    ?>
                    <div class="bcco-collection" data-collection-id="<?php echo $collection->term_id; ?>">
                        <div class="bcco-collection-header bcco-toggle-coll">
                            <span class="dashicons dashicons-arrow-right bcco-toggle-icon"></span>
                            <span class="dashicons dashicons-category"></span>
                            <h2><?php echo esc_html($collection->name); ?></h2>
                            <span class="bcco-series-total"><?php printf(__('%d series', 'bcco'), count($series_list)); ?></span>
                            <a href="<?php echo admin_url('term.php?taxonomy=collection&tag_ID=' . $collection->term_id . '&post_type=post'); ?>" class="bcco-edit-link" title="<?php esc_attr_e('Editar colección', 'bcco'); ?>">
                                <span class="dashicons dashicons-edit"></span>
                            </a>
                        </div>

                        <div class="bcco-collection-body" style="display:none;">
                            <?php if (empty($series_list)) : ?>
                                <p class="bcco-empty"><?php _e('No hay series en esta colección.', 'bcco'); ?></p>
                            <?php else : ?>
                                <ul class="bcco-series-list">
                                    <?php $series_index = 0;
                                    foreach ($series_list as $series) :
                                        $series_index++;
                                        $count = isset($series_counts[$series->term_id]) ? $series_counts[$series->term_id] : 0;
                                        ?>
                                        <li class="bcco-series" id="bcco-series-<?php echo $series->term_id; ?>" data-series-id="<?php echo $series->term_id; ?>"
                                            data-loaded="false" data-offset="0" data-total="<?php echo $count; ?>">
                                            <div class="bcco-series-header bcco-toggle-series">
                                                <span class="bcco-series-handle dashicons dashicons-menu"></span>
                                                <span class="bcco-series-order"><?php echo $series_index; ?>.</span>
                                                <span class="dashicons dashicons-arrow-right bcco-series-toggle-icon"></span>
                                                <span class="dashicons dashicons-book-alt"></span>
                                                <strong><?php echo esc_html($series->name); ?></strong>
                                                <span class="bcco-series-count"><?php echo $count ? sprintf(__('%d artículos', 'bcco'), $count) : '—'; ?></span>
                                                <span class="bcco-loading-spinner" style="display:none;">
                                                    <span class="spinner" style="float:none;margin:0;"></span>
                                                </span>
                                                <a href="<?php echo admin_url('term.php?taxonomy=collection&tag_ID=' . $series->term_id . '&post_type=post'); ?>" class="bcco-edit-link" title="<?php esc_attr_e('Editar serie', 'bcco'); ?>">
                                                    <span class="dashicons dashicons-edit"></span>
                                                </a>
                                            </div>
                                            <div class="bcco-series-body" style="display:none;">
                                                <ul class="bcco-posts-list"></ul>
                                                <p class="bcco-load-more" style="display:none;">
                                                    <button class="button"><?php _e('Cargar más', 'bcco'); ?></button>
                                                </p>
                                            </div>
                                        </li>
                                    <?php endforeach; ?>
                                </ul>
                            <?php endif; ?>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
        <?php
    }

    private function get_batch_counts($series_list, $selected_pt = '') {
        global $wpdb;

        $tt_ids = [];
        foreach ($series_list as $s) {
            $term = get_term($s->term_id, 'collection');
            if ($term) $tt_ids[$s->term_id] = $term->term_taxonomy_id;
        }
        if (empty($tt_ids)) return [];

        $post_types = bcco_get_post_types();
        if ($selected_pt && in_array($selected_pt, $post_types, true)) {
            $post_types = [$selected_pt];
        }

        $tt_ph = implode(',', array_fill(0, count($tt_ids), '%d'));
        $pt_ph = implode(',', array_fill(0, count($post_types), '%s'));

        $sql = "SELECT tr.term_taxonomy_id, COUNT(DISTINCT tr.object_id) as cnt
                FROM {$wpdb->term_relationships} tr
                INNER JOIN {$wpdb->posts} p ON p.ID = tr.object_id
                WHERE tr.term_taxonomy_id IN ({$tt_ph})
                AND p.post_type IN ({$pt_ph})
                AND p.post_status IN ('publish','draft','pending','future','private')
                GROUP BY tr.term_taxonomy_id";

        $params = array_merge(array_values($tt_ids), $post_types);
        $results = $wpdb->get_results($wpdb->prepare($sql, $params));

        $counts = [];
        foreach ($results as $r) {
            $sid = array_search((int) $r->term_taxonomy_id, $tt_ids);
            if ($sid) $counts[$sid] = (int) $r->cnt;
        }
        return $counts;
    }
}

new BCCO_Admin_Page();
