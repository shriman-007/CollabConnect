from flask import Flask,render_template,request, redirect,url_for,flash,session
from model import db,User,Campaign,AdRequest
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)
with app.app_context():
    db.create_all()
    admin = User.query.filter_by(username='admin123').first()
    if not admin:
        admin_user = User(
            username='admin123',
            password=generate_password_hash('adminpassword'),
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

@app.route("/signup/<name>")
def hello(name):
    return f"<p>Hello, {name}</p>"
@app.route("/math/<int:a>/<int:b>")
def add(a,b):
    c=a+b
    return f"<p>{a}+{b}={c}</p>"
@app.route("/mul/<int:a>/<int:b>")
def multiply(a,b):
    c=a*b
    return f"<p>{a}*{b}={c}</p>"
from flask import Flask, request

@app.route('/display', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        return f"Hello, {name}!"
    
    # Display the form using a minimal HTML structure embedded in the Python code
    return render_template("home.html")
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

@app.route('/admin_dash')
def admin_dash():
    # Sample data for demonstration
    ongoing_campaign_progress = 75  # in percentage
    flagged_campaigns = [
        {"name": "Campaign 1", "reason": "Suspicious activity"},
        {"name": "Campaign 2", "reason": "High number of complaints"}
    ]
    return render_template('admin_dash.html', 
                           progress=ongoing_campaign_progress, 
                           flagged_campaigns=flagged_campaigns)
# Sample data
influencers = [
    {"name": "virat", "type": "Influencer", "description": "Expert in tech reviews."},
    {"name": "sachin", "type": "Influencer", "description": "Fashion and lifestyle guru."},
]
sponsors = [
    {"name": "adidas", "type": "Sponsor", "description": "Looking to sponsor sports events."},
    {"name": "boost", "type": "Sponsor", "description": "Interested in fashion and beauty campaigns."},
]
campaigns = [
    {"id":1,"name": "run for tech", "type": "Campaign", "description": "Tech product launch."},
    {"id":2,"name": "rampwalk modelling", "type": "Campaign", "description": "Fashion week promotion."},
]

@app.route('/ad_find', methods=['GET', 'POST'])
def find():
    results = None
    if request.method == 'POST':
        search_query = request.form['search_query'].lower()
        # Sample search logic
        results = [item for item in influencers + sponsors + campaigns if search_query in item['name'].lower() or search_query in item['description'].lower()]
        
        # Uncomment and modify the following lines to fetch from the database
        # import sqlite3
        # conn = sqlite3.connect('your_database.db')
        # cursor = conn.cursor()
        # cursor.execute("SELECT * FROM influencers WHERE name LIKE ? OR description LIKE ?", ('%' + search_query + '%', '%' + search_query + '%'))
        # influencers_results = cursor.fetchall()
        # cursor.execute("SELECT * FROM sponsors WHERE name LIKE ? OR description LIKE ?", ('%' + search_query + '%', '%' + search_query + '%'))
        # sponsors_results = cursor.fetchall()
        # cursor.execute("SELECT * FROM campaigns WHERE name LIKE ? OR description LIKE ?", ('%' + search_query + '%', '%' + search_query + '%'))
        # campaigns_results = cursor.fetchall()
        # conn.close()
        # results = influencers_results + sponsors_results + campaigns_results

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
    return render_template('influencer_profile.html', 
                           profile=profile, 
                           sponsor_requests=sponsor_requests)

@app.route('/infl_find',methods=['GET','POST'])
def find_infl():
    results1 = None
    if request.method == 'POST':
        search_query = request.form['search_query'].lower()
        results1 = [item for item in sponsors + campaigns if search_query in item['name'].lower() or search_query in item['description'].lower()]
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

# Sample data for demonstration
sponsor_profile_data = {
    "name": "James Bond",
    "active_campaigns": [
        {"id": 1, "name": "Tech Product Launch", "progress": 50},
        {"id": 2, "name": "Fashion Week Promotion", "progress": 25}
    ],
    "new_requests": [
        {"id": 1, "influencer_name": "Influencer A", "ad_details": "Tech product promotion"},
        {"id": 2, "influencer_name": "Influencer B", "ad_details": "Fashion event sponsorship"}
    ]
}


@app.route('/sponsor_profile')
def sponsor_profile():
    print(f"Sponsor profile data: {sponsor_profile_data}")
    return render_template('sponsor_profile.html', sponsor_profile=sponsor_profile_data)

@app.route('/sponsor/campaigns')
def sponsor_campaigns():
    campaigns = Campaign.query.all()
    return render_template('sponsor_campaigns.html',campaigns=campaigns)

@app.route('/sponsor/find_sponsor',methods=['GET','POST'])
def find_sponsor():
    results2 = None
    if request.method == 'POST':
        search_query = request.form['search_query'].lower()
        results2 = [item for item in influencers + campaigns if search_query in item['name'].lower() or search_query in item['description'].lower()]
    return render_template('find_sponsor.html',results2=results2)

@app.route('/add_campaign', methods=['GET', 'POST'])
def add_campaign():
    if request.method == 'POST':
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

@app.route('/add_ad_request/<int:campaign_id>', methods=['GET', 'POST'])
def add_ad_request(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if request.method == 'POST':
        ad_name = request.form['ad_name']
        description = request.form['description']
        budget = float(request.form['budget'])
        goal = request.form['goal']
        influencer_name = request.form['influencer_name']
        status = request.form['status']

        new_ad_request = AdRequest(
            campaign_id=campaign_id,
            ad_name=ad_name,
            description=description,
            budget=budget,
            goal=goal,
            influencer_name=influencer_name,
            status=status
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

@app.route('/sponsor/stats')
def sponsor_stats():
    return render_template('sponsor_stats.html')

app.run(debug=True,port=6100)