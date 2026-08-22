=== Indigetal Media Offload for Bunny.net ===
Contributors: indigetal
Tags: media, offload, storage, video, cdn
Requires at least: 6.5
Tested up to: 7.0
Requires PHP: 8.0
Stable tag: 1.0.5
License: GPL-2.0-or-later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Serve WordPress media from Bunny.net CDN. Offload Storage files and Stream video from the Media Library.

== Description ==

**Keep using the WordPress Media Library. Serve media from Bunny.net.**

Indigetal Media Offload for Bunny.net connects your existing Media Library uploads to Bunny **Storage** (files and images) and Bunny **Stream** (video). Attachments stay WordPress attachments — with CDN URLs, optional local file cleanup, and remote delete when you remove media in WordPress.

**Why site owners use it**

* **Use less server disk space** — Optionally remove local copies after successful offload.
* **CDN delivery** — Attachment URLs rewrite to your Storage and Stream Pull Zone hostnames.
* **Video without a separate workflow** — Upload video through the Media Library. Stream handles encoding and playback URLs.

**What you get**

* Bunny Storage offload for supported non-video attachments
* Bunny Stream offload for common video formats WordPress allows by default (MP4/M4V, MKV, WebM, MOV/QT, AVI, FLV, WMV, MPEG/MPG/MPE)
* Thumbnail and dimension metadata for Stream videos when encoding completes
* Remote delete for linked Storage objects and Stream videos
* Per-user Stream collections where that workflow applies

**How it works**

1. Install and activate the plugin.
2. Open **Media → Indigetal Media Offload for Bunny.net → Settings** and enter your Bunny.net Stream and/or Storage credentials and Pull Zone hostnames.
3. Upload through the Media Library as usual — offload and URL rewriting run on supported attachments.

**Delivery scope (important)**

This Free plugin provides **public/basic CDN URLs**. It does not generate signed or token-authenticated URLs from PHP. If your Pull Zone requires token auth on every request, configure Bunny at the edge and/or use a compatible Pro companion or custom integration. See **About & Privacy** in plugin settings and the FAQ below.

An optional **Pro** companion can add private signed delivery. Extension hooks are documented in the plugin.

== Screenshots ==

1. Settings — configure Stream and Storage credentials and Pull Zone hostnames.
2. Media Library — offloaded attachments served from Bunny CDN URLs.
3. About & Privacy — third-party data use, delivery scope, and uninstall retention policy.

== Installation ==

= Minimum Requirements =

* WordPress 6.5 or greater
* PHP 8.0 or greater
* A Bunny.net account
* **Stream (optional):** Stream API access key, library ID, Stream Pull Zone hostname
* **Storage (optional):** Storage zone credentials, region, Storage Pull Zone hostname

= Setup =

1. Install via **Plugins → Add New → Upload Plugin**, or copy the plugin folder to `wp-content/plugins/indigetal-media-offload-for-bunny-net/`.
2. Activate **Indigetal Media Offload for Bunny.net**.
3. Open **Media → Indigetal Media Offload for Bunny.net → Settings**, enable **Stream** and/or **Storage** as needed, then review **About & Privacy**.

By default, uninstall **keeps** plugin settings, credentials, and offload metadata in WordPress so you can reinstall without losing Bunny linkage. Enable **Advanced → Remove plugin-owned WordPress data on uninstall** only when you deliberately want that WordPress-side data removed.

== Frequently Asked Questions ==

= What is Bunny.net? =

Bunny.net provides global CDN, **Stream** (video), and **Storage** (object storage). This plugin uses those services and your Pull Zone hostnames so Media Library attachments can live on Bunny while WordPress keeps normal attachment records.

= Do I need a Bunny.net account? =

Yes. Create Stream libraries and Storage zones in the [Bunny.net dashboard](https://dash.bunny.net/), then enter the credentials and hostnames on **Media → Indigetal Media Offload for Bunny.net → Settings**.

= Do Stream and Storage use the same hostname? =

No. Stream playback uses your **Stream** Pull Zone hostname. Storage files use your **Storage** Pull Zone hostname. Use separate hostnames unless you intentionally configure Bunny.net otherwise.

= Are URLs signed or private? =

Not from this Free plugin. URLs use your configured Pull Zone hostnames and paths. Signed or member-only delivery requires Bunny edge configuration, a compatible Pro companion, or a custom integration — see **About & Privacy** in settings.

= What happens to local files after offload? =

Optional toggles remove local files after successful Storage offload or Stream upload. When enabled, WordPress may no longer keep a disk copy while delivery continues from Bunny.net. Back up before enabling local removal.

= What happens when I delete a WordPress attachment? =

Deleting an attachment can delete linked Storage objects (per manifest) and the remote Stream video. Treat attachment deletion as destructive for linked Bunny objects.

= What happens when I deactivate or uninstall? =

Deactivation clears scheduled events but keeps settings, credentials, and metadata. Uninstall keeps that data by default unless you opted in to **Remove plugin-owned WordPress data on uninstall**. Uninstall never deletes remote Bunny objects — clean those up in WordPress or the Bunny.net dashboard if needed.

= Can I edit images after local files are removed? =

WordPress flows that require a local original on disk may fail once local copies are deleted. Plan backups before enabling aggressive local removal.

= Does this work on multisite? =

The plugin is intended for per-site activation. Network-enable only after testing; use separate Bunny libraries, zones, and Pull Zones per site when you need isolation.

= Where is developer documentation? =

Hook, filter, REST, and meta reference: see PHPDoc in the [GitHub repository](https://github.com/indigetal/media-offload-for-bunny). Build from source: clone the repository and run `npm run package`.

= Does Free support every Bunny video container? =

Free supports formats WordPress allows on the default upload path. It does not add MIME support for `.vod`, `.ts`, `.amv`, or literal `.4mv`. Stream attachment URLs use Bunny MP4 fallback shape (`play_720p.mp4`); enable MP4 fallback on the Stream library before upload.

== Privacy ==

This plugin sends media and configuration-related data to **Bunny.net** only when you enable Stream and/or Storage and use the workflows above. Bunny.net terms and privacy policy: https://bunny.net/tos/ — https://bunny.net/privacy/

**Stream (when enabled):** Your server requests Bunny Stream API hosts such as `video.bunnycdn.com`. Playback URLs may use `player.mediadelivery.net` and your Stream Pull Zone hostname.

**Storage (when enabled):** Your server requests the regional Bunny Storage API for your zone. Public file URLs use your Storage Pull Zone hostname.

**Credentials:** API keys and related options are stored in the WordPress database (encrypted where this plugin applies encryption) and used only to contact Bunny on your behalf.

**Delivery scope (Free):** This release does not generate HMAC-signed or token-authenticated CDN URLs from PHP. Access control depends on your Bunny Pull Zone, Storage, and Stream configuration.

**Deleting content:** Removing a WordPress attachment can remove linked Bunny objects. Uninstall retention is summarized on **About & Privacy** and in the FAQ above.

== Changelog ==

= 1.0.5 =
* Broader Stream upload format validation for WordPress default-path uploads.
* Documentation clarifications for supported formats and MP4 fallback attachment URLs.

= 1.0.4 =
* Document Pro-only private-delivery contract; Stream URL filter adds `context => primary` for MP4 attachment URLs.

= 1.0.3 =
* Stricter Stream collection list-before-create behavior; documented add-on collection resolver API.

= 1.0.2 =
* Stream collection validation against Bunny; paginated collection listing for libraries with 100+ collections.

Older releases: see the [GitHub repository](https://github.com/indigetal/media-offload-for-bunny) commit history.

== Upgrade Notice ==

= 1.0.5 =
Stream format alignment release. No settings migration required.

= 1.0.4 =
Developer alignment for Pro private-delivery integrations. Free behavior unchanged.

= 1.0.3 =
Stream collection hardening. No settings migration required.
