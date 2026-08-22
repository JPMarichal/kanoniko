<?php

class LDS_Passage_Data_Loader {

    public function get_volumes() {
        $path = LDS_PASSAGE_BLOCK_DIR . 'data/volumes.json';
        if ( ! file_exists( $path ) ) {
            return array();
        }
        return json_decode( file_get_contents( $path ), true );
    }

    public function get_volume( $volume_slug ) {
        $volumes = $this->get_volumes();
        foreach ( $volumes as $v ) {
            if ( $v['slug'] === $volume_slug ) {
                return $v;
            }
        }
        return null;
    }

    public function get_books( $volume_slug ) {
        $volume = $this->get_volume( $volume_slug );
        return $volume ? $volume['books'] : array();
    }

    public function get_verse_count( $volume_slug, $book_slug, $chapter ) {
        $path = $this->get_book_path( $volume_slug, $book_slug );
        if ( ! file_exists( $path ) ) {
            return 0;
        }
        $book_data = json_decode( file_get_contents( $path ), true );
        $chapter_key = (string) $chapter;
        if ( ! isset( $book_data[ $chapter_key ] ) ) {
            return 0;
        }
        return count( $book_data[ $chapter_key ] );
    }

    public function get_passage( $volume_slug, $book_slug, $chapter, $start_verse, $end_verse ) {
        $path = $this->get_book_path( $volume_slug, $book_slug );
        if ( ! file_exists( $path ) ) {
            return null;
        }
        $book_data = json_decode( file_get_contents( $path ), true );
        $chapter_key = (string) $chapter;
        if ( ! isset( $book_data[ $chapter_key ] ) ) {
            return null;
        }

        $all_verses = $book_data[ $chapter_key ];
        $verses = array_slice( $all_verses, $start_verse - 1, $end_verse - $start_verse + 1 );

        $book_name = $this->get_book_name( $volume_slug, $book_slug );

        return array(
            'verses'    => $verses,
            'book_name' => $book_name,
        );
    }

    private function get_book_name( $volume_slug, $book_slug ) {
        $books = $this->get_books( $volume_slug );
        foreach ( $books as $b ) {
            if ( $b['slug'] === $book_slug ) {
                return $b['name'];
            }
        }
        return $book_slug;
    }

    private function get_book_path( $volume_slug, $book_slug ) {
        return LDS_PASSAGE_BLOCK_DIR . "data/{$volume_slug}/{$book_slug}.json";
    }
}
