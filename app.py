import os
from flask import Flask, request, make_response, jsonify,json
from flask_migrate import Migrate
from models import db
#from flask_restful import Resource,Api
from werkzeug.exceptions import HTTPException
from models import User, Campaign, Donations, Updates

migrate = Migrate()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Fundconnect.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)
