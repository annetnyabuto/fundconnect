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

@app.route("/")
def index():
    return "<h1>Fundconnect running successfully</h1>"
    
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
    
#campaign routes
    
class Campaigns(Resource):
    def get(self):
        campaigns = Campaign.query.all()
        return [
            {
                "id": campaign.id,
                "category": campaign.category,
                "description": campaign.description,
                "targetamount": campaign.targetamount,
                "raisedamount": campaign.raisedamount,
                "user_id": campaign.user_id
            } for campaign in campaigns
        ], 200
    
    def post(self):
        data = request.get_json()
        new_campaign = Campaign(
            category=data['category'],
            description=data['description'],
            targetamount=data['targetamount'],
            raisedamount=data.get('raisedamount', 0),
            user_id=data['user_id']
        )
        db.session.add(new_campaign)
        db.session.commit()
        return {'message': 'Campaign created successfully', 'id': new_campaign.id}, 201

class CampaignDetail(Resource):
    def get(self, id):
        campaign = Campaign.query.get_or_404(id)
        return {
            "id": campaign.id,
            "category": campaign.category,
            "description": campaign.description,
            "targetamount": campaign.targetamount,
            "raisedamount": campaign.raisedamount,
            "user_id": campaign.user_id
        }, 200
    
    def patch(self, id):
        campaign = Campaign.query.get_or_404(id)
        data = request.get_json()
        
        if 'category' in data:
            campaign.category = data['category']
        if 'description' in data:
            campaign.description = data['description']
        if 'targetamount' in data:
            campaign.targetamount = data['targetamount']
        if 'raisedamount' in data:
            campaign.raisedamount = data['raisedamount']
            
        db.session.commit()
        return {'message': 'Campaign updated successfully'}, 200
    
    def delete(self, id):
        campaign = Campaign.query.get_or_404(id)
        db.session.delete(campaign)
        db.session.commit()
        return {'message': 'Campaign deleted successfully'}, 200

class DonationsResource(Resource):
    def get(self):
        donations = Donations.query.all()
        return [
            {
                "id": donation.id,
                "title": donation.title,
                "paymentmethod": donation.paymentmethod,
                "amount": donation.amount,
                "user_id": donation.user_id,
                "campaign_id": donation.campaign_id
            } for donation in donations
        ], 200
    
    def post(self):
        data = request.get_json()
        new_donation = Donations(
            title=data['title'],
            paymentmethod=data['paymentmethod'],
            amount=data['amount'],
            user_id=data['user_id'],
            campaign_id=data['campaign_id']
        )
        db.session.add(new_donation)
        db.session.commit()
        return {'message': 'Donation created successfully', 'id': new_donation.id}, 201

class DonationDetail(Resource):
    def get(self, id):
        donation = Donations.query.get_or_404(id)
        return {
            "id": donation.id,
            "title": donation.title,
            "paymentmethod": donation.paymentmethod,
            "amount": donation.amount,
            "user_id": donation.user_id,
            "campaign_id": donation.campaign_id
        }, 200
    
    def delete(self, id):
        donation = Donations.query.get_or_404(id)
        db.session.delete(donation)
        db.session.commit()
        return {'message': 'Donation deleted successfully'}, 200

class CampaignDonations(Resource):
    def get(self, id):
        campaign = Campaign.query.get_or_404(id)
        donations = Donations.query.filter_by(campaign_id=id).all()
        return [
            {
                "id": donation.id,
                "title": donation.title,
                "paymentmethod": donation.paymentmethod,
                "amount": donation.amount,
                "user_id": donation.user_id
            } for donation in donations
        ], 200

class UserDonations(Resource):
    def get(self, id):
        user = User.query.get_or_404(id)
        donations = Donations.query.filter_by(user_id=id).all()
        return [
            {
                "id": donation.id,
                "title": donation.title,
                "paymentmethod": donation.paymentmethod,
                "amount": donation.amount,
                "campaign_id": donation.campaign_id
            } for donation in donations
        ], 200

class UpdatesResource(Resource):
    def get(self):
        updates = Updates.query.all()
        return [
            {
                "id": update.id,
                "title": update.title,
                "description": update.description,
                "campaign_id": update.campaign_id
            } for update in updates
        ], 200
    
    def post(self):
        data = request.get_json()
        new_update = Updates(
            title=data['title'],
            description=data['description'],
            campaign_id=data['campaign_id']
        )
        db.session.add(new_update)
        db.session.commit()
        return {'message': 'Update created successfully', 'id': new_update.id}, 201

class UpdateDetail(Resource):
    def get(self, id):
        update = Updates.query.get_or_404(id)
        return {
            "id": update.id,
            "title": update.title,
            "description": update.description,
            "campaign_id": update.campaign_id
        }, 200
    
    def patch(self, id):
        update = Updates.query.get_or_404(id)
        data = request.get_json()
        
        if 'title' in data:
            update.title = data['title']
        if 'description' in data:
            update.description = data['description']
            
        db.session.commit()
        return {'message': 'Update updated successfully'}, 200
    
    def delete(self, id):
        update = Updates.query.get_or_404(id)
        db.session.delete(update)
        db.session.commit()
        return {'message': 'Update deleted successfully'}, 200

api.add_resource(Checksession,'/check', endpoint="check")
api.add_resource(Login, '/login',endpoint="login")
api.add_resource(Logout,'/logout', endpoint="logout")
api.add_resource(Users, '/users')
api.add_resource(UserDetail, '/users/<int:id>')
api.add_resource(Campaigns, '/campaigns')
api.add_resource(CampaignDetail, '/campaigns/<int:id>')
api.add_resource(DonationsResource, '/donations')
api.add_resource(DonationDetail, '/donations/<int:id>')
api.add_resource(CampaignDonations, '/campaigns/<int:id>/donations')
api.add_resource(UserDonations, '/users/<int:id>/donations')
api.add_resource(UpdatesResource, '/updates')
api.add_resource(UpdateDetail, '/updates/<int:id>')

if __name__ == '__main__':
    app.run(debug=True)