<?php

function bc_render_share_bar( $modifier = '' ) {
  if ( ! has_post_thumbnail() || ! is_singular() ) {
    return;
  }

  $bc_url    = urlencode( get_permalink() );
  $bc_title  = urlencode( html_entity_decode( is_singular( 'bc_quote_author' ) ? bc_persona_biography_title() : get_the_title(), ENT_QUOTES, 'UTF-8' ) );
  $bc_image  = rawurlencode( get_the_post_thumbnail_url( get_the_ID(), 'full' ) );
  $class     = $modifier ? 'page-share-bar page-share-bar--' . $modifier : 'page-share-bar';
  ?>
  <div class="<?php echo $class; ?>">
    <span class="page-share-label"><?php echo is_singular( 'bc_quote_author' ) ? 'Comparte esta biografía' : 'Comparte este artículo'; ?>:</span>
    <a href="https://www.facebook.com/sharer/sharer.php?u=<?php echo $bc_url; ?>" target="_blank" rel="noopener" class="page-share-link share-facebook" aria-label="Facebook"><i class="fab fa-facebook-f"></i></a>
    <a href="https://twitter.com/intent/tweet?url=<?php echo $bc_url; ?>&text=<?php echo $bc_title; ?>" target="_blank" rel="noopener" class="page-share-link share-twitter" aria-label="Twitter"><i class="fab fa-x-twitter"></i></a>
    <a href="https://wa.me/?text=<?php echo $bc_url; ?>" target="_blank" rel="noopener" class="page-share-link share-whatsapp" aria-label="WhatsApp"><i class="fab fa-whatsapp"></i></a>
    <a href="https://t.me/share/url?url=<?php echo $bc_url; ?>&text=<?php echo $bc_title; ?>" target="_blank" rel="noopener" class="page-share-link share-telegram" aria-label="Telegram"><i class="fab fa-telegram"></i></a>
    <a href="https://www.threads.net/intent/post?text=<?php echo $bc_title . '%20' . $bc_url; ?>" target="_blank" rel="noopener" class="page-share-link share-threads" aria-label="Threads"><i class="fab fa-threads"></i></a>
    <a href="https://www.facebook.com/dialog/send?display=popup&link=<?php echo $bc_url; ?>&redirect_uri=<?php echo $bc_url; ?>" target="_blank" rel="noopener" class="page-share-link share-messenger" aria-label="Messenger"><i class="fab fa-facebook-messenger"></i></a>
    <a href="https://www.reddit.com/submit?url=<?php echo $bc_url; ?>&title=<?php echo $bc_title; ?>" target="_blank" rel="noopener" class="page-share-link share-reddit" aria-label="Reddit"><i class="fab fa-reddit-alien"></i></a>
    <a href="https://pinterest.com/pin/create/button/?url=<?php echo $bc_url; ?>&media=<?php echo $bc_image; ?>&description=<?php echo $bc_title; ?>" target="_blank" rel="noopener" class="page-share-link share-pinterest" aria-label="Pinterest"><i class="fab fa-pinterest"></i></a>
    <a href="mailto:?subject=<?php echo $bc_title; ?>&body=<?php echo urldecode( $bc_url ); ?>" target="_blank" rel="noopener" class="page-share-link share-email" aria-label="Correo"><i class="fas fa-envelope"></i></a>
  </div>
  <?php
}
