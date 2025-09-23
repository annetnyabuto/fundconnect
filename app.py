import os
from flask import Flask, session, request, make_response, jsonify,json
from flask_migrate import Migrate
from flask_restful import Resource,Api
from werkzeug.exceptions import HTTPException
from models import db, User, Campaign, Donations, Updates
from flask_bcrypt import Bcrypt

migrate = Migrate()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Fundconnect.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)
api=Api(app)
bcrypt = Bcrypt(app)

app.secret_key = "supersecretkey"

@app.before_request
def check_authorized():
    #checks if user is logged in
    if 'user_id' not in session\
        and request.endpoint not in ("login", "signup"):
        return {"error":"401:unauthorised"}
    
class Login(Resource):
    def post(self):
        data = request.get_json()

        name = data.get("name")
        password = data.get("password")

        #Find user
        user = User.query.filter_by(name=name).first()

        if user and user.authenticate(password):
            session["user_id"] = user.id
            return user.to_dict(), 200
        
        return {"error": "name or password is incorrect"}, 401
    
class Users(Resource):
    def get(self):
        users = User.query.all()
        return [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "designation": user.designation
            } for user in users
        ], 200
    
    def post(self):
        data = request.get_json()
        new_user = User(
            name=data['name'], 
            email=data.get('email'),
            designation=data.get('designation')
        )
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User created successfully', 'id': new_user.id}, 201

class UserDetail(Resource):
    def get(self, id):
        user = User.query.get_or_404(id)
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "designation": user.designation
        }, 200
    
    def patch(self, id):
        user = User.query.get_or_404(id)
        data = request.get_json()
        
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        if 'designation' in data:
            user.designation = data['designation']
            
        db.session.commit()
        return {'message': 'User updated successfully'}, 200
    
    def delete(self, id):
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully'}, 200
    
class Checksession(Resource):
    def get(self):
        user= User.query.filter(User.id==session.get("user_id")).first()
        if user:
            return user.to_dict()
        else:
            return {"message":"401:unauthorised access"},401
        
class Logout(Resource):
    def get(self):
        session['user_id']=None
        return {"message":"Logout success"}
    
api.add_resource(Checksession,'/check', endpoint="check")
api.add_resource(Login, '/login',endpoint="login")
api.add_resource(Logout,'/logout', endpoint="logout")
api.add_resource(Users, '/users')
api.add_resource(UserDetail, '/users/<int:id>')