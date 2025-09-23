from faker import Faker
from app import app, db
from models import User, Campaign, Donations, Updates
import random

fake = Faker()
def seed_data():
    with app.app_context():
        # Create all tables
        #db.create_all()
        
        # Clear existing data
        Donations.query.delete()
        Updates.query.delete()
        Campaign.query.delete()
        User.query.delete()
        
        

        # Create users
        users = []
        for _ in range(5):
            user = User(
                name=fake.name(),
                email=fake.unique.email(),
                designation=random.choice(['Organisation', 'Individual']),
                password_hash="admin@2020"
            )
             
            users.append(user)
        
        db.session.add_all(users)
        db.session.commit()
        
        # Create campaigns
        campaigns = []
        for _ in range(8):
            campaign = Campaign(
                category=random.choice(['Education', 'Health', 'Environment']),
                description=fake.text(max_nb_chars=200),
                targetamount=fake.random_int(min=1000, max=50000),
                raisedamount=fake.random_int(min=0, max=25000),
                user_id=random.choice(users).id
            )
            campaigns.append(campaign)
        
        db.session.add_all(campaigns)
        db.session.commit()
        
        # Create donations
        donations = []
        for _ in range(15):
            donation = Donations(
                title=fake.sentence(nb_words=3),
                paymentmethod=random.choice(['Credit Card', 'PayPal', 'Bank Transfer']),
                amount=fake.random_int(min=10, max=1000),
                user_id=random.choice(users).id,
                campaign_id=random.choice(campaigns).id
            )
            donations.append(donation)
        
        db.session.add_all(donations)
        db.session.commit()
        
        # Create updates
        updates = []
        for _ in range(12):
            update = Updates(
                title=fake.sentence(nb_words=4),
                description=fake.text(max_nb_chars=300),
                campaign_id=random.choice(campaigns).id
            )
            updates.append(update)
        
        db.session.add_all(updates)
        db.session.commit()
        
        print("Seed data created successfully!")

if __name__ == "__main__":
    seed_data()

