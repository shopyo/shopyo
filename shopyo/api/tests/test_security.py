"""
Tests for the API security functionality
"""

import pytest
from flask import Flask, request, session
from werkzeug.exceptions import Forbidden

from shopyo.api.security import (
    is_safe_redirect_url,
    get_safe_redirect,
    generate_csrf_token,
    validate_csrf_token,
    get_csrf_token_from_request,
    csrf_protect,
    inject_csrf_token,
    CSRF_TOKEN_HEADER,
    CSRF_TOKEN_FORM_KEY
)

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    return app

def test_is_safe_redirect_url_same_host(app):
    """Test safe redirect URL with same host"""
    with app.test_request_context('http://localhost/'):
        assert is_safe_redirect_url('/dashboard') is True
        assert is_safe_redirect_url('http://localhost/dashboard') is True

def test_is_safe_redirect_url_different_host(app):
    """Test safe redirect URL with different host"""
    with app.test_request_context('http://localhost/'):
        assert is_safe_redirect_url('http://evil.com/dashboard') is False

def test_get_safe_redirect_safe_url(app):
    """Test getting safe redirect URL"""
    with app.test_request_context('http://localhost/'):
        assert get_safe_redirect('/dashboard') == '/dashboard'

def test_get_safe_redirect_unsafe_url(app):
    """Test getting safe redirect URL for unsafe URL"""
    with app.test_request_context('http://localhost/'):
        assert get_safe_redirect('http://evil.com/dashboard') == '/'

def test_get_safe_redirect_with_referrer(app):
    """Test getting safe redirect URL with referrer"""
    with app.test_request_context('http://localhost/', headers={'Referer': 'http://localhost/login'}):
        assert get_safe_redirect('http://evil.com/dashboard') == 'http://localhost/login'

def test_generate_csrf_token(app):
    """Test CSRF token generation"""
    with app.test_request_context():
        token1 = generate_csrf_token()
        token2 = generate_csrf_token()
        assert token1 == token2  # Same token should be returned from session
        assert len(token1) == 86  # Length of secrets.token_urlsafe(64)

def test_validate_csrf_token(app):
    """Test CSRF token validation"""
    with app.test_request_context():
        token = generate_csrf_token()
        assert validate_csrf_token(token) is True
        assert validate_csrf_token('invalid-token') is False
        assert validate_csrf_token(None) is False

def test_get_csrf_token_from_request_header(app):
    """Test getting CSRF token from header"""
    with app.test_request_context(headers={CSRF_TOKEN_HEADER: 'test-token'}):
        assert get_csrf_token_from_request() == 'test-token'

def test_get_csrf_token_from_request_form(app):
    """Test getting CSRF token from form"""
    with app.test_request_context(data={CSRF_TOKEN_FORM_KEY: 'test-token'}):
        assert get_csrf_token_from_request() == 'test-token'

def test_get_csrf_token_from_request_json(app):
    """Test getting CSRF token from JSON"""
    with app.test_request_context(json={CSRF_TOKEN_FORM_KEY: 'test-token'}):
        assert get_csrf_token_from_request() == 'test-token'

def test_csrf_protect_safe_method(app):
    """Test CSRF protection with safe method"""
    @csrf_protect
    def test_view():
        return 'success'
    
    with app.test_request_context(method='GET'):
        assert test_view() == 'success'

def test_csrf_protect_unsafe_method_no_token(app):
    """Test CSRF protection with unsafe method and no token"""
    @csrf_protect
    def test_view():
        return 'success'
    
    with app.test_request_context(method='POST'):
        with pytest.raises(Forbidden):
            test_view()

def test_csrf_protect_unsafe_method_valid_token(app):
    """Test CSRF protection with unsafe method and valid token"""
    @csrf_protect
    def test_view():
        return 'success'
    
    with app.test_request_context():
        token = generate_csrf_token()
        with app.test_request_context(method='POST', headers={CSRF_TOKEN_HEADER: token}):
            assert test_view() == 'success'

def test_inject_csrf_token(app):
    """Test injecting CSRF token into template context"""
    with app.test_request_context():
        context = inject_csrf_token()
        assert CSRF_TOKEN_FORM_KEY in context
        assert isinstance(context[CSRF_TOKEN_FORM_KEY], str)
        assert len(context[CSRF_TOKEN_FORM_KEY]) == 86
