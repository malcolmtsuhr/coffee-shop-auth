import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    '''
    Testing - uncomment the following line to initialize the datbase
    !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
    !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
    '''
    db_drop_and_create_all()

# ----------------------------------------------------------------------------#
# Controllers
# ----------------------------------------------------------------------------#
    '''
    Endpoint to GET /drinks
            it should be a public endpoint
            it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
    or appropriate status code indicating reason for failure
    '''
    '''
    Endpoint to handle GET requests
    for all available drinks.
    Public endpoint
    '''
    @app.route('/drinks', methods=['GET'])
    def getDrinks():
        try:
            drinks = Drink.query.order_by(Drink.id).all()
            short_drinks = [d.short() for d in drinks]

            if len(short_drinks) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'drinks': short_drinks
            }), 200

        except Exception:
            abort(500)

    '''
    Endpoint to GET /drinks-detail
            it should require the 'get:drinks-detail' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks-detail', methods=['GET'])
    @requires_auth('get:drinks-detail')
    def getDrinksDetail(payload):
        try:
            drinks = Drink.query.order_by(Drink.id).all()
            long_drinks = [d.long() for d in drinks]

            if len(long_drinks) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'drinks': long_drinks
            }), 200

        except Exception:
            abort(500)

    '''
    Endpoint to POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where drink is an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks', methods=['POST'])
    @requires_auth('post:drinks')
    def post_drinks(payload):
        body = request.get_json()

        try:
            req_title = body.get("title", None)
            req_recipe = json.dumps(body.get('recipe', None))

            drink = Drink(
                title=req_title,
                recipe=req_recipe
                )
            drink.insert()

            return jsonify({
                'success': True,
                'drinks': [drink.long()]
            }), 200

        except BaseException:
            abort(422)

    '''
    Endpoint to PATCH /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should update the corresponding row for <id>
            it should require the 'patch:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the updated drink
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks/<int:drink_id>', methods=['PATCH'])
    @requires_auth('patch:drinks')
    def edit_drink(payload, drink_id):
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        body = request.get_json()

        req_title = body.get('title', None)
        req_recipe = json.dumps(body.get('recipe', None))

        try:
            if drink is None:
                abort(404)

            if 'title' in body:
                drink.title = req_title

            if 'recipe' in body:
                drink.recipe = req_recipe

            drink.update()

            format_drink = drink.long()

            return jsonify({
                'success': True,
                'drinks': [format_drink]
            }), 200

        except Exception:
            abort(422)

    '''
    Endpoint to DELETE /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should delete the corresponding row for <id>
            it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id}
        where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks/<int:drink_id>', methods=['DELETE'])
    @requires_auth('delete:drinks')
    def deleteDrinks(payload, drink_id):
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        try:
            if drink is None:
                abort(404)

            else:
                drink.delete()

                return jsonify({
                    'success': True,
                    'delete': drink_id
                }), 200

        except Exception:
            abort(422)

    '''
    Error handlers for
    AuthError, 400, 401, 403, 404, 405, 422, and 500.
    '''
    @app.errorhandler(AuthError)
    def authentification_error(AuthError):
        return jsonify({
            "success": False,
            "error": AuthError.status_code,
            "message": AuthError.error['description']
        }), AuthError.status_code

    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            'success': False,
            'error': 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        return jsonify({
            'success': False,
            'error': 401,
            "message": "Unauthorized",
            'description': error.description
        }), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        return jsonify({
            'success': False,
            'error': 403,
            "message": "Forbidden"
        }), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'success': False,
            'error': 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(405)
    def not_found_error(error):
        return jsonify({
            'success': False,
            'error': 405,
            "message": "Method Not Allowed"
        }), 405

    @app.errorhandler(422)
    def not_processable_error(error):
        return jsonify({
            'success': False,
            'error': 422,
            "message": "Not Processable"
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            "message": "Server Error"
        }), 500

    return app
