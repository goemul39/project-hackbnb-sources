import re
from flask import Blueprint, request, send_from_directory

uploads_api = Blueprint('uploads', __name__)

ALLOWED_UPLOAD_NAME = re.compile(r"[A-Za-z0-9._-]+\.(jpg|jpeg|png|webp)")

@uploads_api.route('/')
def get_upload():
   name = request.args.get("name", "")
   if not ALLOWED_UPLOAD_NAME.fullmatch(name):
      return {'error': 'Invalid file name'}, 400
   return send_from_directory('uploads', name)
 