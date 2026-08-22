<?php

class LDS_Passage_REST_Controller {

    private $data_loader;

    public function __construct() {
        $this->data_loader = new LDS_Passage_Data_Loader();
    }

    public function register_routes() {
        register_rest_route( 'lds-passage-block/v1', '/volumes', array(
            'methods'             => 'GET',
            'callback'            => array( $this, 'get_volumes' ),
            'permission_callback' => '__return_true',
        ) );

        register_rest_route( 'lds-passage-block/v1', '/books', array(
            'methods'             => 'GET',
            'callback'            => array( $this, 'get_books' ),
            'permission_callback' => '__return_true',
            'args'                => array(
                'volume' => array(
                    'required'          => true,
                    'sanitize_callback' => 'sanitize_text_field',
                ),
            ),
        ) );

        register_rest_route( 'lds-passage-block/v1', '/verses-count', array(
            'methods'             => 'GET',
            'callback'            => array( $this, 'get_verses_count' ),
            'permission_callback' => '__return_true',
            'args'                => array(
                'volume'  => array(
                    'required'          => true,
                    'sanitize_callback' => 'sanitize_text_field',
                ),
                'book'    => array(
                    'required'          => true,
                    'sanitize_callback' => 'sanitize_text_field',
                ),
                'chapter' => array(
                    'required'          => true,
                    'sanitize_callback' => 'absint',
                ),
            ),
        ) );

        register_rest_route( 'lds-passage-block/v1', '/passage', array(
            'methods'             => 'GET',
            'callback'            => array( $this, 'get_passage' ),
            'permission_callback' => '__return_true',
            'args'                => array(
                'volume'     => array(
                    'required'          => true,
                    'sanitize_callback' => 'sanitize_text_field',
                ),
                'book'       => array(
                    'required'          => true,
                    'sanitize_callback' => 'sanitize_text_field',
                ),
                'chapter'    => array(
                    'required'          => true,
                    'sanitize_callback' => 'absint',
                ),
                'startVerse' => array(
                    'required'          => true,
                    'sanitize_callback' => 'absint',
                ),
                'endVerse'   => array(
                    'required'          => true,
                    'sanitize_callback' => 'absint',
                ),
            ),
        ) );
    }

    public function get_volumes( $request ) {
        $volumes = $this->data_loader->get_volumes();
        $result = array();
        foreach ( $volumes as $v ) {
            $result[] = array(
                'slug' => $v['slug'],
                'name' => $v['name'],
            );
        }
        return rest_ensure_response( $result );
    }

    public function get_books( $request ) {
        $volume = $request->get_param( 'volume' );
        $volume_data = $this->data_loader->get_volume( $volume );

        return rest_ensure_response( array(
            'books'         => $volume_data ? $volume_data['books'] : array(),
            'sectionBased'  => $volume_data && ! empty( $volume_data['sectionBased'] ),
        ) );
    }

    public function get_verses_count( $request ) {
        $count = $this->data_loader->get_verse_count(
            $request->get_param( 'volume' ),
            $request->get_param( 'book' ),
            $request->get_param( 'chapter' )
        );
        return rest_ensure_response( array( 'verseCount' => $count ) );
    }

    public function get_passage( $request ) {
        $passage = $this->data_loader->get_passage(
            $request->get_param( 'volume' ),
            $request->get_param( 'book' ),
            $request->get_param( 'chapter' ),
            $request->get_param( 'startVerse' ),
            $request->get_param( 'endVerse' )
        );

        if ( ! $passage || empty( $passage['verses'] ) ) {
            return new WP_Error(
                'passage_not_found',
                'Pasaje no encontrado. Los datos de escritura aún no se han cargado para este libro.',
                array( 'status' => 404 )
            );
        }

        return rest_ensure_response( array(
            'html' => $this->format_passage( $passage, $request ),
        ) );
    }

    private function format_passage( $passage, $request ) {
        $html = '';
        $start_verse = $request->get_param( 'startVerse' );
        $end_verse   = $request->get_param( 'endVerse' );
        $chapter     = $request->get_param( 'chapter' );

        foreach ( $passage['verses'] as $i => $verse ) {
            $verse_num = $start_verse + $i;
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
            $start_verse === $end_verse ? $start_verse : $start_verse . "\xe2\x80\x94" . $end_verse
        );
        $html .= '<cite>' . esc_html( $citation ) . '</cite>';

        return $html;
    }
}
