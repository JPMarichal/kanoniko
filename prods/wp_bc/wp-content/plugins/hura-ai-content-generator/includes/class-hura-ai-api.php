<?php
/**
 * Handles connection and interaction with the OpenRouter API.
 *
 * Provides methods to call the API for generating article content
 * based on user-configured prompts.
 *
 * @package Hura_AI_Content_Generator
 * @since   1.0.0
 */

// Prevent direct access.
defined( 'ABSPATH' ) || exit;

/**
 * Class Hura_AI_API.
 *
 * Handles sending requests to the OpenRouter API, receiving responses,
 * checking for errors, and returning decoded JSON data.
 *
 * @since 1.0.0
 */
class Hura_AI_API {

	/**
	 * OpenRouter API endpoint.
	 *
	 * @since 1.0.0
	 * @var string
	 */
	private $api_url = 'https://openrouter.ai/api/v1/chat/completions';

	/**
	 * Call the OpenRouter API to generate article content.
	 *
	 * Builds a complete prompt including System Prompt and User Prompt,
	 * sends it to OpenRouter, and processes the returned result.
	 *
	 * @since 1.0.0
	 *
	 * @param array $prompt_data Array of parameters:
	 *                           - language    (string) Article language.
	 *                           - tone        (string) Writing style.
	 *                           - keywords    (string) Keywords to include.
	 *                           - length      (string) Article length.
	 *                           - description (string) Additional requirements.
	 *                           - category    (int)    Category ID.
	 * @return array WP_REST-style response: { success: bool, data: mixed }
	 */
	public function hura_ai_call_openrouter( $prompt_data ) {
		// Get API Key and Model from settings.
		$api_key = get_option( 'hura_ai_openrouter_key', '' );
		$model   = get_option( 'hura_ai_openrouter_model', 'openrouter/free' );

		// Check if API Key exists.
		if ( empty( $api_key ) ) {
			return array(
				'success' => false,
				'data'    => __( 'Please configure the API Key in the Settings page before using.', 'hura-ai-content-generator' ),
			);
		}

		// Build System Prompt - force AI to return pure JSON.
		$system_prompt = 'You are an SEO Content Writer expert. Your task is to create SEO-optimized articles based on the information provided by the user.

IMPORTANT REQUIREMENTS:
- Always return the result as PURE JSON, DO NOT wrap it in ```json or any other markup blocks.
- The JSON structure must be exactly as follows:
{
  "title": "Article title",
  "content": "Article content in HTML format"
}
- "title" field: An attractive article title containing the main keyword, SEO-optimized.
- "content" field: The full article content in standard HTML format. Use appropriate <p>, <h2>, <h3>, <ul>, <li>, <strong>, <em> tags. Naturally integrate the keywords throughout the content.
- The content must have at least 3 headings (h2) and fully developed paragraphs.';

		// Build User Prompt from input data.
		$user_prompt = $this->hura_ai_build_user_prompt( $prompt_data );

		// Configure request body.
		$body = array(
			'model'    => $model,
			'messages' => array(
				array(
					'role'    => 'system',
					'content' => $system_prompt,
				),
				array(
					'role'    => 'user',
					'content' => $user_prompt,
				),
			),
			'max_tokens' => 4096,
			'temperature' => 0.7,
		);

		// Allow modifying the request body before encoding.
		$body = apply_filters( 'hura_ai_openrouter_request_body', $body, $prompt_data );

		// Cấu hình HTTP request.
		$args = array(
			'headers' => array(
				'Authorization' => 'Bearer ' . $api_key,
				'Content-Type'  => 'application/json',
				'HTTP-Referer'  => home_url(),
				'X-Title'       => get_bloginfo( 'name' ),
			),
			'body'    => wp_json_encode( $body ),
			'timeout' => 120,
		);

		// Allow modifying HTTP request arguments.
		$args = apply_filters( 'hura_ai_openrouter_request_args', $args, $prompt_data );

		// Send request to OpenRouter.
		$response = wp_remote_post( $this->api_url, $args );

		// Check for WP_Error.
		if ( is_wp_error( $response ) ) {
			return array(
				'success' => false,
				'data'    => $response->get_error_message(),
			);
		}

		// Check HTTP response status code.
		$status_code = wp_remote_retrieve_response_code( $response );
		if ( 200 !== $status_code ) {
			$error_body = wp_remote_retrieve_body( $response );
			$error_data = json_decode( $error_body, true );

			if ( isset( $error_data['error']['message'] ) ) {
				$error_msg = $error_data['error']['message'];
			} else {
				/* translators: %d: HTTP status code */
				$error_msg = sprintf( __( 'HTTP Error: %d', 'hura-ai-content-generator' ), $status_code );
			}

			return array(
				'success' => false,
				'data'    => $error_msg,
			);
		}

		// Get response body.
		$response_body = wp_remote_retrieve_body( $response );
		$response_data = json_decode( $response_body, true );

		// Check if JSON response is valid.
		if ( JSON_ERROR_NONE !== json_last_error() ) {
			return array(
				'success' => false,
				'data'    => __( 'API response is not valid JSON format.', 'hura-ai-content-generator' ),
			);
		}

		// Get content from AI.
		$ai_content = $response_data['choices'][0]['message']['content'] ?? '';

		if ( empty( $ai_content ) ) {
			return array(
				'success' => false,
				'data'    => __( 'API returned empty content.', 'hura-ai-content-generator' ),
			);
		}

		// Decode JSON from AI response.
		$parsed_content = json_decode( $ai_content, true );

		// If AI returned invalid JSON, try to clean the string.
		if ( JSON_ERROR_NONE !== json_last_error() ) {
			// Try to extract JSON strictly between the first '{' and the last '}'.
			$start = strpos( $ai_content, '{' );
			$end   = strrpos( $ai_content, '}' );
			
			if ( false !== $start && false !== $end && $end > $start ) {
				$cleaned = substr( $ai_content, $start, $end - $start + 1 );
				$parsed_content = json_decode( $cleaned, true );
			}
		}

		// Final validation.
		if ( JSON_ERROR_NONE !== json_last_error() || ! isset( $parsed_content['title'] ) || ! isset( $parsed_content['content'] ) ) {
			return array(
				'success' => false,
				'data'    => __( 'Could not decode AI content. Please try again.', 'hura-ai-content-generator' ),
			);
		}

		return array(
			'success' => true,
			'data'    => $parsed_content,
		);
	}

	/**
	 * Build User Prompt from form data.
	 *
	 * @since 1.0.0
	 *
	 * @param array $data Form data array.
	 * @return string Prompt string sent to AI.
	 */
	private function hura_ai_build_user_prompt( $data ) {
		$language    = isset( $data['language'] ) ? sanitize_text_field( $data['language'] ) : 'English';
		$tone        = isset( $data['tone'] ) ? sanitize_text_field( $data['tone'] ) : 'Professional';
		$keywords    = isset( $data['keywords'] ) ? sanitize_textarea_field( $data['keywords'] ) : '';
		$length      = isset( $data['length'] ) ? sanitize_text_field( $data['length'] ) : 'Medium (800-1500 words)';
		$description = isset( $data['description'] ) ? sanitize_textarea_field( $data['description'] ) : '';
		$category    = isset( $data['category'] ) ? absint( $data['category'] ) : 0;

		// Get category name if available.
		$category_name = '';
		if ( $category > 0 ) {
			$cat_obj = get_category( $category );
			if ( ! is_wp_error( $cat_obj ) ) {
				$category_name = $cat_obj->name;
			}
		}

		$prompt = "Create an article with the following parameters:\n\n";
		$prompt .= "- Language: {$language}\n";
		$prompt .= "- Writing style: {$tone}\n";
		$prompt .= "- Length: {$length}\n";

		if ( ! empty( $category_name ) ) {
			$prompt .= "- Category: {$category_name}\n";
		}

		if ( ! empty( $keywords ) ) {
			$prompt .= "- Keywords to include: {$keywords}\n";
		}

		if ( ! empty( $description ) ) {
			$prompt .= "- Additional description: {$description}\n";
		}

		$prompt .= "\nWrite a detailed, comprehensive, and high-quality article.";

		return $prompt;
	}
}
