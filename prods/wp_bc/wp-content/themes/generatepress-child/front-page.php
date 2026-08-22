<?php get_header(); ?>

<div class="bc-front-page">
  <?php bc_front_page_featured_post(); ?>

  <?php bc_front_page_ad_slot(); ?>

  <?php bc_front_page_big_grid_1(); ?>

  <?php bc_front_page_ad_slot('Publicidad'); ?>

  <?php bc_front_page_tabs(); ?>

  <?php bc_front_page_ad_slot('Publicidad'); ?>

  <?php bc_front_page_big_grid_2(); ?>

  <?php bc_front_page_latest_grid(); ?>

  <?php bc_front_page_ad_slot('Publicidad'); ?>

  <?php bc_front_page_categories_posts(); ?>
</div>

<?php get_footer(); ?>
