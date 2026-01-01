"""
response.py

Utilities for standardized API responses in Flask.
"""

from flask import jsonify


def json_response(data=None, status=200, message=None, **kwargs):
    """
    Return a standard JSON response.

    Args:
        data (dict or list, optional): The main data payload.
        status (int): HTTP status code.
        message (str, optional): Optional message.
        **kwargs: Additional fields to include.

    Returns:
        Flask Response: JSON response.
    """
    response = {
        "success": 200 <= status < 300,
        "data": data,
        "message": message,
    }
    response.update(kwargs)
    return jsonify(response), status


def error_response(message, status=400, errors=None, **kwargs):
    """
    Return a standard error JSON response.

    Args:
        message (str): Error message.
        status (int): HTTP status code.
        errors (dict or list, optional): Additional error details.
        **kwargs: Additional fields to include.

    Returns:
        Flask Response: JSON response.
    """
    response = {
        "success": False,
        "error": {
            "message": message,
            "details": errors,
        },
    }
    response.update(kwargs)
    return jsonify(response), status


def paginated_response(
    items, total, page, per_page, status=200, message=None, **kwargs
):
    """
    Return a paginated JSON response.

    Args:
        items (list): List of items for the current page.
        total (int): Total number of items.
        page (int): Current page number.
        per_page (int): Items per page.
        status (int): HTTP status code.
        message (str, optional): Optional message.
        **kwargs: Additional fields to include.

    Returns:
        Flask Response: JSON response.
    """
    response = {
        "success": 200 <= status < 300,
        "data": items,
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        },
        "message": message,
    }
    response.update(kwargs)
    return jsonify(response), status
