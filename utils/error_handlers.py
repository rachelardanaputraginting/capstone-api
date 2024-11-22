from flask import jsonify
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError

def register_error_handlers(app):
    @app.errorhandler(NoAuthorizationError)
    def handle_no_authorization_error(e):
        return jsonify({
            "status": False,
            "message": "Missing Authorization Header. Please provide a valid token."
        }), 401

    @app.errorhandler(InvalidHeaderError)
    def handle_invalid_header_error(e):
        return jsonify({
            "status": False,
            "message": "Invalid Authorization Header. Please check the token format."
        }), 401
