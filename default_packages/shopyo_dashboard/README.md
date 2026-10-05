# shopyo_dashboard

The admin dashboard. It lists the modules and extensions of the project, some
recent activity, and basic system info.

The page is served at `/shopyo-dashboard/`. You need to be logged in, have
confirmed your email, and be an admin. Anyone else gets sent to the login
page.

## Configuration

```python
SHOPYO_DASHBOARD_URL = "/"  # defaults to "/shopyo-dashboard"
```

The value is read by `get_info()` and shows up as the module's URL on the
dashboard page, so if you change the prefix in your app the list shows the
new one.

## Changelog

- 1.2.0: Added the `SHOPYO_DASHBOARD_URL` option.
