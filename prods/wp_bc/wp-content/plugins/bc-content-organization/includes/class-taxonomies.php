<?php

class BCCO_Taxonomies {

    private $nesting_notice_flagged = false;

    public function __construct() {
        add_action('init', [$this, 'register_taxonomy']);
        add_action('init', [$this, 'register_meta_fields']);
        add_filter('manage_collection_custom_column', [$this, 'custom_column_content'], 10, 3);
        add_filter('manage_edit-collection_columns', [$this, 'custom_columns']);

        add_filter('pre_insert_term', [$this, 'validate_before_insert'], 10, 2);
        add_filter('wp_insert_term_data', [$this, 'fix_nesting_on_insert'], 10, 3);
        add_filter('wp_update_term_data', [$this, 'fix_nesting_on_update'], 10, 4);
        add_filter('redirect_term_location', [$this, 'catch_nesting_notice'], 10, 2);
        add_action('admin_notices', [$this, 'render_nesting_notice']);

        add_action('collection_pre_add_form', [$this, 'render_instructions']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_term_assets']);
        add_filter('taxonomy_parent_dropdown_args', [$this, 'filter_parent_dropdown'], 10, 3);
        add_action('created_collection', [$this, 'assign_series_order_on_create'], 10, 2);
    }

    public function register_taxonomy() {
        $labels = [
            'name'              => __('Colecciones y Series', 'bcco'),
            'singular_name'     => __('Colección/Serie', 'bcco'),
            'search_items'      => __('Buscar', 'bcco'),
            'all_items'         => __('Todas las colecciones', 'bcco'),
            'parent_item'       => __('Colección padre', 'bcco'),
            'parent_item_colon' => __('Colección padre:', 'bcco'),
            'edit_item'         => __('Editar', 'bcco'),
            'update_item'       => __('Actualizar', 'bcco'),
            'add_new_item'      => __('Añadir nueva colección', 'bcco'),
            'new_item_name'     => __('Nueva colección', 'bcco'),
            'menu_name'         => __('Colecciones', 'bcco'),
        ];

        register_taxonomy('collection', bcco_get_post_types(), [
            'labels'            => $labels,
            'hierarchical'      => true,
            'public'            => true,
            'show_ui'           => true,
            'show_admin_column' => true,
            'show_in_menu'      => true,
            'show_in_nav_menus' => false,
            'show_in_rest'      => true,
            'rewrite'           => ['slug' => 'coleccion'],
            'capabilities'      => [
                'manage_terms' => 'manage_categories',
                'edit_terms'   => 'manage_categories',
                'delete_terms' => 'manage_categories',
                'assign_terms' => 'edit_posts',
            ],
        ]);
    }

    public function register_meta_fields() {
        register_post_meta('', '_series_position', [
            'type'         => 'integer',
            'description'  => 'Posición del post dentro de su serie',
            'single'       => true,
            'default'      => 0,
            'show_in_rest' => true,
        ]);

        register_term_meta('collection', '_series_order', [
            'type'         => 'integer',
            'description'  => 'Orden de la serie dentro de la colección',
            'single'       => true,
            'default'      => 0,
            'show_in_rest' => true,
        ]);
    }

    public function custom_columns($columns) {
        $columns['type'] = __('Tipo', 'bcco');
        return $columns;
    }

    public function custom_column_content($content, $column_name, $term_id) {
        if ($column_name === 'type') {
            $parent = wp_get_term_taxonomy_parent_id($term_id, 'collection');
            if ($parent) {
                $content = '<span style="color:#2271b1;">' . __('Serie', 'bcco') . '</span>';
            } else {
                $content = '<span style="color:#46b450;">' . __('Colección', 'bcco') . '</span>';
            }
        }
        return $content;
    }

    public function filter_parent_dropdown($args, $taxonomy, $action) {
        if ($taxonomy !== 'collection') return $args;

        $all = get_terms([
            'taxonomy'   => 'collection',
            'hide_empty' => false,
            'fields'     => 'id=>parent',
        ]);

        $series_ids = [];
        foreach ($all as $id => $parent) {
            if ($parent > 0) {
                $series_ids[] = $id;
            }
        }

        $args['exclude'] = $series_ids;
        $args['show_option_none'] = __('— Ninguna (es una Colección) —', 'bcco');
        $args['option_none_value'] = '';

        return $args;
    }

    public function render_instructions() {
        $screen = get_current_screen();
        if (!$screen || $screen->taxonomy !== 'collection') return;
        ?>
        <div class="notice bcco-instructions">
            <h3><?php _e('Instrucciones', 'bcco'); ?></h3>
            <p><?php _e('Aquí puedes crear y organizar <strong>Colecciones</strong> y <strong>Series</strong> para agrupar tus artículos.', 'bcco'); ?></p>
            <ol>
                <li><?php _e('Para crear una <strong>Colección</strong> (agrupa series): escribe el nombre y haz clic en "Añadir nueva colección". Deja "Colección padre" en <em>"— Ninguna (es una Colección) —"</em>.', 'bcco'); ?></li>
                <li><?php _e('Para crear una <strong>Serie</strong> (agrupa artículos) dentro de una colección: escribe el nombre y selecciona en "Colección padre" a qué colección pertenece. Las series no pueden tener hijos.', 'bcco'); ?></li>
                <li><?php _e('Para <strong>convertir una Serie en Colección</strong>: edita la serie y cambia "Colección padre" a <em>"— Ninguna (es una Colección) —"</em>. Los artículos se conservan.', 'bcco'); ?></li>
            </ol>
            <p>
                <?php _e('Después de crear, ve a', 'bcco'); ?>
                <a href="<?php echo admin_url('edit.php?page=bcco-organize'); ?>"><?php _e('Posts → Organizar series', 'bcco'); ?></a>
                <?php _e('para ordenar las series y los artículos con arrastrar y soltar.', 'bcco'); ?>
            </p>
        </div>
        <?php
    }

    public function enqueue_term_assets($hook) {
        if ($hook !== 'edit-tags.php' && $hook !== 'term.php') return;
        $screen = get_current_screen();
        if (!$screen || $screen->taxonomy !== 'collection') return;

        wp_enqueue_style('bcco-admin', BCCO_PLUGIN_URL . 'assets/css/admin.css', [], '1.0.0');

        wp_enqueue_script('bcco-term-validation', BCCO_PLUGIN_URL . 'assets/js/admin.js', ['jquery'], '1.0.0', true);
        wp_localize_script('bcco-term-validation', 'bcco_term', [
            'msg_collection' => __('Esto será una <strong>Colección</strong>. Las colecciones agrupan series.', 'bcco'),
            'msg_series'     => __('Esto será una <strong>Serie</strong>. Las series agrupan artículos y no pueden tener hijos.', 'bcco'),
        ]);
    }

    public function validate_before_insert($term, $taxonomy) {
        if ($taxonomy !== 'collection') return $term;
        if (!isset($_POST['parent']) || $_POST['parent'] === '') return $term;

        $parent_id = (int) $_POST['parent'];
        if ($parent_id <= 0) return $term;

        $parent = get_term($parent_id, 'collection');
        if ($parent && $parent->parent > 0) {
            return new WP_Error(
                'bcco_deep_nesting',
                __('Error: No se puede crear una sub-serie. La jerarquía máxima es Colección → Serie.', 'bcco')
            );
        }

        return $term;
    }

    public function fix_nesting_on_insert($data, $taxonomy, $args) {
        if ($taxonomy !== 'collection' || empty($data['parent'])) return $data;

        $parent = get_term($data['parent'], 'collection');
        if ($parent && $parent->parent > 0) {
            $data['parent'] = 0;
            $this->nesting_notice_flagged = true;
        }

        return $data;
    }

    public function fix_nesting_on_update($data, $term_id, $taxonomy, $args) {
        if ($taxonomy !== 'collection' || empty($data['parent'])) return $data;

        $parent = get_term($data['parent'], 'collection');
        if ($parent && $parent->parent > 0) {
            $data['parent'] = 0;
            $this->nesting_notice_flagged = true;
        }

        return $data;
    }

    public function catch_nesting_notice($location, $term_id) {
        if ($this->nesting_notice_flagged) {
            $location = add_query_arg('bcco_error', 'deep_nesting', $location);
        }
        return $location;
    }

    public function render_nesting_notice() {
        if (!isset($_GET['bcco_error']) || $_GET['bcco_error'] !== 'deep_nesting') return;
        ?>
        <div class="notice notice-warning is-dismissible">
            <p>
                <?php _e('La serie seleccionada como padre ya pertenece a una colección. No se permiten sub-series. El término se ha guardado como colección (nivel raíz).', 'bcco'); ?>
            </p>
        </div>
        <?php
    }

    public function assign_series_order_on_create($term_id, $tt_id) {
        $term = get_term($term_id, 'collection');
        if (!$term || $term->parent <= 0) return;

        $existing = get_term_meta($term_id, '_series_order', true);
        if ($existing !== '' && $existing !== false) return;

        $siblings = get_terms([
            'taxonomy'   => 'collection',
            'hide_empty' => false,
            'parent'     => $term->parent,
            'fields'     => 'ids',
        ]);

        $max = 0;
        foreach ($siblings as $sid) {
            $o = (int) get_term_meta($sid, '_series_order', true);
            if ($o > $max) $max = $o;
        }

        update_term_meta($term_id, '_series_order', $max + 1);
    }
}

new BCCO_Taxonomies();
