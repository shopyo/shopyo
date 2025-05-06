"""
Tests for the API validators functionality
"""

import os
import pytest
from wtforms import Form, StringField
from wtforms.validators import ValidationError

from shopyo.api.validators import (
    get_module_path_if_exists,
    is_alpha_num_underscore,
    is_empty_str,
    is_valid_slug,
    is_valid_url,
    verify_slug
)

class TestForm(Form):
    slug = StringField('Slug', validators=[verify_slug])

def test_is_alpha_num_underscore():
    """Test alphanumeric and underscore validation"""
    assert is_alpha_num_underscore('abc123') is True
    assert is_alpha_num_underscore('abc_123') is True
    assert is_alpha_num_underscore('abc-123') is False
    assert is_alpha_num_underscore('abc 123') is False
    assert is_alpha_num_underscore('') is False

def test_is_empty_str():
    """Test empty string validation"""
    assert is_empty_str('') is True
    assert is_empty_str('   ') is True
    assert is_empty_str('  test  ') is False
    assert is_empty_str('test') is False

def test_is_valid_slug():
    """Test slug validation"""
    assert is_valid_slug('valid-slug') is True
    assert is_valid_slug('valid_slug') is True
    assert is_valid_slug('valid-slug-123') is True
    assert is_valid_slug('invalid slug') is False
    assert is_valid_slug('invalid@slug') is False
    assert is_valid_slug('') is False

def test_is_valid_url():
    """Test URL validation"""
    # Valid URLs
    assert is_valid_url('http://example.com') is True
    assert is_valid_url('https://example.com') is True
    assert is_valid_url('http://example.com/path') is True
    assert is_valid_url('http://example.com:8080') is True
    assert is_valid_url('http://localhost') is True
    assert is_valid_url('http://127.0.0.1') is True
    assert is_valid_url('http://[::1]') is True
    
    # Invalid URLs
    assert is_valid_url('not-a-url') is False
    assert is_valid_url('http://') is False
    assert is_valid_url('ftp://') is False
    assert is_valid_url('') is False

def test_verify_slug():
    """Test slug verification in form"""
    form = TestForm()
    
    # Valid slugs
    form.slug.data = 'valid-slug'
    form.validate()
    assert form.errors == {}
    
    form.slug.data = 'valid_slug'
    form.validate()
    assert form.errors == {}
    
    # Invalid slugs
    form.slug.data = 'invalid slug'
    form.validate()
    assert 'slug' in form.errors
    
    form.slug.data = 'invalid@slug'
    form.validate()
    assert 'slug' in form.errors

def test_get_module_path_if_exists(tmp_path):
    """Test module path existence check"""
    # Create test directory structure
    modules_dir = tmp_path / 'modules'
    modules_dir.mkdir()
    
    # Create a module
    test_module = modules_dir / 'test_module'
    test_module.mkdir()
    
    # Create a submodule
    submodule = modules_dir / 'parent_module' / 'test_module'
    submodule.parent.mkdir()
    submodule.mkdir()
    
    # Change to test directory
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    
    try:
        # Test finding module
        assert get_module_path_if_exists('test_module') == str(test_module)
        
        # Test finding submodule
        assert get_module_path_if_exists('test_module') == str(test_module)
        
        # Test non-existent module
        assert get_module_path_if_exists('non_existent') is None
    finally:
        os.chdir(old_cwd)
