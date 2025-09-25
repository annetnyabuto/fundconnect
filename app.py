import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Resource, Api
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from models import db, User, Campaign, Donations, Updates
from flask_bcrypt import Bcrypt

migrate = Migrate()
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Fundconnect.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'supersecretkey'

db.init_app(app)
migrate.init_app(app, db)
api=Api(app)
bcrypt = Bcrypt(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Token is missing'}, 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return {'error': 'Invalid token'}, 401
        except jwt.ExpiredSignatureError:
            return {'error': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token'}, 401
        
        return f(current_user, *args, **kwargs)
    return decorated
    
class Login(Resource):
    def post(self):
        data = request.get_json()
        name = data.get('name')
        password = data.get('password')
        
        user = User.query.filter_by(name=name).first()
        
        if user and user.authenticate(password):
            token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, app.config['JWT_SECRET_KEY'], algorithm='HS256')
            
            return {
                'token': token,
                'user': user.to_dict()
            }, 200
        
        return {'error': 'Invalid credentials'}, 401
    
class Users(Resource):
    @token_required
    def get(self, current_user):
        users = User.query.all()
        return [user.to_dict() for user in users], 200
    
    def post(self):
        data = request.get_json()
        
        if not data or not data.get('name') or not data.get('password'):
            return {'error': 'Name and password are required'}, 400
            
        if User.query.filter_by(name=data['name']).first():
            return {'error': 'Username already exists'}, 409
            
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
    @token_required
    def get(self, current_user, id):
        user = User.query.get_or_404(id)
        return user.to_dict(), 200
    
    @token_required
    def patch(self, current_user, id):
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
    
    @token_required
    def delete(self, current_user, id):
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully'}, 200
    
class Checksession(Resource):
    @token_required
    def get(self, current_user):
        return current_user.to_dict(), 200
        
class Logout(Resource):
    def post(self):
        return {'message': 'Logout successful'}, 200
    
class Campaigns(Resource):
    @token_required
    def get(self, current_user):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        campaigns = Campaign.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'campaigns': [campaign.to_dict() for campaign in campaigns.items],
            'total': campaigns.total,
            'pages': campaigns.pages,
            'current_page': page
        }, 200
    
    @token_required
    def post(self, current_user):
        data = request.get_json()
        new_campaign = Campaign(
            category=data['category'],
            description=data['description'],
            targetamount=data['targetamount'],
            raisedamount=data.get('raisedamount', 0),
            user_id=current_user.id
        )
        db.session.add(new_campaign)
        db.session.commit()
        return {'message': 'Campaign created successfully', 'id': new_campaign.id}, 201

class CampaignDetail(Resource):
    @token_required
    def get(self, current_user, id):
        campaign = Campaign.query.get_or_404(id)
        return campaign.to_dict(), 200
    
    @token_required
    def patch(self, current_user, id):
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
    
    @token_required
    def delete(self, current_user, id):
        campaign = Campaign.query.get_or_404(id)
        db.session.delete(campaign)
        db.session.commit()
        return {'message': 'Campaign deleted successfully'}, 200

class DonationsResource(Resource):
    @token_required
    def get(self, current_user):
        donations = Donations.query.all()
        return [donation.to_dict() for donation in donations], 200
    
    @token_required
    def post(self, current_user):
        data = request.get_json()
        
        if not data.get('amount') or data['amount'] <= 0:
            return {'error': 'Valid donation amount required'}, 400
            
        campaign = Campaign.query.get_or_404(data['campaign_id'])
        
        new_donation = Donations(
            title=data['title'],
            paymentmethod=data['paymentmethod'],
            amount=data['amount'],
            user_id=current_user.id,
            campaign_id=data['campaign_id']
        )
        
        campaign.raisedamount = (campaign.raisedamount or 0) + data['amount']
        
        db.session.add(new_donation)
        db.session.commit()
        return {'message': 'Donation created successfully', 'id': new_donation.id}, 201

class DonationDetail(Resource):
    @token_required
    def get(self, current_user, id):
        donation = Donations.query.get_or_404(id)
        return donation.to_dict(), 200
    
    @token_required
    def delete(self, current_user, id):
        donation = Donations.query.get_or_404(id)
        db.session.delete(donation)
        db.session.commit()
        return {'message': 'Donation deleted successfully'}, 200

class CampaignDonations(Resource):
    @token_required
    def get(self, current_user, id):
        campaign = Campaign.query.get_or_404(id)
        donations = Donations.query.filter_by(campaign_id=id).all()
        return [donation.to_dict() for donation in donations], 200

class UserDonations(Resource):
    @token_required
    def get(self, current_user, id):
        user = User.query.get_or_404(id)
        donations = Donations.query.filter_by(user_id=id).all()
        return [donation.to_dict() for donation in donations], 200

class UpdatesResource(Resource):
    @token_required
    def get(self, current_user):
        updates = Updates.query.all()
        return [update.to_dict() for update in updates], 200
    
    @token_required
    def post(self, current_user):
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
    @token_required
    def get(self, current_user, id):
        update = Updates.query.get_or_404(id)
        return update.to_dict(), 200
    
    @token_required
    def patch(self, current_user, id):
        update = Updates.query.get_or_404(id)
        data = request.get_json()
        
        if 'title' in data:
            update.title = data['title']
        if 'description' in data:
            update.description = data['description']
            
        db.session.commit()
        return {'message': 'Update updated successfully'}, 200
    
    @token_required
    def delete(self, current_user, id):
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