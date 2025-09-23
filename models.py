from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from flask_bcrypt import Bcrypt

bcryptt=Bcrypt()

metadata = MetaData()

db = SQLAlchemy(metadata=metadata)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    _password_hash = db.Column(db.String, nullable=False)
    designation = db.Column(db.String)

    
    campaigns = db.relationship('Campaign', backref='user')
    donations = db.relationship('Donations', backref='user')

    def __repr__(self):
        return f'<User {self.id}, {self.name}, {self.email}, {self.password}, {self.designation}>'

@hybrid_property
def password_hash(self):  
    return self._password_hash
    
@password_hash.setter
def password_hash(self,password):
    # Added encoding since this is needed for python3
    password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
    self._password_hash = password_hash.decode('utf-8')
 

def authenticate(self,password):
    # Added encoding since this is needed for python3
    return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

class Campaign(db.Model):
    __tablename__ = "campaign"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String)
    description = db.Column(db.String)
    targetamount = db.Column(db.Integer)
    raisedamount = db.Column(db.Integer)
    
    # Foreign key to User (many campaigns belong to one user)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    donations = db.relationship('Donations', backref='campaign', lazy=True)
    updates = db.relationship('Updates', backref='campaign', lazy=True)

    def __repr__(self):
        return f'<Campaign {self.id}, {self.category}, {self.description}, {self.targetamount}, {self.raisedamount}>'

class Donations(db.Model):
    __tablename__ = "donations"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    paymentmethod = db.Column(db.String)
    amount = db.Column(db.Integer)
    
    # Foreign keys (many donations belong to one user and one campaign)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)

    def __repr__(self):
        return f'<Donations {self.id}, {self.title}, {self.paymentmethod}, {self.amount}>'

class Updates(db.Model):
    __tablename__ = "updates"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    
    # Foreign key (many updates belong to one campaign)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)

    def __repr__(self):
        return f'<Updates {self.id}, {self.title}, {self.description}>'

