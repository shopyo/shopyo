"""
Tests for the API response functionality
"""

import pytest
from flask import Flask

from shopyo.api.response import json_response, error_response, paginated_response

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

def test_json_response_success(app):
    """Test successful JSON response"""
    with app.test_request_context():
        response, status = json_response(
            data={'test': 'data'},
            message='Success',
            extra='field'
        )
        assert status == 200
        assert response.json['success'] is True
        assert response.json['data'] == {'test': 'data'}
        assert response.json['message'] == 'Success'
        assert response.json['extra'] == 'field'

def test_json_response_error_status(app):
    """Test JSON response with error status"""
    with app.test_request_context():
        response, status = json_response(
            data={'error': 'data'},
            status=400,
            message='Error'
        )
        assert status == 400
        assert response.json['success'] is False
        assert response.json['data'] == {'error': 'data'}
        assert response.json['message'] == 'Error'

def test_error_response(app):
    """Test error response"""
    with app.test_request_context():
        response, status = error_response(
            message='Validation failed',
            status=400,
            errors=['Invalid field'],
            extra='field'
        )
        assert status == 400
        assert response.json['success'] is False
        assert response.json['error']['message'] == 'Validation failed'
        assert response.json['error']['details'] == ['Invalid field']
        assert response.json['extra'] == 'field'

def test_paginated_response(app):
    """Test paginated response"""
    with app.test_request_context():
        items = [{'id': 1}, {'id': 2}]
        response, status = paginated_response(
            items=items,
            total=10,
            page=1,
            per_page=2,
            message='Success',
            extra='field'
        )
        assert status == 200
        assert response.json['success'] is True
        assert response.json['data'] == items
        assert response.json['pagination']['total'] == 10
        assert response.json['pagination']['page'] == 1
        assert response.json['pagination']['per_page'] == 2
        assert response.json['pagination']['pages'] == 5
        assert response.json['message'] == 'Success'
        assert response.json['extra'] == 'field'

def test_paginated_response_last_page(app):
    """Test paginated response on last page"""
    with app.test_request_context():
        items = [{'id': 9}, {'id': 10}]
        response, status = paginated_response(
            items=items,
            total=10,
            page=5,
            per_page=2
        )
        assert status == 200
        assert response.json['pagination']['pages'] == 5
        assert response.json['pagination']['page'] == 5 