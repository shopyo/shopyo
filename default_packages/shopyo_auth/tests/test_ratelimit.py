"""
Elite Tests for Brute-force Protection (Rate Limiting).
Verifies that the system can handle traffic spikes and correctly throttles malicious actors.
"""

import pytest
from flask import url_for
from shopyo_auth import limiter


class TestRateLimiting:
    """Verifies the rate limiting subsystem."""

    @pytest.fixture(autouse=True)
    def reset_limiter(self, flask_app):
        """Ensure each test starts with a clean rate limit bucket."""
        with flask_app.app_context():
            # Only reset if storage is initialized
            if hasattr(limiter, "_storage") and limiter._storage:
                limiter.storage.reset()

    def test_limiter_disabled(self, test_client, flask_app):
        """Verify system does not throttle when disabled."""
        flask_app.config["SHOPYO_AUTH_RATE_LIMIT_ENABLED"] = False
        limiter.enabled = False

        # Should handle high volume without error
        for _ in range(10):
            response = test_client.get(url_for("shopyo_auth.login"))
            assert response.status_code == 200

    def test_limiter_blocks_excessive_requests(self, test_client, flask_app):
        """Verify system throttles after reaching the configured limit."""
        flask_app.config["SHOPYO_AUTH_RATE_LIMIT_ENABLED"] = True
        flask_app.config["SHOPYO_AUTH_RATE_LIMIT"] = "3 per minute"
        limiter.enabled = True

        # 1-3: Success
        for _ in range(3):
            assert test_client.get(url_for("shopyo_auth.login")).status_code == 200

        # 4: Throttled
        response = test_client.get(url_for("shopyo_auth.login"))
        assert response.status_code == 429
        assert any(
            msg in response.data
            for msg in [
                b"Too Many Requests",
                b"Too many requests",
                b"Rate limit exceeded",
            ]
        )

    def test_limiter_isolation_per_endpoint(self, test_client, flask_app):
        """Verify that hitting the limit on one endpoint doesn't block others."""
        flask_app.config["SHOPYO_AUTH_RATE_LIMIT_ENABLED"] = True
        flask_app.config["SHOPYO_AUTH_RATE_LIMIT"] = "2 per minute"
        limiter.enabled = True

        # Exhaust login
        for _ in range(2):
            test_client.get(url_for("shopyo_auth.login"))

        assert test_client.get(url_for("shopyo_auth.login")).status_code == 429

        # Register should still be accessible
        assert test_client.get(url_for("shopyo_auth.register")).status_code == 200
