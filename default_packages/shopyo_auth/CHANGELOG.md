# Changelog

## v1.10.4 (2026-10-22)

- ✨ Security: password-reset and account-confirmation tokens now use distinct purpose-bound salts (`<PASSWORD_SALT>:email-confirm` / `<PASSWORD_SALT>:password-reset`) — a token received in one email can no longer be replayed for the other flow
- ✨ Security: password-reset tokens are single use — the payload carries a fingerprint of the current password state, so completing a reset (or any password change) instantly invalidates every outstanding reset link; previously links stayed valid and reusable for up to an hour after the password had already been changed
- ✨ Security: login sessions **and remember-me cookies** no longer survive a password change — the Flask-Login identity itself (`User.get_id()` → `<id>|<stamp>`) embeds the password state and `load_user` re-verifies it on every load; identities without credential state (legacy bare ids) are refused, forcing a one-time re-login after upgrade; the three competing `user_loader` registrations (`shopyo.init`, `shopyo_appadmin.admin`, `shopyo_auth.models`) now delegate to one canonical loader so import order cannot shadow the check
- ✨ Security: outbound email links (password reset, account confirmation) are built from the `APP_URL` configuration (new `absolute_url()` helper in shopyo core) instead of the request `Host` header — set `APP_URL` in the deployment environment in production; it falls back to `SERVER_NAME` and then to the request host for development
