<?php

class BCCO_Frontend_Widget extends WP_Widget {

    public function __construct() {
        parent::__construct(
            'bcco_series_widget',
            __('Navegación de Serie', 'bcco'),
            [
                'description' => __('Muestra la serie y colección del artículo actual con navegación entre artículos de la misma serie.', 'bcco'),
            ]
        );
    }

    public function widget($args, $instance) {
        $post_types = bcco_get_post_types();
        if (!is_singular($post_types)) return;

        global $post;

        $terms = wp_get_post_terms($post->ID, 'collection');
        if (empty($terms) || is_wp_error($terms)) return;

        $series = $terms[0];
        $collection = $series->parent > 0 ? get_term($series->parent, 'collection') : null;
        if (!$collection || is_wp_error($collection)) return;

        $series_posts = get_posts([
            'post_type'      => $post_types,
            'numberposts'    => -1,
            'tax_query'      => [[
                'taxonomy' => 'collection',
                'field'    => 'term_id',
                'terms'    => $series->term_id,
            ]],
            'meta_key'       => '_series_position',
            'orderby'        => 'meta_value_num',
            'order'          => 'ASC',
        ]);

        $current_pos = (int) get_post_meta($post->ID, '_series_position', true);
        $total = count($series_posts);

        $collection_link = get_term_link($collection);
        $series_link = get_term_link($series);

        echo $args['before_widget'];
        ?>

        <div class="bcco-widget">
            <p class="bcco-collection-name">
                <a href="<?php echo esc_url($collection_link); ?>">
                    <i class="fas fa-folder-open"></i> <?php echo esc_html($collection->name); ?>
                </a>
            </p>

            <p class="bcco-series-name">
                <a href="<?php echo esc_url($series_link); ?>">
                    <i class="fas fa-book-open"></i> <?php echo esc_html($series->name); ?>
                </a>
            </p>

            <p class="bcco-progress">
                <?php printf(__('Artículo %d de %d', 'bcco'), $current_pos, $total); ?>
            </p>

            <ol class="bcco-post-list">
                <?php foreach ($series_posts as $sp) :
                    $pos = (int) get_post_meta($sp->ID, '_series_position', true);
                    $is_current = ($sp->ID === $post->ID);
                    ?>
                    <li class="bcco-post-item <?php echo $is_current ? 'bcco-current' : ''; ?>">
                        <?php if ($is_current) : ?>
                            <i class="fas fa-chevron-circle-right"></i>
                            <span><?php echo esc_html($sp->post_title); ?></span>
                        <?php else : ?>
                            <a href="<?php echo get_permalink($sp->ID); ?>">
                                <i class="far fa-file-alt"></i> <?php echo esc_html($sp->post_title); ?>
                            </a>
                        <?php endif; ?>
                    </li>
                <?php endforeach; ?>
            </ol>

            <div class="bcco-nav-links">
                <?php
                $prev = null;
                $next = null;
                foreach ($series_posts as $i => $sp) {
                    if ($sp->ID === $post->ID) {
                        if (isset($series_posts[$i - 1])) $prev = $series_posts[$i - 1];
                        if (isset($series_posts[$i + 1])) $next = $series_posts[$i + 1];
                        break;
                    }
                }
                ?>
                <?php if ($prev) : ?>
                    <span class="bcco-nav bcco-prev">
                        <a href="<?php echo get_permalink($prev->ID); ?>">
                            <i class="fas fa-arrow-left"></i> <?php _e('Anterior', 'bcco'); ?>
                        </a>
                    </span>
                <?php endif; ?>
                <?php if ($next) : ?>
                    <span class="bcco-nav bcco-next">
                        <a href="<?php echo get_permalink($next->ID); ?>">
                            <?php _e('Siguiente', 'bcco'); ?> <i class="fas fa-arrow-right"></i>
                        </a>
                    </span>
                <?php endif; ?>
                <div class="bcco-clear"></div>
            </div>
        </div>

        <?php
        echo $args['after_widget'];
    }

    public function form($instance) {
        ?>
        <p><?php _e('Este widget muestra la serie y colección del artículo actual, con navegación entre artículos de la misma serie.', 'bcco'); ?></p>
        <?php
    }
}

add_action('widgets_init', function() {
    register_widget('BCCO_Frontend_Widget');
});
