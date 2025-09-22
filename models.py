from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

metadata = MetaData()

db = SQLAlchemy(metadata=metadata)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    password = db.Column(db.String)
    designation = db.Column(db.String)

    def __repr__(self):
        return f'<User {self.id}, {self.name}, {self.email}, {self.password}, {self.designation}>'

class Campaign(db.Model):
    __tablename__ = "campaign"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String)
    description = db.Column(db.String)
    targetamount = db.Column(db.Integer)
    raisedamount = db.Column(db.Integer)

    def __repr__(self):
        return f'<Campaign {self.id}, {self.category}, {self.description}, {self.targetamount}, {self.raisedamount}>'

class Donations(db.Model):
    __tablename__ = "donations"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    paymentmethod = db.Column(db.String)
    amount = db.Column(db.Integer)

    def __repr__(self):
        return f'<User {self.id}, {self.title}, {self.paymentmethod}, {self.amount}>'

class Updates(db.Model):
    __tablename__ = "updates"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)

    def __repr__(self):
        return f'<User {self.id}, {self.title}, {self.description}>'

