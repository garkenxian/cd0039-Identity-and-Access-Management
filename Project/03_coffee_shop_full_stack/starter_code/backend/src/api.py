import os
from flask import Flask, request, jsonify, abort
from werkzeug.exceptions import HTTPException
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# Database initialization (uncomment on first run to populate with test data)
# db_drop_and_create_all()

# ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    """
    GET /drinks
    Public endpoint to retrieve all drinks in short format.
    
    Returns:
        200 with list of drinks in short format
        422 if response construction fails
    """
    try:
        drinks = Drink.query.all()
        drinks_short = [drink.short() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": drinks_short
        }), 200
    except HTTPException:
        raise
    except Exception as e:
        abort(422)


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    """
    GET /drinks-detail
    Secured endpoint requiring 'get:drinks-detail' permission.
    Returns drinks in long format with full recipe details.
    
    Args:
        payload: Decoded JWT payload from auth decorator
    
    Returns:
        200 with list of drinks in long format
        401 for missing/invalid/expired token
        403 for insufficient permissions
    """
    try:
        drinks = Drink.query.all()
        drinks_long = [drink.long() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": drinks_long
        }), 200
    except HTTPException:
        raise
    except Exception as e:
        abort(422)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    """
    POST /drinks
    Secured endpoint requiring 'post:drinks' permission.
    Creates a new drink with provided title and recipe.
    
    Args:
        payload: Decoded JWT payload from auth decorator
    
    Request body:
        {
            "title": "string",
            "recipe": [{"name": "string", "color": "string", "parts": number}]
        }
    
    Returns:
        200 with newly created drink in long format
        400 for malformed body
        401 for missing/invalid/expired token
        403 for insufficient permissions
        422 for validation/insert errors
    """
    try:
        body = request.get_json()
        
        if not body:
            abort(400)
        
        title = body.get('title')
        recipe = body.get('recipe')
        
        if not title or not recipe:
            abort(400)
        
        # Validate recipe is a list
        if not isinstance(recipe, list):
            abort(400)
        
        # Convert recipe to JSON string
        recipe_str = json.dumps(recipe)
        
        drink = Drink(title=title, recipe=recipe_str)
        drink.insert()
        
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    
    except HTTPException:
        raise
    except exc.IntegrityError:
        # Handle duplicate title
        abort(422)
    except (ValueError, KeyError):
        abort(400)
    except Exception as e:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    """
    PATCH /drinks/<id>
    Secured endpoint requiring 'patch:drinks' permission.
    Updates an existing drink's title and/or recipe.
    
    Args:
        payload: Decoded JWT payload from auth decorator
        drink_id: ID of drink to update
    
    Request body:
        {
            "title": "string" (optional),
            "recipe": [...] (optional)
        }
    
    Returns:
        200 with updated drink in long format
        400 for invalid id/body
        401 for missing/invalid/expired token
        403 for insufficient permissions
        404 if drink id not found
        422 for update failures
    """
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        
        if not drink:
            abort(404)
        
        body = request.get_json()
        
        if not body:
            abort(400)
        
        if 'title' in body:
            drink.title = body.get('title')
        
        if 'recipe' in body:
            recipe = body.get('recipe')
            if not isinstance(recipe, list):
                abort(400)
            drink.recipe = json.dumps(recipe)
        
        drink.update()
        
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    
    except HTTPException:
        raise
    except exc.IntegrityError:
        # Handle duplicate title
        abort(422)
    except (ValueError, KeyError):
        abort(400)
    except Exception as e:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    """
    DELETE /drinks/<id>
    Secured endpoint requiring 'delete:drinks' permission.
    Deletes the specified drink.
    
    Args:
        payload: Decoded JWT payload from auth decorator
        drink_id: ID of drink to delete
    
    Returns:
        200 with deleted drink ID
        400 for invalid id
        401 for missing/invalid/expired token
        403 for insufficient permissions
        404 if drink id not found
    """
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        
        if not drink:
            abort(404)
        
        drink.delete()
        
        return jsonify({
            "success": True,
            "delete": drink_id
        }), 200
    
    except HTTPException:
        raise
    except Exception as e:
        abort(422)


# Error Handling

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(AuthError)
def handle_auth_error(error):
    """
    Handle AuthError exceptions raised by auth module.
    Maps to appropriate HTTP status code and returns structured JSON.
    """
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error.get('description', 'Authentication failed')
    }), error.status_code
