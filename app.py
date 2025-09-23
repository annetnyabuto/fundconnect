import os
from flask import Flask, session, request, make_response, jsonify,json
from flask_migrate import Migrate
from models import db
from flask_restful import Resource,Api
from werkzeug.exceptions import HTTPException
from models import User, Campaign, Donations, Updates
from flask_bcrypt import Bcrypt

migrate = Migrate()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Fundconnect.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)
api=Api(app)
bcrypt = Bcrypt(app)

@app.before_request
def check_authorized():
    #checks if user is logged in
    if 'user_id' not in session\
        and request.endpoint not in ("login", "signup"):
        return {"error":"401:unauthorised"}
    
class User(Resource):
    #register users
    def post(self):
        user_data = request.json
    