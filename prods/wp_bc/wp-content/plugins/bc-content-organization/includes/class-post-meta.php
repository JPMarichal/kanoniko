<?php

class BCCO_Post_Meta {

    public function __construct() {
        add_action('add_meta_boxes', [$this, 'add_meta_box']);
        add_action('save_post', [$this, 'save_meta_box']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_assets']);
    }

    public function enqueue_assets($hook) {
        if (!in_array($hook, ['post.php', 'post-new.php'])) return;
        if (!in_array(get_post_type(), bcco_get_post_types())) return;

        wp_enqueue_style('bcco-admin', BCCO_PLUGIN_URL . 'assets/css/admin.css', [], '1.0.0');
    }

    public function add_meta_box() {
        foreach (bcco_get_post_types() as $pt) {
            add_meta_box(
                'bcco_series_meta',
                __('Serie y posición', 'bcco'),
                [$this, 'render_meta_box'],
                $pt,
                'side',
                'high'
            );
        }
    }

    public function render_meta_box($post) {
        wp_nonce_field('bcco_series_meta', 'bcco_series_meta_nonce');

        $collections = get_terms([
            'taxonomy'   => 'collection',
            'hide_empty' => false,
            'parent'     => 0,
        ]);

        $assigned_terms = wp_get_post_terms($post->ID, 'collection');
        $current_term = !empty($assigned_terms) ? $assigned_terms[0] : null;
        $current_position = (int) get_post_meta($post->ID, '_series_position', true);

        if ($current_position < 1 && $current_term) {
            $siblings = get_posts([
                'post_type'      => bcco_get_post_types(),
                'numberposts'    => 1,
                'post__not_in'   => [$post->ID],
                'tax_query'      => [[
                    'taxonomy' => 'collection',
                    'field'    => 'term_id',
                    'terms'    => $current_term->term_id,
                ]],
                'meta_key'       => '_series_position',
                'orderby'        => 'meta_value_num',
                'order'          => 'DESC',
                'fields'         => 'ids',
            ]);
            if (!empty($siblings)) {
                $current_position = (int) get_post_meta($siblings[0], '_series_position', true) + 1;
            } else {
                $current_position = 1;
            }
        }
        ?>
        <p>
            <label for="bcco_collection"><?php _e('Colección:', 'bcco'); ?></label>
            <select name="bcco_collection" id="bcco_collection" style="width:100%;margin-top:4px;">
                <option value=""><?php _e('— Seleccionar —', 'bcco'); ?></option>
                <?php foreach ($collections as $col) : ?>
                    <option value="<?php echo $col->term_id; ?>" 
                        <?php selected($current_term && $current_term->parent === $col->term_id, true); ?>>
                        <?php echo esc_html($col->name); ?>
                    </option>
                <?php endforeach; ?>
            </select>
        </p>
        <p>
            <label for="bcco_series"><?php _e('Serie:', 'bcco'); ?></label>
            <select name="bcco_series" id="bcco_series" style="width:100%;margin-top:4px;">
                <option value=""><?php _e('— Sin serie —', 'bcco'); ?></option>
            </select>
        </p>
        <p>
            <label for="bcco_position"><?php _e('Posición:', 'bcco'); ?></label>
            <input type="number" name="bcco_position" id="bcco_position"
                   value="<?php echo esc_attr($current_position); ?>"
                   min="1" step="1" style="width:80px;margin-top:4px;">
        </p>
        <script>
        jQuery(document).ready(function($) {
            var seriesData = <?php echo json_encode($this->get_series_tree()); ?>;
            var currentSeriesId = <?php echo $current_term ? (int) $current_term->term_id : 'null'; ?>;
            var currentCollectionId = <?php echo $current_term && $current_term->parent ? (int) $current_term->parent : 'null'; ?>;

            function populateSeries(collectionId) {
                var $sel = $('#bcco_series');
                $sel.empty().append('<option value=""><?php _e('— Sin serie —', 'bcco'); ?></option>');
                if (collectionId && seriesData[collectionId]) {
                    seriesData[collectionId].forEach(function(s) {
                        var $opt = $('<option>').val(s.term_id).text(s.name);
                        if (currentSeriesId && parseInt(s.term_id) === currentSeriesId) {
                            $opt.prop('selected', true);
                        }
                        $sel.append($opt);
                    });
                }
            }

            if (currentCollectionId) {
                $('#bcco_collection').val(currentCollectionId);
                populateSeries(currentCollectionId);
            }

            $('#bcco_collection').on('change', function() {
                populateSeries($(this).val());
            });
        });
        </script>
        <?php
    }

    private function get_series_tree() {
        $collections = get_terms([
            'taxonomy'   => 'collection',
            'hide_empty' => false,
            'parent'     => 0,
        ]);

        $tree = [];
        foreach ($collections as $col) {
            $children = get_terms([
                'taxonomy'   => 'collection',
                'hide_empty' => false,
                'parent'     => $col->term_id,
            ]);
            if (!empty($children)) {
                $tree[$col->term_id] = array_map(function($t) {
                    return ['term_id' => $t->term_id, 'name' => $t->name];
                }, $children);
            } else {
                $tree[$col->term_id] = [];
            }
        }
        return $tree;
    }

    public function save_meta_box($post_id) {
        if (!isset($_POST['bcco_series_meta_nonce'])) return;
        if (!wp_verify_nonce($_POST['bcco_series_meta_nonce'], 'bcco_series_meta')) return;
        if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) return;
        if (!current_user_can('edit_post', $post_id)) return;

        $series_term_id = isset($_POST['bcco_series']) ? intval($_POST['bcco_series']) : 0;

        if ($series_term_id > 0) {
            wp_set_post_terms($post_id, [$series_term_id], 'collection');
        } else {
            wp_set_post_terms($post_id, [], 'collection');
        }

        if (isset($_POST['bcco_position']) && $_POST['bcco_position'] !== '') {
            $position = intval($_POST['bcco_position']);
        } else {
            $position = 0;
        }

        if ($position < 1 && $series_term_id > 0) {
            $existing = get_posts([
                'post_type'      => bcco_get_post_types(),
                'numberposts'    => 1,
                'post__not_in'   => [$post_id],
                'tax_query'      => [[
                    'taxonomy' => 'collection',
                    'field'    => 'term_id',
                    'terms'    => $series_term_id,
                ]],
                'meta_key'       => '_series_position',
                'orderby'        => 'meta_value_num',
                'order'          => 'DESC',
                'fields'         => 'ids',
            ]);

            if (!empty($existing)) {
                $max_pos = (int) get_post_meta($existing[0], '_series_position', true);
                $position = $max_pos + 1;
            } else {
                $position = 1;
            }
        }

        update_post_meta($post_id, '_series_position', $position);
    }
}

new BCCO_Post_Meta();
