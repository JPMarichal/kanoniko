<?php
/**
 * Image media auto-metadata.
 *
 * @package GeneratePress_Child
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Auto-populate alt text and description from post_title on new image uploads.
 */
add_action( 'add_attachment', 'bc_auto_image_metadata' );

function bc_auto_image_metadata( $attachment_id ) {
	if ( ! wp_attachment_is_image( $attachment_id ) ) {
		return;
	}

	$attachment = get_post( $attachment_id );
	if ( ! $attachment ) {
		return;
	}

	$title       = $attachment->post_title;
	$seo_alt     = apply_filters( 'bc_image_alt_override', '', $attachment_id );
	$seo_desc    = apply_filters( 'bc_image_description_override', '', $attachment_id );

	$needs_update = false;
	$update_data  = array( 'ID' => $attachment_id );

	if ( empty( $title ) ) {
		$title = bc_title_from_filename( $attachment_id );
		if ( $title ) {
			$update_data['post_title'] = $title;
			$needs_update = true;
		} else {
			return;
		}
	}

	$alt         = ! empty( $seo_alt ) ? $seo_alt : $title;
	$description = ! empty( $seo_desc ) ? $seo_desc : $title;

	if ( empty( get_post_meta( $attachment_id, '_wp_attachment_image_alt', true ) ) ) {
		update_post_meta( $attachment_id, '_wp_attachment_image_alt', sanitize_text_field( $alt ) );
	}

	if ( empty( $attachment->post_content ) ) {
		$update_data['post_content'] = sanitize_text_field( $description );
		$needs_update = true;
	}

	if ( $needs_update ) {
		remove_action( 'add_attachment', 'bc_auto_image_metadata' );
		wp_update_post( $update_data );
		add_action( 'add_attachment', 'bc_auto_image_metadata' );
	}
}

/**
 * Derive a title from the filename when post_title is empty.
 */
function bc_title_from_filename( $attachment_id ) {
	$file = get_post_meta( $attachment_id, '_wp_attached_file', true );
	if ( ! $file ) {
		return '';
	}
	$title = pathinfo( $file, PATHINFO_FILENAME );
	$title = str_replace( array( '-', '_' ), ' ', $title );
	$title = ucwords( $title );
	return $title;
}

/**
 * WP-CLI: wp bc image-metadata [--dry-run] [--force] [--batch-size=N]
 *
 * Backfill alt text and description for existing images.
 */
if ( defined( 'WP_CLI' ) && WP_CLI ) {
	WP_CLI::add_command( 'bc image-metadata', function ( $args, $assoc_args ) {
		global $wpdb;

		$batch_size = isset( $assoc_args['batch-size'] ) ? absint( $assoc_args['batch-size'] ) : 50;
		$dry_run    = ! empty( $assoc_args['dry-run'] );
		$force      = ! empty( $assoc_args['force'] );

		$total = (int) $wpdb->get_var(
			"SELECT COUNT(ID) FROM {$wpdb->posts}
			WHERE post_type = 'attachment'
			AND post_mime_type LIKE 'image/%'"
		);

		if ( ! $total ) {
			WP_CLI::success( 'No image attachments found.' );
			return;
		}

		$cursor    = 0;
		$processed = 0;
		$updated   = 0;

		$progress = WP_CLI\Utils\make_progress_bar( "Processing {$total} images", $total );

		while ( $processed < $total ) {
			$attachments = $wpdb->get_results( $wpdb->prepare(
				"SELECT ID, post_title, post_content
				FROM {$wpdb->posts}
				WHERE post_type = 'attachment'
				AND post_mime_type LIKE 'image/%'
				AND ID > %d
				ORDER BY ID ASC
				LIMIT %d",
				$cursor,
				$batch_size
			) );

			if ( empty( $attachments ) ) {
				break;
			}

			foreach ( $attachments as $attachment ) {
				$cursor = $attachment->ID;
				$processed++;

				$title = $attachment->post_title;

				$needs_title = $force || empty( $title );
				if ( $needs_title ) {
					$title = bc_title_from_filename( $attachment->ID );
					if ( empty( $title ) ) {
						$progress->tick();
						continue;
					}
				}

				$current_alt  = get_post_meta( $attachment->ID, '_wp_attachment_image_alt', true );
				$needs_alt    = $force || empty( $current_alt );
				$needs_desc   = $force || empty( $attachment->post_content );

				if ( ! $needs_title && ! $needs_alt && ! $needs_desc ) {
					$progress->tick();
					continue;
				}

				if ( $dry_run ) {
					$progress->tick();
					continue;
				}

				$seo_alt     = apply_filters( 'bc_image_alt_override', '', $attachment->ID );
				$seo_desc    = apply_filters( 'bc_image_description_override', '', $attachment->ID );
				$alt         = ! empty( $seo_alt ) ? $seo_alt : $title;
				$description = ! empty( $seo_desc ) ? $seo_desc : $title;

				$needs_update = false;
				$update_data  = array( 'ID' => $attachment->ID );

				if ( $needs_title ) {
					$update_data['post_title'] = $title;
					$needs_update = true;
				}

				if ( $needs_alt ) {
					update_post_meta( $attachment->ID, '_wp_attachment_image_alt', sanitize_text_field( $alt ) );
				}

				if ( $needs_desc ) {
					$update_data['post_content'] = sanitize_text_field( $description );
					$needs_update = true;
				}

				if ( $needs_update ) {
					wp_update_post( $update_data );
				}

				$updated++;
				$progress->tick();
			}

			wp_cache_flush_runtime();
		}

		$progress->finish();

		if ( $dry_run ) {
			WP_CLI::success( "Dry run: {$processed} images would be processed." );
		} else {
			WP_CLI::success( "Done. {$processed} checked, {$updated} updated." );
		}
	} );
}
