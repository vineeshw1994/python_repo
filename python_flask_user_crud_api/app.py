# app.py
from quart import Quart, send_from_directory
from routes.user_routes import user_bp
import os

app = Quart(__name__)
app.register_blueprint(user_bp, url_prefix='/api')

# Serve uploaded images
@app.route('/uploads/<filename>')
async def uploaded_file(filename):
    return await send_from_directory('uploads', filename)

if __name__ == '__main__':
    app.run(port=5000, debug=True)