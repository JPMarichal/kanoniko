import { __ } from '@wordpress/i18n';
import { useState, useEffect } from '@wordpress/element';
import { SelectControl, Spinner, ToolbarGroup, ToolbarButton, Button } from '@wordpress/components';
import { BlockControls, useBlockProps } from '@wordpress/block-editor';
import apiFetch from '@wordpress/api-fetch';
import { addQueryArgs } from '@wordpress/url';

function range( n ) {
    return Array.from( { length: n }, ( _, i ) => i + 1 );
}

export default function Edit( { attributes, setAttributes } ) {
    const { volume, book, chapter, startVerse, endVerse } = attributes;
    const hasPassage = !! ( volume && book && chapter && startVerse );

    const [ isEditing, setIsEditing ] = useState( ! hasPassage );
    const [ volumes, setVolumes ] = useState( [] );
    const [ books, setBooks ] = useState( [] );
    const [ sectionBased, setSectionBased ] = useState( false );
    const [ verseCount, setVerseCount ] = useState( 0 );
    const [ passageHtml, setPassageHtml ] = useState( '' );
    const [ loading, setLoading ] = useState( false );
    const blockProps = useBlockProps();

    useEffect( () => {
        apiFetch( { path: '/lds-passage-block/v1/volumes' } ).then( setVolumes ).catch( () => {} );
    }, [] );

    useEffect( () => {
        if ( ! volume ) {
            setBooks( [] );
            setSectionBased( false );
            return;
        }
        apiFetch( { path: addQueryArgs( '/lds-passage-block/v1/books', { volume } ) } )
            .then( ( data ) => {
                setBooks( data.books );
                setSectionBased( data.sectionBased );
            } )
            .catch( () => {} );
    }, [ volume ] );

    useEffect( () => {
        if ( ! volume || ! book || ! chapter ) {
            setVerseCount( 0 );
            return;
        }
        apiFetch( {
            path: addQueryArgs( '/lds-passage-block/v1/verses-count', { volume, book, chapter } ),
        } )
            .then( ( data ) => setVerseCount( data.verseCount ) )
            .catch( () => {} );
    }, [ volume, book, chapter ] );

    useEffect( () => {
        if ( ! volume || ! book || ! chapter || ! startVerse ) {
            setPassageHtml( '' );
            return;
        }
        setLoading( true );
        apiFetch( {
            path: addQueryArgs( '/lds-passage-block/v1/passage', {
                volume,
                book,
                chapter,
                startVerse,
                endVerse: endVerse || startVerse,
            } ),
        } )
            .then( ( data ) => setPassageHtml( data.html ) )
            .catch( () => setPassageHtml( '' ) )
            .finally( () => setLoading( false ) );
    }, [ volume, book, chapter, startVerse, endVerse, isEditing ] );

    const selectedBook = books.find( ( b ) => b.slug === book );
    const chapterCount = selectedBook ? selectedBook.chapters : 0;
    const chapterLabel = sectionBased ? __( 'Sección', 'lds-passage-block' ) : __( 'Capítulo', 'lds-passage-block' );

    const chapterOptions = [
        { value: '', label: `Seleccionar ${chapterLabel.toLowerCase()}...` },
        ...range( chapterCount ).map( ( i ) => ( { value: i, label: `${chapterLabel} ${i}` } ) ),
    ];

    const verseOptions = [
        { value: '', label: 'Seleccionar versículo...' },
        ...range( verseCount ).map( ( i ) => ( { value: i, label: `Versículo ${i}` } ) ),
    ];

    const selectors = (
        <div className="lds-passage-selectors" style={ { maxWidth: 720, margin: '0 auto' } }>
            <SelectControl
                label={ __( 'Volumen', 'lds-passage-block' ) }
                value={ volume }
                options={ [
                    { value: '', label: 'Seleccionar volumen...' },
                    ...volumes.map( ( v ) => ( { value: v.slug, label: v.name } ) ),
                ] }
                onChange={ ( val ) =>
                    setAttributes( {
                        volume: val,
                        book: '',
                        chapter: 1,
                        startVerse: 1,
                        endVerse: 1,
                    } )
                }
            />

            <SelectControl
                label={ __( 'Libro', 'lds-passage-block' ) }
                value={ book }
                options={ [
                    { value: '', label: 'Seleccionar libro...' },
                    ...books.map( ( b ) => ( { value: b.slug, label: b.name } ) ),
                ] }
                onChange={ ( val ) =>
                    setAttributes( {
                        book: val,
                        chapter: 1,
                        startVerse: 1,
                        endVerse: 1,
                    } )
                }
                disabled={ ! volume }
            />

            <SelectControl
                label={ chapterLabel }
                value={ chapter }
                options={ chapterOptions }
                onChange={ ( val ) =>
                    setAttributes( {
                        chapter: Number( val ),
                        startVerse: 1,
                        endVerse: 1,
                    } )
                }
                disabled={ ! book }
            />

            <SelectControl
                label={ __( 'Versículo inicial', 'lds-passage-block' ) }
                value={ startVerse }
                options={ verseOptions }
                onChange={ ( val ) => {
                    const v = Number( val );
                    setAttributes( {
                        startVerse: v,
                        endVerse: v > Number( endVerse ) ? v : endVerse,
                    } );
                } }
                disabled={ ! chapter || verseCount === 0 }
            />

            <SelectControl
                label={ __( 'Versículo final (opcional)', 'lds-passage-block' ) }
                value={ endVerse }
                options={ [
                    { value: startVerse, label: `= Inicial (${startVerse})` },
                    ...range( verseCount )
                        .filter( ( i ) => i > startVerse )
                        .map( ( i ) => ( { value: i, label: `Versículo ${i}` } ) ),
                ] }
                onChange={ ( val ) => setAttributes( { endVerse: Number( val ) } ) }
                disabled={ ! startVerse }
            />
        </div>
    );

    if ( isEditing || ! hasPassage ) {
        return (
            <div { ...blockProps }>
                <div className="lds-passage-editor" style={ { maxWidth: 720, margin: '0 auto' } }>
                    <div className="lds-passage-header">
                        <span className="lds-passage-icon">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M4 6H20V7.5H4V6Z" fill="currentColor"/>
                                <path d="M4 9.5H20V11H4V9.5Z" fill="currentColor"/>
                                <path d="M4 13H14V14.5H4V13Z" fill="currentColor"/>
                                <path d="M4 16.5H10V18H4V16.5Z" fill="currentColor"/>
                                <path d="M18 13.5L22 17L18 20.5V13.5Z" fill="currentColor"/>
                            </svg>
                        </span>
                        <span>{ __( 'Pasaje de Escritura', 'lds-passage-block' ) }</span>
                    </div>
                    <p className="lds-passage-desc">
                        { __(
                            'Selecciona el pasaje de las Escrituras que deseas insertar.',
                            'lds-passage-block'
                        ) }
                    </p>
                    { selectors }
                    { loading && <Spinner /> }
                    { passageHtml && ! loading && (
                        <div
                            className="lds-passage-preview"
                            dangerouslySetInnerHTML={ { __html: passageHtml } }
                        />
                    ) }
                    { ! passageHtml && ! loading && volume && book && chapter && (
                        <p className="lds-passage-empty">
                            { __(
                                'Selecciona los versículos para ver el pasaje.',
                                'lds-passage-block'
                            ) }
                        </p>
                    ) }
                    { passageHtml && (
                        <div className="lds-passage-actions">
                            <Button
                                isPrimary
                                onClick={ () => setIsEditing( false ) }
                            >
                                { __( 'Insertar pasaje', 'lds-passage-block' ) }
                            </Button>
                        </div>
                    ) }
                </div>
            </div>
        );
    }

    return (
        <>
            <BlockControls>
                <ToolbarGroup>
                    <ToolbarButton
                        icon="edit"
                        label={ __( 'Cambiar pasaje', 'lds-passage-block' ) }
                        onClick={ () => setIsEditing( true ) }
                    />
                </ToolbarGroup>
            </BlockControls>
            <blockquote { ...blockProps }>
                { loading && <Spinner /> }
                { passageHtml && (
                    <div dangerouslySetInnerHTML={ { __html: passageHtml } } />
                ) }
            </blockquote>
        </>
    );
}
