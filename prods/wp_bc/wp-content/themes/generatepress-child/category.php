<?php get_header(); ?>

<main id="main" class="bc-cat-archive">
  <div class="grid-container">
    <header class="bc-cat-archive-header">
      <?php the_archive_title('<h1 class="bc-cat-archive-title">', '</h1>'); ?>
      <?php the_archive_description('<div class="bc-cat-archive-desc">', '</div>'); ?>
    </header>

    <?php if (have_posts()) : ?>
      <div class="row row-cols-1 row-cols-sm-2 row-cols-lg-3 g-4">
        <?php while (have_posts()) : the_post(); ?>
          <div class="col">
            <article class="bc-cat-card">
              <a href="<?php the_permalink(); ?>" class="bc-cat-card-link">
                <?php if (has_post_thumbnail()) : ?>
                  <div class="bc-cat-card-img-wrap">
                    <img class="bc-cat-card-img" src="<?php the_post_thumbnail_url('medium'); ?>" alt="<?php the_title_attribute(); ?>" title="<?php the_title_attribute(); ?>" loading="lazy">
                  </div>
                <?php endif; ?>
                <div class="bc-cat-card-body">
                  <h2 class="bc-cat-card-title"><?php the_title(); ?></h2>
                  <p class="bc-cat-card-excerpt"><?php echo wp_trim_words(get_the_excerpt() ?: get_the_content(), 20, '…'); ?></p>
                  <span class="bc-cat-card-date"><?php echo get_the_date('j M, Y'); ?></span>
                </div>
              </a>
            </article>
          </div>
        <?php endwhile; ?>
      </div>

      <nav class="bc-cat-pagination">
        <?php echo paginate_links(); ?>
      </nav>

    <?php else : ?>
      <p class="bc-cat-empty">No se encontraron artículos en esta categoría.</p>
    <?php endif; ?>
  </div>
</main>

<?php get_footer(); ?>
