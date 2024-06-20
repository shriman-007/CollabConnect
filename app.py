from flask import Flask,render_template,request, redirect,url_for,flash
from model import db,user,flaggedUser
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite://rwwj.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)
with app.app_context():
    db.create_all()
@app.route("/")
def hello_world():
    return "<p>Hello,World!</p>"
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
        if uname == 'admin123' and password == 'pwd':
            return redirect(url_for('admin_dash'))
    return render_template('admin_login.html')

# @app.route("/user_login",methods=['GET','POST'])
# def login_u():    
#     if request.method=='POST':
#         uname=request.form['username']
#         if uname !='':
#             if request.form['password']!='':
#                 return f"Welcome,{uname}!"
#     return render_template("user_login.html")
@app.route("/signup",methods=['GET','POST'])
def signup():    
    if request.method=='POST':
        uname=request.form['username']
        if uname.isalnum() :
            if request.form['password']!="":
                indus=request.form['industry']
                return f"Welcome,{uname}, your account has been created! Your industry is {indus}"
@app.route("/signup_infl",methods=['GET','POST'])
def signup_infl():    
    if request.method=='POST':
        uname=request.form['username']
        if uname.isalnum() :
            if request.form['password']!="":
                platforms = request.form.getlist('platform')
                platform_list = ", ".join(platforms) 

                return f"Welcome,{uname}, your account has been created! Your platform is  {platform_list}"                
    return render_template("signup_infl.html")

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

@app.route('/admin_stats')
def stats():
    return render_template('ad_stats.html')

@app.route('/logout')
def logout():
    return "You have been logged out."

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

@app.route('/influencer_login', methods=['GET', 'POST'])
def influencer_login():
    if request.method == 'POST':
        uname = request.form['username']
        password = request.form['password']
        if uname == 'inf123' and password == 'pwd':
            return redirect(url_for('influencer_profile'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('influencer_login.html')

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

@app.route('/infl_stats')
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

@app.route('/sponsor_login', methods=['GET', 'POST'])
def sponsor_login():
    if request.method == 'POST':
        uname = request.form['username']
        password = request.form['password']
        if uname == 'sponsor123' and password == 'pwd':
            return redirect(url_for('sponsor_profile'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('user_login.html')

@app.route('/sponsor_profile')
def sponsor_profile():
    print(f"Sponsor profile data: {sponsor_profile_data}")
    return render_template('sponsor_profile.html', sponsor_profile=sponsor_profile_data)

@app.route('/sponsor/campaigns')
def sponsor_campaigns():
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
        # In a real application, this data would be saved to a database
        new_campaign = {
            "id": len(campaigns) + 1,
            "title": request.form['title'],
            "description": request.form['description'],
            "image": request.form['image'],
            "niche": request.form['niche'],
            "date": request.form['date'],
            "budget": "$0"  # Default value for demonstration
        }
        campaigns.append(new_campaign)
        return redirect(url_for('sponsor_campaigns'))
    return render_template('add_campaign.html')

@app.route('/add_ad_request/<int:campaign_id>', methods=['GET', 'POST'])
def add_ad_request(campaign_id):
    if request.method == 'POST':
        # In a real application, this data would be saved to a database
        new_ad_request = {
            "ad_name": request.form['ad_name'],
            "description": request.form['description'],
            "term": request.form['term'],
            "payment": request.form['payment'],
            "influencer_assigned": request.form['influencer_assigned']
        }
        # Here, you would typically save the new ad request to the campaign in the database
        flash('Ad request created successfully!', 'success')
        return redirect(url_for('sponsor_campaigns'))
    return render_template('add_ad_request.html', campaign_id=campaign_id)


@app.route('/sponsor/stats')
def sponsor_stats():
    return render_template('sponsor_stats.html')

app.run(debug=True,port=5500)