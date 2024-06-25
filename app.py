from flask import Flask,render_template,request, redirect,url_for,flash,session
from model import db,User,Campaign,AdRequest,FlaggedUser
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)
with app.app_context():
    db.create_all()
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin_user = User(
            username='admin',
            password=generate_password_hash('admin'),
            role='admin',
            company_name=None,
            category=None,
            niche=None
        )
        db.session.add(admin_user)
        db.session.commit()

@app.route('/')
def landing_page():
    return render_template('landing_page.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=uname, role='admin').first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('admin_dash'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('admin_login.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            
            if user.role == 'sponsor':
                return redirect(url_for('sponsor_profile'))
            elif user.role == 'influencer':
                return redirect(url_for('influencer_profile'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('user_login.html')


# Sponsor signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        company_name = request.form['company_name']
        industry = request.form['industry']
        budget = float(request.form['budget'])

        # Create new sponsor user
        new_user = User(
            username=username,
            password=generate_password_hash(password),
            role='sponsor',
            company_name=company_name,
            name=None,
            category=industry,
            niche=None,
            reach=None,
            budget=budget,
            platforms=None
        )

        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('user_login'))
    return render_template('signup.html')

@app.route('/signup_infl', methods=['GET', 'POST'])
def signup_infl():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        category = request.form['category']
        niche = request.form['niche']
        reach = int(request.form['reach'])

        # Create new influencer user
        new_user = User(
            username=username,
            password=generate_password_hash(password),
            role='influencer',
            company_name=None,  # No company_name for influencers
            name=name,
            category=category,
            niche=niche,
            reach=reach,
            budget=None,
            platforms = ','.join(request.form.getlist('platforms'))  # Convert list to comma-separated string

        )
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('user_login'))
    return render_template('signup_infl.html')

# @app.route('/admin_dash')
# def admin_dash():
#     # Sample data for demonstration
#     ongoing_campaign_progress = 75  # in percentage
#     flagged_campaigns = [
#         {"name": "Campaign 1", "reason": "Suspicious activity"},
#         {"name": "Campaign 2", "reason": "High number of complaints"}
#     ]
#     return render_template('admin_dash.html', 
#                            progress=ongoing_campaign_progress, 
#                            flagged_campaigns=flagged_campaigns)
@app.route('/admin_dash')
def admin_dash():
    users = User.query.filter(~User.flagged.any(),User.role != 'admin').all()
    flagged_users = FlaggedUser.query.all()
    
    # Fetch flagged campaigns as needed (replace with your actual logic)
    flagged_campaigns = []  # Example, replace with actual data fetching logic

    # Fetch ongoing campaigns and their progress
    campaigns = Campaign.query.all()
    return render_template('admin_dash.html', users=users, flagged_users=flagged_users, flagged_campaigns=flagged_campaigns, campaigns=campaigns)

@app.route('/flag_user/<int:user_id>', methods=['POST'])
def flag_user(user_id):
    user = User.query.get(user_id)
    if user:
        # Check if the user is already flagged
        flagged_user = FlaggedUser.query.filter_by(user_id=user_id).first()
        if not flagged_user:
            new_flagged_user = FlaggedUser(user_id=user.id, username=user.username, role=user.role)
            db.session.add(new_flagged_user)
            db.session.commit()
            flash('User has been flagged successfully.', 'success')
        else:
            flash('User is already flagged.', 'warning')
    return redirect(url_for('admin_dash'))

@app.route('/unflag_user/<int:user_id>', methods=['POST'])
def unflag_user(user_id):
    flagged_user = FlaggedUser.query.filter_by(user_id=user_id).first()
    if flagged_user:
        db.session.delete(flagged_user)
        db.session.commit()
        flash('User has been unflagged successfully.', 'success')
    return redirect(url_for('admin_dash'))

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    flagged_user = FlaggedUser.query.filter_by(user_id=user_id).first()
    if flagged_user:
        user = User.query.get(user_id)
        db.session.delete(flagged_user)
        db.session.delete(user)
        db.session.commit()
        flash('Flagged user has been deleted successfully.', 'success')
    else:
        flash('User must be flagged before deletion.', 'warning')
    return redirect(url_for('admin_dash'))

@app.route('/flagged_user_profile/<int:flagged_user_id>')
def flagged_user_profile(flagged_user_id):
    flagged_user = FlaggedUser.query.get(flagged_user_id)
    return render_template('flagged_user_profile.html', flagged_user=flagged_user)

# # Sample data
# influencers = [
#     {"name": "virat", "type": "Influencer", "description": "Expert in tech reviews."},
#     {"name": "sachin", "type": "Influencer", "description": "Fashion and lifestyle guru."},
# ]
# sponsors = [
#     {"name": "adidas", "type": "Sponsor", "description": "Looking to sponsor sports events."},
#     {"name": "boost", "type": "Sponsor", "description": "Interested in fashion and beauty campaigns."},
# ]
# campaigns = [
#     {"id":1,"name": "run for tech", "type": "Campaign", "description": "Tech product launch."},
#     {"id":2,"name": "rampwalk modelling", "type": "Campaign", "description": "Fashion week promotion."},
# ]

# @app.route('/ad_find', methods=['GET', 'POST'])
# def find():
#     results = None
#     if request.method == 'POST':
#         search_query = request.form['search_query'].lower()
#         # Sample search logic
#         results = [item for item in influencers + sponsors + campaigns if search_query in item['name'].lower() or search_query in item['description'].lower()]
        
#         # Uncomment and modify the following lines to fetch from the database
#         # import sqlite3
#         # conn = sqlite3.connect('your_database.db')
#         # cursor = conn.cursor()
#         # cursor.execute("SELECT * FROM influencers WHERE name LIKE ? OR description LIKE ?", ('%' + search_query + '%', '%' + search_query + '%'))
#         # influencers_results = cursor.fetchall()
#         # cursor.execute("SELECT * FROM sponsors WHERE name LIKE ? OR description LIKE ?", ('%' + search_query + '%', '%' + search_query + '%'))
#         # sponsors_results = cursor.fetchall()
#         # cursor.execute("SELECT * FROM campaigns WHERE name LIKE ? OR description LIKE ?", ('%' + search_query + '%', '%' + search_query + '%'))
#         # campaigns_results = cursor.fetchall()
#         # conn.close()
#         # results = influencers_results + sponsors_results + campaigns_results

#     return render_template('ad_find.html', results=results)
@app.route('/ad_find', methods=['GET', 'POST'])
def find():
    results = None
    if request.method == 'POST':
        search_query = request.form['search_query'].lower()
        
        # Search logic for users and campaigns
        users = User.query.filter(
            (User.username.ilike(f"%{search_query}%")) |
            (User.company_name.ilike(f"%{search_query}%")) |
            (User.name.ilike(f"%{search_query}%")) |
            (User.category.ilike(f"%{search_query}%")) |
            (User.niche.ilike(f"%{search_query}%"))
        ).all()
        
        campaigns = Campaign.query.filter(
            (Campaign.campaign_name.ilike(f"%{search_query}%")) |
            (Campaign.category.ilike(f"%{search_query}%")) |
            (Campaign.products.ilike(f"%{search_query}%")) |
            (Campaign.goals.ilike(f"%{search_query}%"))
        ).all()
        
        results = {
            'users': users,
            'campaigns': campaigns
        }

    return render_template('ad_find.html', results=results)

@app.route('/ad_stats')
def stats():
    return render_template('ad_stats.html')

@app.route('/logout')
def logout():
    return render_template('landing_page.html')

profile = {
    "name": "Influencer Name",
    "profile_picture": "https://via.placeholder.com/150",
    "ratings": 4.5,
    "earnings": "$5000",
    "campaign_progress": 60  # in percentage
}

sponsor_requests = [
    {"id": 1, "ad_details": "Tech product launch promotion", "status": "pending"},
    {"id": 2, "ad_details": "Fashion week promotion", "status": "pending"}
]

@app.route('/influencer_profile')
def influencer_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user_login'))

    user = User.query.get_or_404(user_id)
    if user.role != 'influencer':
        return redirect(url_for('user_login'))

    profile = {
        'username': user.username,
        'name': user.name,
        'category': user.category,
        'niche': user.niche,
        'reach': user.reach,
        'platforms': user.platforms.split(',') if user.platforms else [],
        'ratings': 4.5,  # This should be calculated based on actual data
        'earnings': 1000,  # This should be calculated based on actual data
        'campaign_progress': 75,  # This should be calculated based on actual data
        'profile_picture': 'path_to_profile_picture.jpg'  # This should be fetched from the database or storage
    }

    sponsor_requests = AdRequest.query.filter_by(influencer_name=user.username).all()
    return render_template('influencer_profile.html', profile=profile, sponsor_requests=sponsor_requests)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user_login'))

    user = User.query.get_or_404(user_id)
    if user.role != 'influencer':
        return redirect(url_for('user_login'))

    user.username = request.form['username']
    user.name = request.form['name']
    user.category = request.form['category']
    user.niche = request.form['niche']
    user.reach = request.form['reach']
    user.platforms = ','.join(request.form.getlist('platforms'))

    db.session.commit()
    flash('Profile updated successfully!', 'success')
    
    return redirect(url_for('influencer_profile'))

@app.route('/infl_find',methods=['GET','POST'])
def find_infl():
    results1 = None
    if request.method == 'POST':
        search_query = request.form['search_query'].lower()
        
        # Search logic for users and campaigns
        users = User.query.filter(
            (User.role=='sponsor')&
            ((User.username.ilike(f"%{search_query}%")) |
            (User.company_name.ilike(f"%{search_query}%")) |
            (User.name.ilike(f"%{search_query}%")) |
            (User.category.ilike(f"%{search_query}%")) |
            (User.niche.ilike(f"%{search_query}%"))
        )).all()
        
        campaigns = Campaign.query.filter(
            (Campaign.campaign_name.ilike(f"%{search_query}%")) |
            (Campaign.category.ilike(f"%{search_query}%")) |
            (Campaign.products.ilike(f"%{search_query}%")) |
            (Campaign.goals.ilike(f"%{search_query}%"))
        ).all()
        
        results1 = {
            'users': users,
            'campaigns': campaigns
        }

    return render_template('infl_find.html',results1=results1)

@app.route('/infl_stat')
def stats_inf():
    return render_template('infl_stat.html')

@app.route('/request_action/<int:request_id>/<action>')
def request_action(request_id, action):
    # Sample logic to handle request actions
    for request in sponsor_requests:
        if request['id'] == request_id:
            if action in ['accept', 'reject', 'renegotiate']:
                request['status'] = action
                flash(f'Request {action}ed successfully.', 'success')
                break
    return redirect(url_for('influencer_profile'))

# # Sample data for demonstration
# sponsor_profile_data = {
#     "name": "James Bond",
#     "active_campaigns": [
#         {"id": 1, "name": "Tech Product Launch", "progress": 50},
#         {"id": 2, "name": "Fashion Week Promotion", "progress": 25}
#     ],
#     "new_requests": [
#         {"id": 1, "influencer_name": "Influencer A", "ad_details": "Tech product promotion"},
#         {"id": 2, "influencer_name": "Influencer B", "ad_details": "Fashion event sponsorship"}
#     ]
# }


@app.route('/sponsor_profile')
def sponsor_profile():
    # Check if sponsor ID is in session
    if 'user_id' in session:
        sponsor_id = session['user_id']
        # Fetch sponsor data from the database
        sponsor = User.query.filter_by(id=sponsor_id, role='sponsor').first()
        if sponsor:
            active_campaigns = Campaign.query.filter_by(status='planning', user_id=sponsor_id).all()
            new_requests = AdRequest.query.filter_by(status='pending', user_id=sponsor_id).all()
            sponsor_profile_data = {
                'username':sponsor.username,
                'name': sponsor.company_name,
                'category':sponsor.category,
                'active_campaigns': [{'id': campaign.id, 'name': campaign.campaign_name, 'progress': campaign.progress} for campaign in active_campaigns],
                'new_requests': [{'id': request.id, 'influencer_name': request.influencer_name, 'ad_details': request.ad_name} for request in new_requests]
            }

            return render_template('sponsor_profile.html', sponsor_profile=sponsor_profile_data)
        else:
            # Handle case where sponsor ID from session does not match any sponsor in the database
            return "Sponsor not found."
    else:
        # Handle case where sponsor is not logged in
        return "Please log in as a sponsor."

@app.route('/update_sponsor_profile', methods=['POST'])
def update_sponsor_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user_login'))

    user = User.query.get_or_404(user_id)
    if user.role != 'sponsor':
        return redirect(url_for('user_login'))

    user.username = request.form['username']
    user.company_name = request.form['company_name']
    user.category = request.form['category']

    db.session.commit()
    flash('Profile updated successfully!', 'success')
    
    return redirect(url_for('sponsor_profile'))

@app.route('/sponsor/campaigns')
def sponsor_campaigns():
    campaigns = Campaign.query.all()
    return render_template('sponsor_campaigns.html',campaigns=campaigns)

@app.route('/sponsor/find_sponsor',methods=['GET','POST'])
def find_sponsor():
    results2 = None
    if request.method == 'POST':
        search_query = request.form['search_query'].lower()
        
        # Search logic for users and campaigns
        users = User.query.filter(
            (User.role=='influencer')&
            ((User.username.ilike(f"%{search_query}%")) |
            (User.company_name.ilike(f"%{search_query}%")) |
            (User.name.ilike(f"%{search_query}%")) |
            (User.category.ilike(f"%{search_query}%")) |
            (User.niche.ilike(f"%{search_query}%"))
        )).all()
        
        campaigns = Campaign.query.filter(
            (Campaign.campaign_name.ilike(f"%{search_query}%")) |
            (Campaign.category.ilike(f"%{search_query}%")) |
            (Campaign.products.ilike(f"%{search_query}%")) |
            (Campaign.goals.ilike(f"%{search_query}%"))
        ).all()
        
        results2 = {
            'users': users,
            'campaigns': campaigns
        }
    return render_template('find_sponsor.html',results2=results2)

@app.route('/add_campaign', methods=['GET', 'POST'])
def add_campaign():
    if request.method == 'POST':
        user_id = session.get('user_id')
        campaign_name = request.form['campaign_name']
        category = request.form['category']
        budget = float(request.form['budget'])
        status = request.form['status']
        products = request.form['products']
        goals = request.form['goals']
        progress = int(request.form['progress'])
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()

        # Create new campaign
        new_campaign = Campaign(
            user_id=user_id,
            campaign_name=campaign_name,
            category=category,
            budget=budget,
            status=status,
            products=products,
            goals=goals,
            progress=progress,
            start_date=start_date,
            end_date=end_date
        )

        # Add campaign to the database
        db.session.add(new_campaign)
        db.session.commit()

        return redirect(url_for('sponsor_campaigns'))  # Redirect to sponsor dashboard after campaign creation

    return render_template('add_campaign.html')

@app.route('/edit_campaign/<int:campaign_id>', methods=['GET', 'POST'])
def edit_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)

    if request.method == 'POST':
        campaign.campaign_name = request.form['campaign_name']
        campaign.category = request.form['category']
        campaign.budget = float(request.form['budget'])
        campaign.status = request.form['status']
        campaign.products = request.form['products']
        campaign.goals = request.form['goals']
        campaign.progress = int(request.form['progress'])
        campaign.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        campaign.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()

        db.session.commit()
        return redirect(url_for('sponsor_campaigns'))  # Redirect to sponsor dashboard after updating campaign

    return render_template('edit_campaign.html', campaign=campaign)

@app.route('/delete_campaign/<int:campaign_id>', methods=['POST','GET'])
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()  # Commit the deletion to the database
    flash('Campaign deleted successfully!', 'success')
    return redirect(url_for('sponsor_campaigns'))


@app.route('/add_ad_request/<int:campaign_id>', methods=['GET', 'POST'])
def add_ad_request(campaign_id):
    #campaign = Campaign.query.get_or_404(campaign_id)
    if request.method == 'POST':
        ad_name = request.form['ad_name']
        description = request.form['description']
        budget = float(request.form['budget'])
        goal = request.form['goal']
        influencer_name = request.form['influencer_name']
        status = request.form['status']
        user_id=session.get('user_id')
        new_ad_request = AdRequest(
            campaign_id=campaign_id,
            ad_name=ad_name,
            description=description,
            budget=budget,
            goal=goal,
            influencer_name=influencer_name,
            status=status,
            user_id=user_id
        )

        db.session.add(new_ad_request)
        db.session.commit()
        flash('Ad request created successfully!', 'success')
        return redirect(url_for('sponsor_campaigns'))    
    return render_template('add_ad_request.html', campaign_id=campaign_id)

@app.route('/view_ad_requests/<int:campaign_id>', methods=['GET'])
def view_ad_requests(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id).all()
    return render_template('view_ad_requests.html', campaign=campaign, ad_requests=ad_requests)

@app.route('/edit_ad_request/<int:ad_request_id>', methods=['POST'])
def edit_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    ad_request.ad_name = request.form['ad_name']
    ad_request.description = request.form['description']
    ad_request.budget = float(request.form['budget'])
    ad_request.goal = request.form['goal']
    ad_request.influencer_name = request.form['influencer_name']
    ad_request.status = request.form['status']

    db.session.commit()
    flash('Ad request updated successfully!', 'success')
    return redirect(url_for('view_ad_requests', campaign_id=ad_request.campaign_id))

@app.route('/delete_ad_request/<int:ad_request_id>', methods=['POST'])
def delete_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    campaign_id = ad_request.campaign_id
    db.session.delete(ad_request)
    db.session.commit()  # Commit the deletion to the database
    flash('Ad request deleted successfully!', 'success')
    return redirect(url_for('view_ad_requests', campaign_id=campaign_id))

@app.route('/renegotiate_ad_request/<int:request_id>', methods=['POST'])
def renegotiate_ad_request(request_id):
    # Check if sponsor ID is in session
    if 'user_id' in session:
        sponsor_id = session['user_id']
        # Fetch the ad request from the database
        ad_request = AdRequest.query.filter_by(id=request_id, user_id=sponsor_id).first()
        if ad_request:
            # Update renegotiation details based on form submission
            ad_request.renegotiate_details = request.form['renegotiate_details']
            # Add other fields here
            # Commit changes to the database
            db.session.commit()
            # Redirect to sponsor profile page after updating
            return redirect(url_for('sponsor_profile'))
        else:
            # Handle case where ad request ID does not match any request for the logged-in sponsor
            return "Ad request not found."
    else:
        # Handle case where sponsor is not logged in
        return "Please log in as a sponsor."


@app.route('/sponsor/stats')
def sponsor_stats():
    return render_template('sponsor_stats.html')

if __name__ == '__main__':
    app.run(debug=True)