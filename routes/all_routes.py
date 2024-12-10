from flask import Blueprint, request, jsonify
from controllers.account_controller import (
    register_user, login_user, get_histories, get_profile, update_profile
)
from middleware.auth_middleware import authenticate_token

routes = Blueprint('routes', __name__)

# Account-related routes
routes.route('/register', methods=['POST'], endpoint='register_user')(register_user)
routes.route('/login', methods=['POST'], endpoint='login_user')(login_user)
routes.route('/histories', methods=['GET'], endpoint='get_histories')(authenticate_token(get_histories))
routes.route('/profile', methods=['GET'], endpoint='get_profile')(authenticate_token(get_profile))
routes.route('/profile/update', methods=['PUT'], endpoint='update_profile')(authenticate_token(update_profile))


