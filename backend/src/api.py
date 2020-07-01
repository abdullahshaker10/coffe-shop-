import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from src.database.models import Drink

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()


@app.route('/drinks')
def reterive_drinks():
    try:
        drinks = Drink.query.all()
        drinks = [drink.short() for drink in drinks]
        print(drinks)
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(422)

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_details():
    try:
        drinks = Drink.query.all()
        drinks = [drink.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(422)


@app.route('/drinks', methods=['POST'])
@requires_auth('get:drinks-detail')
def add_new_drink():
    try:
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)
        print(recipe)
        drink = Drink(
            title=title,
            recipe=json.dumps(recipe),
        )
        drink.insert()
        drink = [drink.long()]
        return jsonify({
            'success': True,
            'drinks': drink
        })
    except:
        abort(422)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(id):
    try:
        drink = Drink.query.filter(
            Drink.id == id
        ).one_or_none()
        if not drink:
            abort(404)
        body = request.get_json()
        drink.title = body.get('title', drink.title)
        drink.recipe = body.get('recipe', drink.recipe)
        drink.update()
        drink = [drink.long()]
        return jsonify({
            'success': True,
            'drinks': drink
        })
    except:
        abort(422)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(id):
    try:
        drink = Drink.query.filter(
            Drink.id == id
        ).one_or_none()
        if not drink:
            abort(404)
        drink.delete()
        return jsonify({
            'success': True,
            'delete': id
        })
    except:
        abort(422)


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(401)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Not Authorized"
    }), 401
