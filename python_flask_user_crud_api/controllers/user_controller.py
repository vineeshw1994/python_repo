# controllers/user_controller.py
import bcrypt
import jwt
import os
import aiofiles
from datetime import datetime, timedelta
from config.db import users
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
SECRET_KEY = "your-super-secret-jwt-key"
JWT_EXPIRY_HOURS = 24

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

async def signup(data, file=None):
    try:
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")

        if not email or not password:
            return {"error": "Email and password required"}, 400

        existing = await users.find_one({"email": email})
        if existing:
            return {"error": "User already exists"}, 409

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        profile_pic = None

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(await file.read())
            profile_pic = f"/uploads/{filename}"

        user_doc = {
            "email": email,
            "password": hashed,
            "name": name,
            "profile_pic": profile_pic,
            "created_at": datetime.utcnow()
        }
        result = await users.insert_one(user_doc)
        user_doc.pop("password")
        user_doc["_id"] = str(result.inserted_id)
        return user_doc, 201

    except Exception as e:
        return {"error": str(e)}, 500


# controllers/user_controller.py

async def login(data):
    try:
        email = data.get("email")
        password = data.get("password")

        # Validate input (this is CRITICAL)
        if not email or not password:
            return {
                "status": False,
                "message": "Email and password are required"
            }, 400

        user = await users.find_one({"email": email})
        if not user or not bcrypt.checkpw(password.encode(), user["password"]):
            return {
                "status": False,
                "message": "Invalid credentials"
            }, 401

        # Generate JWT
        token = jwt.encode({
            "user_id": str(user["_id"]),
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
        }, SECRET_KEY, algorithm="HS256")

        return {
            "status": True,
            "message": "Login successful",
            "token": token,
            "user": {
                "id": str(user["_id"]),
                "email": user["email"],
                "name": user.get("name")  # Safe access
            }
        }, 200

    except Exception as e:
        return {
            "status": False,
            "message": "Server error"
        }, 500


async def update_profile(user_id, data, file=None):
    try:
        update_fields = {}
        if "name" in data:
            update_fields["name"] = data["name"]

        old_user = await users.find_one({"_id": user_id})
        old_pic = old_user.get("profile_pic")

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(await file.read())
            update_fields["profile_pic"] = f"/uploads/{filename}"

            # Delete old image
            if old_pic and os.path.exists(old_pic[1:]):  # Remove leading "/"
                os.remove(old_pic[1:])

        if not update_fields:
            return {"error": "No data to update"}, 400

        await users.update_one({"_id": user_id}, {"$set": update_fields})
        updated = await users.find_one({"_id": user_id})
        updated["_id"] = str(updated["_id"])
        updated.pop("password", None)
        return updated, 200

    except Exception as e:
        return {"error": str(e)}, 500