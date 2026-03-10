# Shopyo Page

The `shopyo_page` package provides a flexible CMS-like page management system for Shopyo applications. It supports multi-language content, SEO metadata (descriptions and keywords), and custom layout templates.

## Features

- **Page Management:** Create, edit, and publish custom pages with ease.
- **Rich Text Editing:** Built-in Quill.js integration for formatted content.
- **Multi-language Support:** Manage different content versions for the same page slug.
- **Custom Templates:** Define custom layouts per-page or globally.
- **Theme Integration:** Automatically integrates with the active front-end theme (nav, footer, resources).

## Configuration

You can customize the module using the following configuration variables in your Shopyo `config.py`:

- `SHOPYO_PAGE_URL`: (Default: `/shopyo-page`) The base URL prefix for the module.
- `SHOPYO_PAGE_TEMPLATE`: (Default: `shopyo_page/view_page.html`) The default global template used to render pages if no per-page template is specified.

## Custom Templates

Shopyo Page allows for deep UI customization at two levels:

### 1. Global Override
Set `SHOPYO_PAGE_TEMPLATE` in your config to a template path relative to your theme or template folder.

### 2. Per-Page Template
In the page dashboard, you can specify a "Custom Template" path (e.g., `blogus/landing.html`).
- This path is relative to the template search paths.
- If using themes, place your template in `static/themes/front/[theme_name]/[template_name].html`.

## Usage

1.  Navigate to the **Page** module in the admin dashboard.
2.  Create a new page with a Title and Slug.
3.  Add content using the rich text editor.
4.  (Optional) Specify a custom template if you want a layout different from the default.
5.  View your page at `/shopyo-page/s/[slug]`.

---

### Changelog

- **1.3.0**: Added `SHOPYO_PAGE_TEMPLATE` config and per-page custom template selection.
- **1.2.0**: Added option `SHOPYO_PAGE_URL`.
