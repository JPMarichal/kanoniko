/**
 * JavaScript for Hura AI Content Generator plugin.
 *
 * Handles AJAX tasks: Generate Content, Save as Draft,
 * Copy to Clipboard, and displaying notifications.
 *
 * @package Hura_AI_Content_Generator
 * @since   1.0.0
 */

(function ($) {
	'use strict';

	/**
	 * Main object containing all handler methods.
	 *
	 * @since 1.0.0
	 */
	var HuraAI = {

		/**
		 * Initialize events.
		 */
		init: function () {
			this.bindEvents();
		},

		/**
		 * Bind events to page elements.
		 */
		bindEvents: function () {
			var self = this;

			// Generate button click event.
			$('#hura-btn-generate').on('click', function (e) {
				e.preventDefault();
				self.generateContent();
			});

			// Copy to Clipboard button click event.
			$('#hura-btn-copy').on('click', function (e) {
				e.preventDefault();
				self.copyToClipboard();
			});

			// Save to Post (Draft) button click event.
			$('#hura-btn-save').on('click', function (e) {
				e.preventDefault();
				self.saveAsDraft();
			});
		},

		/**
		 * Handle Generate Content: Send AJAX and update UI.
		 */
		generateContent: function () {
			var self = this;

			// Collect form data.
			var formData = {
				action: 'hura_ai_generate_content',
				nonce: hura_ai_ajax.nonce,
				category: $('#hura-ai-category').val(),
				language: $('#hura-ai-language').val(),
				tone: $('#hura-ai-tone').val(),
				keywords: $('#hura-ai-keywords').val(),
				length: $('#hura-ai-length').val(),
				description: $('#hura-ai-description').val()
			};

			// Validate input data.
			if (!formData.language || !formData.tone) {
				self.showNotice('error', 'Please fill in all required fields.');
				return;
			}

			// Show loading, hide placeholder and editor.
			$('#hura-ai-placeholder').hide();
			$('#hura-ai-editor-area').hide();
			$('#hura-ai-loading').show();

			// Disable Generate button to prevent spam.
			$('#hura-btn-generate').prop('disabled', true).text('Processing...');

			// Send AJAX request.
			$.ajax({
				url: hura_ai_ajax.ajax_url,
				type: 'POST',
				data: formData,
				dataType: 'json',
				success: function (response) {
					if (response.success) {
						// Fill title and content into editor.
						$('#hura-ai-post-title').val(response.data.title);

						// Set content in wp_editor (tinyMCE).
						if (typeof tinyMCE !== 'undefined' && tinyMCE.get('hura_ai_editor')) {
							tinyMCE.get('hura_ai_editor').setContent(response.data.content);
						} else {
							$('#hura_ai_editor').val(response.data.content);
						}

						// Hide loading, show editor.
						$('#hura-ai-loading').hide();
						$('#hura-ai-editor-area').show();

						// Show success notification.
						self.showNotice('success', 'Article created successfully! You can edit it directly below.');
					} else {
						// Handle server error.
						$('#hura-ai-loading').hide();
						$('#hura-ai-placeholder').show();
						self.showNotice('error', response.data.message || 'An error occurred while generating content.');
					}
				},
				error: function (jqXHR, textStatus) {
					$('#hura-ai-loading').hide();
					$('#hura-ai-placeholder').show();
					self.showNotice('error', 'Connection error: ' + textStatus);
				},
				complete: function () {
					// Re-enable Generate button.
					$('#hura-btn-generate').prop('disabled', false).text('Generate');
				}
			});
		},

		/**
		 * Copy content from wp_editor to Clipboard.
		 */
		copyToClipboard: function () {
			var self = this;
			var content = '';

			// Get content from wp_editor.
			if (typeof tinyMCE !== 'undefined' && tinyMCE.get('hura_ai_editor') && !tinyMCE.get('hura_ai_editor').isHidden()) {
				content = tinyMCE.get('hura_ai_editor').getContent();
			} else {
				content = $('#hura_ai_editor').val();
			}

			if (!content) {
				self.showNotice('error', 'No content to copy.');
				return;
			}

			// Create a temporary textarea to copy from.
			var $temp = $('<textarea>');
			$('body').append($temp);
			$temp.val(content).select();

			try {
				document.execCommand('copy');
				self.showNotice('success', 'Content copied to clipboard!');
			} catch (err) {
				self.showNotice('error', 'Could not copy. Please try again.');
			}

			$temp.remove();
		},

		/**
		 * Save post as Draft via AJAX.
		 */
		saveAsDraft: function () {
			var self = this;
			var title = $('#hura-ai-post-title').val();
			var content = '';
			var category = $('#hura-ai-category').val();

			// Get content from wp_editor.
			if (typeof tinyMCE !== 'undefined' && tinyMCE.get('hura_ai_editor') && !tinyMCE.get('hura_ai_editor').isHidden()) {
				content = tinyMCE.get('hura_ai_editor').getContent();
			} else {
				content = $('#hura_ai_editor').val();
			}

			// Validate data.
			if (!title || !content) {
				self.showNotice('error', 'Title and content cannot be empty.');
				return;
			}

			// Disable Save button.
			$('#hura-btn-save').prop('disabled', true).text('Saving...');

			// Send AJAX request.
			$.ajax({
				url: hura_ai_ajax.ajax_url,
				type: 'POST',
				data: {
					action: 'hura_ai_save_as_draft',
					nonce: hura_ai_ajax.nonce,
					title: title,
					content: content,
					category: category
				},
				dataType: 'json',
				success: function (response) {
					if (response.success) {
						// Show success notification with edit link.
						var message = response.data.message;
						if (response.data.edit_url) {
							message += ' <a href="' + response.data.edit_url + '" target="_blank">Edit Post</a>';
						}
						self.showNotice('success', message);
					} else {
						self.showNotice('error', response.data.message || 'An error occurred while saving the post.');
					}
				},
				error: function () {
					self.showNotice('error', 'Connection error. Please try again.');
				},
				complete: function () {
					$('#hura-btn-save').prop('disabled', false).text('Save to Post (Draft)');
				}
			});
		},

		/**
		 * Display Admin Notice as a Toast.
		 *
		 * @param {string} type    Notice type: 'success' or 'error'.
		 * @param {string} message Notice message content (can contain HTML).
		 */
		showNotice: function (type, message) {
			var noticeClass = (type === 'success') ? 'notice-success' : 'notice-error';
			var dismissButton = '<button type="button" class="notice-dismiss"><span class="screen-reader-text">Dismiss</span></button>';
			var noticeHtml = '<div class="notice ' + noticeClass + ' is-dismissible">' +
				'<p>' + message + '</p>' +
				dismissButton +
				'</div>';

			var $notices = $('#hura-ai-notices');
			$notices.html(noticeHtml);

			// Auto-hide notification after 8 seconds.
			setTimeout(function () {
				$notices.find('.notice').fadeOut(300, function () {
					$(this).remove();
				});
			}, 8000);

			// Handle dismiss event for notifications.
			$notices.on('click', '.notice-dismiss', function () {
				$(this).closest('.notice').fadeOut(300, function () {
					$(this).remove();
				});
			});
		}
	};

	// Khởi tạo khi DOM đã sẵn sàng.
	$(document).ready(function () {
		HuraAI.init();
	});

})(jQuery);
