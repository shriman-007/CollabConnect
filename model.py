from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'sponsor' or 'influencer'
    company_name = db.Column(db.String(100))  # Only for sponsors
    name = db.Column(db.String(100))  # Only for infl
    category = db.Column(db.String(50))  # For influencers: category
    niche = db.Column(db.String(50))  # For influencers: niche
    reach = db.Column(db.Integer)  # For influencers: reach
    budget = db.Column(db.Float)
    platforms = db.Column(db.String(120))  # Store platforms as comma-separated string

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80))
    budget = db.Column(db.Float)
    status = db.Column(db.String(80))
    products = db.Column(db.String(200))
    goals = db.Column(db.String(200))
    progress = db.Column(db.Integer)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
