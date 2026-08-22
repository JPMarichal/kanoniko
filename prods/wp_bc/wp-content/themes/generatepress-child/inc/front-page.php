<?php

add_filter('generate_sidebar_layout', function ($layout) {
  if (is_front_page() || is_category() || is_tag()) {
    return 'no-sidebar';
  }
  return $layout;
});

add_filter('body_class', function ($classes) {
  if (is_front_page() || is_category() || is_tag()) {
    $classes[] = 'no-sidebar';
    $classes = array_diff($classes, ['right-sidebar', 'left-sidebar', 'both-sidebars', 'both-right', 'both-left']);
  }
  return $classes;
});

add_filter('generate_show_title', function ($show) {
  if (is_front_page()) {
    return false;
  }
  return $show;
});

function bc_front_page_cat_color($term_id) {
  $colors = ['#1e73be', '#dd3333', '#dd9933', '#8224e3', '#1abc9c', '#e74c3c', '#3498db', '#2ecc71'];
  return $colors[$term_id % count($colors)];
}

function bc_front_page_cat_label($cat) {
  $color = bc_front_page_cat_color($cat->term_id);
  return '<span class="bc-fp-cat-label" style="background:' . esc_attr($color) . '">' . esc_html($cat->name) . '</span>';
}

function bc_front_page_exclude_ids() {
  static $ids = [];
  return $ids;
}

function bc_front_page_track_id($post_id) {
  $ids = &bc_front_page_exclude_ids();
  $ids[] = (int) $post_id;
}

// ── 1. Breaking News Ticker ──────────────────────

function bc_front_page_ticker() {
  $q = new WP_Query([
    'posts_per_page'      => 8,
    'ignore_sticky_posts' => true,
    'no_found_rows'       => true,
  ]);
  if (!$q->have_posts()) {
    return;
  }
  $posts = [];
  while ($q->have_posts()) {
    $q->the_post();
    $cats = get_the_category();
    $cat = !empty($cats) ? $cats[0] : null;
    $posts[] = [
      'title' => get_the_title(),
      'url'   => get_permalink(),
      'cat'   => $cat ? bc_front_page_cat_color($cat->term_id) : '',
    ];
  }
  wp_reset_postdata();
  ?>
  <div class="bc-fp-ticker-wrap">
    <span class="bc-fp-ticker-label"><i class="fas fa-bolt"></i> Últimas Noticias</span>
    <div class="bc-fp-ticker-track-wrap">
      <div class="bc-fp-ticker-track">
        <?php for ($i = 0; $i < 3; $i++) : ?>
          <?php foreach ($posts as $p) : ?>
            <span class="bc-fp-ticker-item">
              <a href="<?php echo esc_url($p['url']); ?>"><?php echo esc_html($p['title']); ?></a>
            </span>
          <?php endforeach; ?>
        <?php endfor; ?>
      </div>
    </div>
  </div>
  <?php
}

// ── 2. Featured Post ─────────────────────────────

function bc_front_page_featured_post() {
  $q = new WP_Query(['posts_per_page' => 1, 'ignore_sticky_posts' => true, 'no_found_rows' => true]);
  if (!$q->have_posts()) {
    return;
  }
  $q->the_post();
  bc_front_page_track_id(get_the_ID());
  $has_thumb = has_post_thumbnail();
  ?>
  <article class="bc-fp-featured">
    <a href="<?php the_permalink(); ?>" class="bc-fp-featured-link">
      <?php if ($has_thumb) : ?>
        <div class="bc-fp-featured-image-wrap">
          <img class="bc-fp-featured-image" src="<?php the_post_thumbnail_url('bc-hero'); ?>" alt="<?php the_title_attribute(); ?>" title="<?php the_title_attribute(); ?>" loading="eager">
          <div class="bc-fp-featured-overlay"></div>
        </div>
      <?php endif; ?>
      <div class="bc-fp-featured-body">
        <?php
        $cats = get_the_category();
        if (!empty($cats)) {
          echo bc_front_page_cat_label($cats[0]);
        }
        ?>
        <h2 class="bc-fp-featured-title"><?php the_title(); ?></h2>
        <p class="bc-fp-featured-excerpt"><?php echo wp_trim_words(get_the_excerpt() ?: get_the_content(), 25, '…'); ?></p>
        <div class="bc-fp-featured-meta">
          <span><?php echo get_the_date('j M, Y'); ?></span>
        </div>
      </div>
    </a>
  </article>
  <?php
  wp_reset_postdata();
}

// ── 3. Big Grid Style 1 (2-col: large left + 2 stacked right) ──

function bc_front_page_big_grid_1() {
  $exclude = bc_front_page_exclude_ids();
  $q = new WP_Query([
    'posts_per_page'      => 3,
    'post__not_in'        => $exclude,
    'ignore_sticky_posts' => true,
    'no_found_rows'       => true,
  ]);
  if (!$q->have_posts()) {
    return;
  }
  ?>
  <section class="bc-fp-section">
    <h2 class="bc-fp-section-title">En Portada</h2>
    <div class="bc-fp-big-grid-1">
      <?php
      $q->the_post();
      bc_front_page_track_id(get_the_ID());
      bc_front_page_big_grid_1_card('large');
      ?>
      <div class="bc-fp-bg1-stacked">
        <?php while ($q->have_posts()) : $q->the_post(); ?>
          <?php bc_front_page_track_id(get_the_ID()); ?>
          <?php bc_front_page_big_grid_1_card('small'); ?>
        <?php endwhile; ?>
      </div>
    </div>
  </section>
  <?php
  wp_reset_postdata();
}

function bc_front_page_big_grid_1_card($size) {
  $has_thumb = has_post_thumbnail();
  $cats = get_the_category();
  ?>
  <article class="bc-fp-bg1-card bc-fp-bg1-card--<?php echo $size; ?>">
    <a href="<?php the_permalink(); ?>">
      <?php if ($has_thumb) : ?>
        <div class="bc-fp-bg1-img-wrap">
          <img src="<?php the_post_thumbnail_url($size === 'large' ? 'bc-hero' : 'medium'); ?>" alt="<?php the_title_attribute(); ?>" title="<?php the_title_attribute(); ?>" loading="lazy">
          <div class="bc-fp-bg1-overlay"></div>
        </div>
      <?php endif; ?>
      <div class="bc-fp-bg1-body">
        <?php if (!empty($cats)) : ?>
          <?php echo bc_front_page_cat_label($cats[0]); ?>
        <?php endif; ?>
        <h3 class="bc-fp-bg1-title"><?php the_title(); ?></h3>
        <?php if ($size === 'large') : ?>
          <p class="bc-fp-bg1-excerpt"><?php echo wp_trim_words(get_the_excerpt() ?: get_the_content(), 18, '…'); ?></p>
        <?php endif; ?>
        <span class="bc-fp-bg1-date"><?php echo get_the_date('j M, Y'); ?></span>
      </div>
    </a>
  </article>
  <?php
}

// ── 4. Big Grid Style 2 (3-col equal with overlay) ──

function bc_front_page_big_grid_2() {
  $exclude = bc_front_page_exclude_ids();
  $exclude = array_merge($exclude, [0]);
  $temp_q = new WP_Query([
    'posts_per_page'      => 3,
    'post__not_in'        => $exclude,
    'ignore_sticky_posts' => true,
    'no_found_rows'       => true,
  ]);
  if (!$temp_q->have_posts()) {
    return;
  }
  ?>
  <section class="bc-fp-section">
    <h2 class="bc-fp-section-title">Destacado</h2>
    <div class="bc-fp-big-grid-2">
      <?php while ($temp_q->have_posts()) : $temp_q->the_post(); ?>
        <?php bc_front_page_track_id(get_the_ID()); ?>
        <article class="bc-fp-bg2-card">
          <a href="<?php the_permalink(); ?>">
            <?php if (has_post_thumbnail()) : ?>
              <div class="bc-fp-bg2-img-wrap">
                <img src="<?php the_post_thumbnail_url('medium'); ?>" alt="<?php the_title_attribute(); ?>" title="<?php the_title_attribute(); ?>" loading="lazy">
                <div class="bc-fp-bg2-overlay"></div>
              </div>
            <?php endif; ?>
            <div class="bc-fp-bg2-body">
              <?php
              $cats = get_the_category();
              if (!empty($cats)) {
                echo bc_front_page_cat_label($cats[0]);
              }
              ?>
              <h3 class="bc-fp-bg2-title"><?php the_title(); ?></h3>
              <span class="bc-fp-bg2-date"><?php echo get_the_date('j M, Y'); ?></span>
            </div>
          </a>
        </article>
      <?php endwhile; ?>
    </div>
  </section>
  <?php
  wp_reset_postdata();
}

// ── 5. "Don't Miss" Tabs ─────────────────────────

function bc_front_page_tabs() {
  $categories = get_categories([
    'hide_empty' => true,
    'orderby'    => 'count',
    'order'      => 'DESC',
    'number'     => 6,
  ]);
  if (empty($categories)) {
    return;
  }
  $tab_id = 'bc-fp-tabs-' . uniqid();
  $exclude = bc_front_page_exclude_ids();
  ?>
  <section class="bc-fp-section bc-fp-tabs-section" id="<?php echo $tab_id; ?>">
    <h2 class="bc-fp-section-title">No Te Pierdas</h2>
    <div class="bc-fp-tabs-nav">
      <?php foreach ($categories as $i => $cat) : ?>
        <button class="bc-fp-tab-btn <?php echo $i === 0 ? 'bc-fp-tab-active' : ''; ?>"
          data-category="<?php echo esc_attr($cat->term_id); ?>"
          data-target="<?php echo $tab_id; ?>"
          style="<?php echo $i === 0 ? '--tab-color:' . esc_attr(bc_front_page_cat_color($cat->term_id)) : ''; ?>">
          <?php echo esc_html($cat->name); ?>
        </button>
      <?php endforeach; ?>
    </div>
    <div class="bc-fp-tabs-panels">
      <?php foreach ($categories as $i => $cat) : ?>
        <?php
        $tab_q = new WP_Query([
          'posts_per_page'      => 5,
          'cat'                 => $cat->term_id,
          'post__not_in'        => $exclude,
          'ignore_sticky_posts' => true,
          'no_found_rows'       => true,
        ]);
        ?>
        <div class="bc-fp-tab-panel <?php echo $i === 0 ? 'bc-fp-tab-panel-active' : ''; ?>"
          data-category="<?php echo esc_attr($cat->term_id); ?>"
          data-parent="<?php echo $tab_id; ?>">
          <?php if ($tab_q->have_posts()) : ?>
            <?php
            $tab_q->the_post();
            bc_front_page_track_id(get_the_ID());
            $has_thumb = has_post_thumbnail();
            ?>
            <div class="bc-fp-tab-featured">
              <a href="<?php the_permalink(); ?>">
                <?php if ($has_thumb) : ?>
                  <img src="<?php the_post_thumbnail_url('medium'); ?>" alt="<?php the_title_attribute(); ?>" title="<?php the_title_attribute(); ?>" loading="lazy">
                <?php endif; ?>
                <h3 class="bc-fp-tab-feat-title"><?php the_title(); ?></h3>
              </a>
            </div>
            <ul class="bc-fp-tab-list">
              <?php while ($tab_q->have_posts()) : $tab_q->the_post(); ?>
                <?php bc_front_page_track_id(get_the_ID()); ?>
                <li>
                  <a href="<?php the_permalink(); ?>">
                    <span class="bc-fp-tab-list-title"><?php the_title(); ?></span>
                    <span class="bc-fp-tab-list-date"><?php echo get_the_date('j M, Y'); ?></span>
                  </a>
                </li>
              <?php endwhile; ?>
            </ul>
          <?php else : ?>
            <p class="bc-fp-tab-empty">No hay artículos en esta categoría.</p>
          <?php endif; ?>
          <?php wp_reset_postdata(); ?>
        </div>
      <?php endforeach; ?>
    </div>
  </section>
  <?php
}

// ── 6. Ad Slot ───────────────────────────────────

function bc_front_page_ad_slot($label = 'Publicidad') {
  ?>
  <div class="bc-fp-ad">
    <div class="bc-fp-ad-inner">
      <span class="bc-fp-ad-label">- <?php echo esc_html($label); ?> -</span>
      <div class="bc-fp-ad-placeholder">728 × 90</div>
    </div>
  </div>
  <?php
}

// ── 7. Latest Grid (existing, refined) ───────────

function bc_front_page_latest_grid() {
  $exclude = bc_front_page_exclude_ids();
  $q = new WP_Query([
    'posts_per_page'      => 6,
    'post__not_in'        => $exclude,
    'ignore_sticky_posts' => true,
    'no_found_rows'       => true,
  ]);
  if (!$q->have_posts()) {
    return;
  }
  ?>
  <section class="bc-fp-section">
    <h2 class="bc-fp-section-title">Últimos Artículos</h2>
    <div class="bc-fp-grid">
      <?php while ($q->have_posts()) : $q->the_post(); ?>
        <?php bc_front_page_track_id(get_the_ID()); ?>
        <article class="bc-fp-card">
          <a href="<?php the_permalink(); ?>" class="bc-fp-card-link">
            <?php if (has_post_thumbnail()) : ?>
              <div class="bc-fp-card-image-wrap">
                <img class="bc-fp-card-image" src="<?php the_post_thumbnail_url('medium'); ?>" alt="<?php the_title_attribute(); ?>" title="<?php the_title_attribute(); ?>" loading="lazy">
              </div>
            <?php endif; ?>
            <div class="bc-fp-card-body">
              <?php
              $cats = get_the_category();
              if (!empty($cats)) :
                echo bc_front_page_cat_label($cats[0]);
              endif;
              ?>
              <h3 class="bc-fp-card-title"><?php the_title(); ?></h3>
              <p class="bc-fp-card-date"><?php echo get_the_date('j M, Y'); ?></p>
            </div>
          </a>
        </article>
      <?php endwhile; ?>
    </div>
  </section>
  <?php
  wp_reset_postdata();
}

// ── 8. Category sections (existing) ──────────────

function bc_front_page_categories_posts() {
  $categories = get_categories([
    'hide_empty' => true,
    'orderby'    => 'count',
    'order'      => 'DESC',
    'number'     => 4,
  ]);
  if (empty($categories)) {
    return;
  }

  $exclude = bc_front_page_exclude_ids();
  foreach ($categories as $cat) :
    $cat_posts = new WP_Query([
      'posts_per_page'      => 4,
      'cat'                 => $cat->term_id,
      'post__not_in'        => $exclude,
      'ignore_sticky_posts' => true,
      'no_found_rows'       => true,
    ]);
    if (!$cat_posts->have_posts()) {
      continue;
    }
    $cat_color = bc_front_page_cat_color($cat->term_id);
    ?>
    <section class="bc-fp-section">
      <h2 class="bc-fp-section-title">
        <a href="<?php echo esc_url(get_category_link($cat->term_id)); ?>" style="color:<?php echo esc_attr($cat_color); ?>"><?php echo esc_html($cat->name); ?></a>
      </h2>
      <div class="bc-fp-cat-row">
        <?php
        $has_featured = false;
        while ($cat_posts->have_posts()) : $cat_posts->the_post();
          bc_front_page_track_id(get_the_ID());
          if (!$has_featured && has_post_thumbnail()) : $has_featured = true; ?>
            <article class="bc-fp-cat-featured">
              <a href="<?php the_permalink(); ?>">
                <?php the_post_thumbnail('medium', ['class' => 'bc-fp-cat-featured-image', 'loading' => 'lazy', 'title' => get_the_title()]); ?>
                <h3 class="bc-fp-cat-featured-title"><?php the_title(); ?></h3>
              </a>
            </article>
          <?php else : ?>
            <article class="bc-fp-cat-item">
              <a href="<?php the_permalink(); ?>">
                <h3 class="bc-fp-cat-item-title"><?php the_title(); ?></h3>
                <span class="bc-fp-cat-item-date"><?php echo get_the_date('j M, Y'); ?></span>
              </a>
            </article>
          <?php endif;
        endwhile; ?>
      </div>
    </section>
    <?php
    wp_reset_postdata();
  endforeach;
}

// ── Tabs JS (enqueue once) ───────────────────────

// ── Hook ticker to after_header for full-width ────

add_action('generate_after_header', function () {
  if (is_front_page()) {
    bc_front_page_ticker();
  }
});

add_action('wp_enqueue_scripts', function () {
  if (!is_front_page()) {
    return;
  }
  wp_add_inline_script('jquery', '
document.addEventListener("click", function(e) {
  var btn = e.target.closest(".bc-fp-tab-btn");
  if (!btn) return;
  var tabId = btn.getAttribute("data-target");
  var cat   = btn.getAttribute("data-category");
  var container = document.getElementById(tabId);
  if (!container) return;
  container.querySelectorAll(".bc-fp-tab-btn").forEach(function(b) {
    b.classList.remove("bc-fp-tab-active");
    b.style.setProperty("--tab-color", "");
  });
  btn.classList.add("bc-fp-tab-active");
  btn.style.setProperty("--tab-color", getComputedStyle(btn).getPropertyValue("--tab-color") || "#1e73be");
  container.querySelectorAll(".bc-fp-tab-panel").forEach(function(p) {
    p.classList.remove("bc-fp-tab-panel-active");
  });
  var panel = container.querySelector(".bc-fp-tab-panel[data-category=\"" + cat + "\"]");
  if (panel) panel.classList.add("bc-fp-tab-panel-active");
});
');
}, 100);
