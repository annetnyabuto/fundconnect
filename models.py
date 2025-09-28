from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from flask_bcrypt import Bcrypt

bcrypt=Bcrypt()

metadata = MetaData()

db = SQLAlchemy(metadata=metadata)


class User(db.Model, SerializerMixin):
    __tablename__ = "users"
    
    serialize_rules = ('-_password_hash', '-campaigns.user', '-donations.user')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)
    designation = db.Column(db.String, nullable=False)

    campaigns = db.relationship('Campaign', backref='user')
    donations = db.relationship('Donations', backref='user')

    def __repr__(self):
        return f'<User {self.id}, {self.name}, {self.email}, {self.password_hash}, {self.designation}>'
    

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
    
    def set_password(self, password):
        self.password_hash = password
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'designation': self.designation
        }


class Campaign(db.Model, SerializerMixin):
    __tablename__ = "campaign"
    
    serialize_rules = ('-user.campaigns', '-donations.campaign', '-updates.campaign')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    category = db.Column(db.String)
    description = db.Column(db.String)
    targetamount = db.Column(db.Integer)
    raisedamount = db.Column(db.Integer)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    donations = db.relationship('Donations', backref='campaign', lazy=True)
    updates = db.relationship('Updates', backref='campaign', lazy=True)

    def __repr__(self):
        return f'<Campaign {self.id}, {self.name}, {self.category}, {self.description}, {self.targetamount}, {self.raisedamount}>'

class Donations(db.Model, SerializerMixin):
    __tablename__ = "donations"
    
    serialize_rules = ('-user.donations', '-campaign.donations')

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    paymentmethod = db.Column(db.String)
    amount = db.Column(db.Integer)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)

    def __repr__(self):
        return f'<Donations {self.id}, {self.title}, {self.paymentmethod}, {self.amount}>'

class Updates(db.Model, SerializerMixin):
    __tablename__ = "updates"
    
    serialize_rules = ('-campaign.updates',)

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)

    def __repr__(self):
        return f'<Updates {self.id}, {self.title}, {self.description}>'

