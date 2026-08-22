=== Hura AI Content Generator ===
Contributors: huynhmaianhkiet
Tags: AI content, SEO, OpenRouter, content generator, auto writing
Requires at least: 5.0
Tested up to: 7.0
Stable tag: 1.0.0
Requires PHP: 7.4
License: GPL v2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Automatically generate SEO-optimized articles using optimized Prompt structure via OpenRouter API.

== Description ==

Hura AI Content Generator helps you automatically create SEO-optimized articles using the power of AI through the OpenRouter API.

Key Features:

* Generate articles in multiple languages (English, Arabic, Chinese, French, German, Hindi, Japanese, Spanish, Vietnamese, and many more).
* Customize writing tone (Professional, Creative, Informative, Casual).
* Natural keyword integration.
* Choose article length (Short, Medium, Long).
* Integrated WordPress Editor (TinyMCE) for direct editing.
* Save posts as Draft with a single click.
* Easy copy to Clipboard.
* Support for multiple AI Models from OpenRouter.

== External Services ==

This plugin connects to a third-party API via OpenRouter to generate AI content. It sends user-prompted text data to OpenRouter's servers when a content generation request is triggered by the administrator.

This service is provided by OpenRouter. You can find their legal documents here:
- OpenRouter Terms of Service: https://openrouter.ai/terms
- OpenRouter Privacy Policy: https://openrouter.ai/privacy

== Installation ==

1. Upload the plugin and extract it to `/wp-content/plugins/hura-ai-content-generator/`.
2. Activate the plugin via the 'Plugins' menu in WordPress Admin.
3. Go to 'AI Content Generator' → 'Settings' to configure your API Key.
4. Register at https://openrouter.ai/keys to get an API Key.
5. Enter your API Key and select your desired AI Model.
6. Go to 'AI Content Generator' → 'Generate' to start creating content.

== Frequently Asked Questions ==

= How do I get an API Key? =

Register at https://openrouter.ai/keys and create a new API Key.

= What AI Models can I use? =

You can use any Model available on OpenRouter, for example:
- meta-llama/llama-3-8b-instruct:free (Free)
- openai/gpt-4o
- anthropic/claude-3.5-sonnet
- google/gemini-pro

= Does the plugin support Vietnamese? =

Yes, the plugin fully supports Vietnamese and many other languages.

== Changelog ==

= 1.0.0 =
* Initial release.
* Auto-generate article content via OpenRouter API.
* Integrated WordPress Editor.
* Save posts as Draft.
* Multi-language support.
* Flexible AI Model configuration.

== Upgrade Notice ==

= 1.0.0 =
Initial release.
