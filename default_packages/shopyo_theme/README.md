# Shopyo Theme

The `shopyo_theme` package provides a robust theme management system for Shopyo applications. It allows administrators to easily switch between different front-end and back-end themes, enabling a customizable look and feel without altering the core application logic.

## Features

- **Theme Switching:** distinct management for Front (public-facing) and Back (admin-facing) themes.
- **Visual Interface:** A clean, card-based grid UI for browsing and activating themes.
- **Asset Management:** easy retrieval of theme-specific static assets (CSS, JS, images).
- **Metadata Support:** `info.json` support for theme metadata (author, version, description).

## Usage

### Managing Themes

1.  Log in to the Shopyo admin dashboard.
2.  Navigate to the **Theme** module (usually `/shopyo_theme` or via the sidebar).
3.  You will see two sections: **Front Themes** and **Back Themes**.
4.  Click **Activate** on any theme card to apply it instantly.

### Creating a New Theme

Themes are located in `static/themes/`.

**Structure:**

```text
static/
└── themes/
    ├── front/
    │   └── my_new_theme/
    │       ├── info.json
    │       └── styles.css
    └── back/
        └── my_admin_theme/
            ├── info.json
            └── styles.css
```

**info.json Example:**

```json
{
    "author": {
        "name": "Your Name",
        "email": "your@email.com"
    },
    "version": "1.0.0",
    "display_name": "My New Theme"
}
```

## Configuration

The active themes are stored in the application settings:
- `ACTIVE_FRONT_THEME`
- `ACTIVE_BACK_THEME`
