<?php

class LDS_Passage_Block_Renderer {

    private $data_loader;

    public function __construct() {
        $this->data_loader = new LDS_Passage_Data_Loader();
    }

    public function render( $attributes, $content, $block ) {
        $volume     = $attributes['volume'] ?? '';
        $book       = $attributes['book'] ?? '';
        $chapter    = $attributes['chapter'] ?? 0;
        $startVerse = $attributes['startVerse'] ?? 0;
        $endVerse   = $attributes['endVerse'] ?? $startVerse;

        if ( empty( $volume ) || empty( $book ) || $chapter < 1 || $startVerse < 1 ) {
            return '';
        }

        if ( $endVerse < $startVerse ) {
            $endVerse = $startVerse;
        }

        $passage = $this->data_loader->get_passage( $volume, $book, $chapter, $startVerse, $endVerse );

        if ( ! $passage || empty( $passage['verses'] ) ) {
            return '';
        }

        $html = '<blockquote class="wp-block-lds-passage-block-passage">';

        foreach ( $passage['verses'] as $i => $verse ) {
            $verse_num = $startVerse + $i;
            $html .= sprintf(
                '<div class="verse-line"><strong class="verse-num">%d</strong> %s</div>',
                $verse_num,
                esc_html( $verse )
            );
        }

        $citation = sprintf(
            '(%s %d:%s)',
            $passage['book_name'],
            $chapter,
            $startVerse === $endVerse ? $startVerse : $startVerse . "\xe2\x80\x94" . $endVerse
        );
        $html .= '<cite>' . esc_html( $citation ) . '</cite>';
        $html .= '</blockquote>';

        return $html;
    }
}
