<?php
/**
 * CPT: bc_quote_author (Personas) - Carbon Fields configuration
 */

defined( 'ABSPATH' ) || exit;

use Carbon_Fields\Container;
use Carbon_Fields\Field;

$calling_terms = [
    ''                               => '— Seleccionar —',
    'presidente-de-la-iglesia'      => 'Presidente de la Iglesia',
    'consejero-primera-presidencia' => 'Consejero en la Primera Presidencia',
    'apostol'                        => 'Apóstol',
    'setenta-autoridad-general'      => 'Setenta Autoridad General',
    'asistente-cuorum-doce'          => 'Asistente al Cuórum de los Doce',
    'obispo-presidente'              => 'Obispo Presidente',
    'obispado-presidente'            => 'Obispado Presidente',
    'patriarca-general'              => 'Patriarca General',
    'presidencia-sociedad-socorro'   => 'Presidencia General de la Sociedad de Socorro',
    'presidencia-escuela-dominical'  => 'Presidencia General de la Escuela Dominical',
    'presidencia-hombres-jovenes'    => 'Presidencia General de los Hombres Jóvenes',
    'presidencia-mujeres-jovenes'    => 'Presidencia General de las Mujeres Jóvenes',
    'presidencia-primaria'           => 'Presidencia General de la Primaria',
    'consejero-asistente-pp'         => 'Consejero Asistente de la Primera Presidencia',
    'otro'                           => 'Otro',
];

Container::make( 'post_meta', 'Datos de Persona' )
    ->where( 'post_type', '=', 'bc_quote_author' )
    ->add_fields( [
        Field::make( 'text', '_author_description', 'Descripción (último llamamiento)' )
            ->set_attribute( 'placeholder', 'Ej: Decimosexto Presidente de la Iglesia de Jesucristo de los Santos de los Últimos Días' )
            ->set_help_text( 'Breve descripción del autor (cargo, llamado, etc.)' ),

        Field::make( 'checkbox', '_author_is_ga', 'Es Autoridad General' ),

        Field::make( 'select', '_author_witness_type', 'Testigo del Libro de Mormón' )
            ->add_options( [
                ''                => '— No es testigo —',
                'three-witnesses' => 'Uno de los tres testigos',
                'eight-witnesses' => 'Uno de los ocho testigos',
            ] ),

        Field::make( 'separator', 'bio_separator', 'Información biográfica' ),

        Field::make( 'text', '_author_birth_date', 'Fecha de nacimiento' )
            ->set_attribute( 'placeholder', 'Ej: 12 de enero de 1800' ),

        Field::make( 'text', '_author_birth_place', 'Lugar de nacimiento' )
            ->set_attribute( 'placeholder', 'Ej: Sharon, Vermont, Estados Unidos' ),

        Field::make( 'text', '_author_death_date', 'Fecha de defunción' )
            ->set_attribute( 'placeholder', 'Ej: 23 de agosto de 1877' ),

        Field::make( 'text', '_author_death_place', 'Lugar de defunción' )
            ->set_attribute( 'placeholder', 'Ej: Salt Lake City, Utah, Estados Unidos' ),

        Field::make( 'text', '_author_nationality', 'Nacionalidad' )
            ->set_attribute( 'placeholder', 'Ej: Estadounidense' ),

        Field::make( 'separator', 'parents_separator', 'Padres' ),

        Field::make( 'text', '_author_father', 'Padre' )
            ->set_attribute( 'placeholder', 'Ej: Joseph Smith Sr.' ),

        Field::make( 'text', '_author_mother', 'Madre' )
            ->set_attribute( 'placeholder', 'Ej: Lucy Mack Smith' ),

        Field::make( 'separator', 'spouses_separator', 'Cónyuges' ),

        Field::make( 'complex', '_author_spouses', 'Cónyuges' )
            ->set_help_text( 'Agrega cónyuges en orden cronológico.' )
            ->add_fields( [
                Field::make( 'text', 'name', 'Nombre completo' )
                    ->set_attribute( 'placeholder', 'Nombre completo' ),
                Field::make( 'text', 'marriage_year', 'Año de matrimonio' )
                    ->set_attribute( 'type', 'number' )
                    ->set_attribute( 'min', 1800 )
                    ->set_attribute( 'max', 2100 )
                    ->set_attribute( 'placeholder', 'Matrimonio' ),
                Field::make( 'text', 'end_year', 'Año de fin (opcional)' )
                    ->set_attribute( 'type', 'number' )
                    ->set_attribute( 'min', 1800 )
                    ->set_attribute( 'max', 2100 )
                    ->set_attribute( 'placeholder', 'Fin (opcional)' ),
                Field::make( 'text', 'children_count', 'Número de hijos' )
                    ->set_attribute( 'type', 'number' )
                    ->set_attribute( 'min', 0 )
                    ->set_attribute( 'max', 99 )
                    ->set_attribute( 'placeholder', 'Hijos' ),
            ] )
            ->set_layout( 'tabbed-vertical' )
            ->set_header_template( '<%- name || "Cónyuge" %>' ),

        Field::make( 'separator', 'callings_separator', 'Historial de llamamientos' ),

        Field::make( 'complex', '_author_callings', 'Llamamientos' )
            ->set_help_text( 'Agrega todos los llamamientos en orden cronológico. El último se usa como descripción principal.' )
            ->add_fields( [
                Field::make( 'select', 'calling', 'Llamamiento' )
                    ->add_options( $calling_terms ),
                Field::make( 'text', 'org', 'Descripción completa / Organización' )
                    ->set_attribute( 'placeholder', 'Descripción completa' ),
                Field::make( 'text', 'start', 'Año de inicio' )
                    ->set_attribute( 'type', 'number' )
                    ->set_attribute( 'min', 1800 )
                    ->set_attribute( 'max', 2100 )
                    ->set_attribute( 'placeholder', 'Inicio' ),
                Field::make( 'text', 'end', 'Año de fin' )
                    ->set_attribute( 'type', 'number' )
                    ->set_attribute( 'min', 1800 )
                    ->set_attribute( 'max', 2100 )
                    ->set_attribute( 'placeholder', 'Fin' ),
            ] )
            ->set_layout( 'tabbed-vertical' )
            ->set_header_template( '<%- calling_label || "Llamamiento" %> <%- org ? "— " + org : "" %>' ),
    ] );

// Register meta keys for REST API
add_action( 'init', function () {
    $meta_fields = [
        '_author_description'  => [ 'type' => 'string', 'show_in_rest' => true ],
        '_author_is_ga'        => [ 'type' => 'boolean', 'show_in_rest' => true ],
        '_author_witness_type' => [ 'type' => 'string', 'show_in_rest' => true ],
        '_author_callings'     => [ 'type' => 'string', 'show_in_rest' => true ],
        '_author_birth_date'   => [ 'type' => 'string', 'show_in_rest' => true ],
        '_author_birth_place'  => [ 'type' => 'string', 'show_in_rest' => true ],
        '_author_death_date'   => [ 'type' => 'string', 'show_in_rest' => true ],
        '_author_death_place'  => [ 'type' => 'string', 'show_in_rest' => true ],
        '_author_nationality'  => [ 'type' => 'string', 'show_in_rest' => true ],
        '_author_father'       => [ 'type' => 'string', 'show_in_rest' => true ],
        '_author_mother'       => [ 'type' => 'string', 'show_in_rest' => true ],
        '_author_spouses'      => [ 'type' => 'string', 'show_in_rest' => true ],
    ];

    foreach ( $meta_fields as $key => $args ) {
        register_post_meta( 'bc_quote_author', $key, $args );
    }
} );

// Sync taxonomy terms from callings
add_action( 'carbon_fields_post_meta_container_saved', function ( $post_id ) {
    if ( get_post_type( $post_id ) !== 'bc_quote_author' ) {
        return;
    }

    $callings = carbon_get_post_meta( $post_id, '_author_callings' );
    if ( is_array( $callings ) && ! empty( $callings ) ) {
        $term_slugs = array_unique( array_column( $callings, 'calling' ) );
        wp_set_object_terms( $post_id, array_values( $term_slugs ), 'bc_author_calling', true );
    }
} );