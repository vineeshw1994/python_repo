# routes/user_routes.py
from quart import Blueprint, request, jsonify
from controllers.user_controller import signup, login, update_profile
from functools import wraps
import jwt
from config.db import users
from bson import ObjectId

user_bp = Blueprint('user', __name__)
SECRET_KEY = "your-super-secret-jwt-key"

def token_required(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token missing"}), 401
        try:
            data = jwt.decode(token.replace("Bearer ", ""), SECRET_KEY, algorithms=["HS256"])
            user_id = ObjectId(data["user_id"])
            user = await users.find_one({"_id": user_id})
            if not user:
                return jsonify({"error": "Invalid token"}), 401
            request.user_id = user_id
        except:
            return jsonify({"error": "Invalid token"}), 401
        return await f(*args, **kwargs)
    return decorated

@user_bp.route('/signup', methods=['POST'])
async def signup_route():
    files = await request.files
    data = await request.form
    file = files.get('profile_pic')
    result, status = await signup(data, file)
    return jsonify(result), status

@user_bp.route('/login', methods=['POST'])
async def login_route():
    data = await request.get_json()
    result, status = await login(data)
    return jsonify(result), status

@user_bp.route('/profile', methods=['PUT'])
@token_required
async def update_profile_route():
    files = await request.files
    data = await request.form
    file = files.get('profile_pic')
    result, status = await update_profile(request.user_id, data, file)
    return jsonify(result), status

@user_bp.route('/logout', methods=['POST'])
@token_required
async def logout_route():
    # JWT is stateless → just tell frontend to delete token
    return jsonify({"message": "Logged out"}), 200