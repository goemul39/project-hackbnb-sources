from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from database.init import db
from database.seed import seed_database

from api.rooms.rooms_models import Room
from api.rooms.rooms_api import rooms_api
from api.users.users_models import User
from api.users.users_api import users_api
from api.auth.auth_api import auth_api
from api.bookings.bookings_api import bookings_api
from api.bookings.bookings_models import Booking
from api.uploads.uploads_api import uploads_api


app = Flask(__name__)
app.config.from_pyfile('config.py')

# D8: no debug in prod, it leaks stack traces
app.config['DEBUG'] = False
app.config['PROPAGATE_EXCEPTIONS'] = False

# Add CORS to all requests
CORS(app, origins=app.config["CORS_ORIGINS"])

# Initialize database
db.init_app(app)
with app.app_context():
   db.create_all()
   seed_database()

# Routes
app.register_blueprint(rooms_api, url_prefix='/rooms')
app.register_blueprint(users_api, url_prefix='/users')
app.register_blueprint(auth_api, url_prefix='/auth')
app.register_blueprint(bookings_api, url_prefix='/bookings')
app.register_blueprint(uploads_api, url_prefix='/uploads')


@app.route('/', methods=['GET'])
def welcome():
   return "Welcome on API"


# D8: return a generic error instead of the traceback
@app.errorhandler(500)
def handle_internal_error(_error):
   db.session.rollback()
   return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(Exception)
def handle_unexpected_error(error):
   if isinstance(error, HTTPException):
      return error
   # Hide details from the user, but keep them in the server logs
   app.logger.exception(error)
   db.session.rollback()
   return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
   app.run(
      debug=False,
      host="0.0.0.0",
      port=9001,
   )
