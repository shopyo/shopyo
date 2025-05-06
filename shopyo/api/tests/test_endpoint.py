"""
Tests for the API endpoint functionality
"""

import pytest
from flask import Flask
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from shopyo.api.models import YoModel
from shopyo.api.endpoint import APIEndpoint, api_endpoint

Base = declarative_base()

class TestModel(YoModel, Base):
    __tablename__ = 'test_model'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(String(200))

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        Base.metadata.create_all(app.extensions['sqlalchemy'].db.engine)
        yield app

@pytest.fixture
def endpoint(app):
    return APIEndpoint(TestModel)

def test_validate_request(endpoint):
    """Test the default validate_request method returns empty list"""
    assert endpoint.validate_request({}) == []

def test_format_response(endpoint):
    """Test the default format_response method returns data as is"""
    data = {'test': 'data'}
    assert endpoint.format_response(data) == data

def test_get_query_filters(endpoint):
    """Test the default get_query_filters method returns empty dict"""
    assert endpoint.get_query_filters() == {}

def test_handle_list_empty(endpoint, app):
    """Test handling empty list request"""
    with app.test_request_context():
        response = endpoint.handle_list()
        assert response[1] == 200
        assert response[0]['items'] == []
        assert response[0]['total'] == 0

def test_handle_create(endpoint, app):
    """Test creating a new item"""
    with app.test_request_context(json={'name': 'Test', 'description': 'Test Description'}):
        response = endpoint.handle_create()
        assert response[1] == 201
        assert response[0]['data']['name'] == 'Test'
        assert response[0]['data']['description'] == 'Test Description'

def test_handle_create_no_data(endpoint, app):
    """Test creating with no data"""
    with app.test_request_context():
        response = endpoint.handle_create()
        assert response[1] == 400
        assert 'No data provided' in response[0]['message']

def test_handle_get_not_found(endpoint, app):
    """Test getting non-existent item"""
    with app.test_request_context():
        response = endpoint.handle_get(999)
        assert response[1] == 404
        assert 'Item not found' in response[0]['message']

def test_handle_update_not_found(endpoint, app):
    """Test updating non-existent item"""
    with app.test_request_context(json={'name': 'Updated'}):
        response = endpoint.handle_update(999)
        assert response[1] == 404
        assert 'Item not found' in response[0]['message']

def test_handle_delete_not_found(endpoint, app):
    """Test deleting non-existent item"""
    with app.test_request_context():
        response = endpoint.handle_delete(999)
        assert response[1] == 404
        assert 'Item not found' in response[0]['message']

def test_api_endpoint_decorator(app):
    """Test the api_endpoint decorator"""
    @api_endpoint(TestModel)
    def test_route(endpoint, *args, **kwargs):
        return endpoint
    
    result = test_route()
    assert isinstance(result, APIEndpoint)
    assert result.model_class == TestModel 