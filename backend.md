# AI Agent Task: Generate Sponnect Flask Backend (Consolidated, Core Features)

## Objective

Generate the core backend API for the Sponnect application within `sponnect/backend`. Consolidate code into `app.py` and `models.py`. Implement all core functionalities (including negotiation and flagging, excluding background jobs/caching). Use Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, targeting SQLite in a WSL environment.

---

## Step 1: Project Structure & Dependencies

1.  **Create Project Structure (in your WSL terminal):**
    ```
    mkdir sponnect
    cd sponnect
    mkdir backend
    mkdir frontend
    cd backend
    touch models.py
    touch app.py
    touch config.py
    touch run.py
    touch .env
    ```
    *(You should now be inside the `sponnect/backend` directory)*

2.  **Add Secrets to `.env`:**
    Open the `.env` file and add *secure, unique* values:
    ```
    # .env (in sponnect/backend)
    SECRET_KEY='your_strong_flask_secret_key_here'
    JWT_SECRET_KEY='your_strong_jwt_secret_key_here'
    DATABASE_URL='sqlite:///app.db'
    ADMIN_USERNAME='admin_sponnect'
    ADMIN_PASSWORD='replace_with_strong_admin_password'
    FLASK_APP=app.py
    FLASK_DEBUG=1 # 1 for development, 0 for production
    ```
    *Remember to add `.env` to `.gitignore` if using version control.*

3.  **Install Dependencies (in your WSL terminal, inside `sponnect/backend`):**
    ```
    pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-JWT-Extended python-dotenv Werkzeug
    ```

---

## Step 2: Define Database Models (`models.py`)

1.  **Create `sponnect/backend/models.py`:**
    ```
    # models.py
    from flask_sqlalchemy import SQLAlchemy
    from werkzeug.security import generate_password_hash, check_password_hash
    from datetime import datetime

    db = SQLAlchemy()

    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False, index=True)
        password_hash = db.Column(db.String(128), nullable=False)
        role = db.Column(db.String(20), nullable=False, default='influencer', index=True) # 'influencer', 'sponsor', 'admin'
        is_active = db.Column(db.Boolean, default=True, nullable=False)
        sponsor_approved = db.Column(db.Boolean, nullable=True, default=None) # For sponsors: True/False/None
        is_flagged = db.Column(db.Boolean, default=False, nullable=False) # For admin flagging
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

        # Sponsor specific fields
        company_name = db.Column(db.String(100), nullable=True)
        industry = db.Column(db.String(100), nullable=True)
        # Sponsor budget field removed - Budget is per-campaign

        # Influencer specific fields
        influencer_name = db.Column(db.String(100), nullable=True) # Public Name
        category = db.Column(db.String(50), nullable=True)
        niche = db.Column(db.String(100), nullable=True)
        reach = db.Column(db.Integer, nullable=True, default=0)

        # Relationships
        campaigns = db.relationship('Campaign', back_populates='sponsor', lazy='dynamic',
                                    foreign_keys='Campaign.sponsor_id')
        ad_requests_received = db.relationship('AdRequest', back_populates='target_influencer', lazy='dynamic',
                                               foreign_keys='AdRequest.influencer_id')
        ad_requests_initiated = db.relationship('AdRequest', back_populates='initiating_user', lazy='dynamic',
                                               foreign_keys='AdRequest.initiator_id')

        def set_password(self, password):
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)

        def __repr__(self):
            return f'<User {self.username} ({self.role})>'

    class Campaign(db.Model):
        __tablename__ = 'campaigns'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(120), nullable=False)
        description = db.Column(db.Text, nullable=True)
        start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        end_date = db.Column(db.DateTime, nullable=True)
        budget = db.Column(db.Float, nullable=False)
        visibility = db.Column(db.String(10), nullable=False, default='private', index=True) # 'public', 'private'
        goals = db.Column(db.Text, nullable=True)
        is_flagged = db.Column(db.Boolean, default=False, nullable=False) # For admin flagging
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        sponsor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

        # Relationships
        sponsor = db.relationship('User', back_populates='campaigns', foreign_keys=[sponsor_id])
        ad_requests = db.relationship('AdRequest', back_populates='campaign', lazy='dynamic',
                                      cascade="all, delete-orphan")

        def __repr__(self):
            return f'<Campaign {self.name}>'

    class AdRequest(db.Model):
        __tablename__ = 'ad_requests'
        id = db.Column(db.Integer, primary_key=True)
        campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False, index=True)
        influencer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True) # Target Influencer
        initiator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True) # User who created/last modified

        message = db.Column(db.Text, nullable=True) # Latest message/note in negotiation
        requirements = db.Column(db.Text, nullable=False)
        payment_amount = db.Column(db.Float, nullable=False)
        status = db.Column(db.String(20), nullable=False, default='Pending', index=True) # 'Pending', 'Accepted', 'Rejected', 'Negotiating'
        last_offer_by = db.Column(db.String(20), nullable=True) # 'sponsor' or 'influencer' - tracks negotiation turn
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        # Relationships
        campaign = db.relationship('Campaign', back_populates='ad_requests', foreign_keys=[campaign_id])
        target_influencer = db.relationship('User', back_populates='ad_requests_received', foreign_keys=[influencer_id])
        initiating_user = db.relationship('User', back_populates='ad_requests_initiated', foreign_keys=[initiator_id])

        def __repr__(self):
            return f'<AdRequest {self.id} Campaign:{self.campaign_id} Status:{self.status}>'

    # Add Indexes
    db.Index('idx_adrequest_campaign_influencer', AdRequest.campaign_id, AdRequest.influencer_id)
    db.Index('idx_adrequest_status', AdRequest.status)
    db.Index('idx_campaign_sponsor_visibility', Campaign.sponsor_id, Campaign.visibility)

    ```

---

## Step 3: Configuration (`config.py`)

1.  **Create `sponnect/backend/config.py`:**
    ```
    # config.py
    import os
    from datetime import timedelta
    from dotenv import load_dotenv

    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    class Config:
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-flask-secret-key'
        JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'default-jwt-secret-key'
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(BASE_DIR, 'sponnect_app.db') # Changed DB name
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_HOURS', 1)))

        ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
        ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'password')
        DEBUG = os.environ.get('FLASK_DEBUG') == '1'
    ```

---

## Step 4: Main Application (`app.py`)

1.  **Create `sponnect/backend/app.py`:**
    ```
    # app.py
    import os
    from flask import Flask, request, jsonify
    from flask_migrate import Migrate
    from flask_jwt_extended import (
        JWTManager, jwt_required, create_access_token,
        get_jwt_identity, get_jwt, verify_jwt_in_request
    )
    from functools import wraps
    from datetime import datetime
    from sqlalchemy import func # For stats count

    from config import Config
    from models import db, User, Campaign, AdRequest

    # --- App Initialization ---
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- Extension Initialization ---
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    # --- Decorators ---
    def role_required(required_role):
        def decorator(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                verify_jwt_in_request()
                claims = get_jwt()
                user_role = claims.get('role')
                # Allow admin access to all role-restricted routes
                if user_role == 'admin':
                    return fn(*args, **kwargs)
                if user_role != required_role:
                    return jsonify(message=f"{required_role.capitalize()} access required"), 403
                return fn(*args, **kwargs)
            return wrapper
        return decorator

    admin_required = role_required('admin') # Note: Admin can access sponsor/influencer routes too
    sponsor_required = role_required('sponsor')
    influencer_required = role_required('influencer')

    # --- Helper Functions ---
    def serialize_user_basic(user):
        return {'id': user.id, 'username': user.username, 'role': user.role, 'is_flagged': user.is_flagged}

    def serialize_user_profile(user):
        data = serialize_user_basic(user)
        data['created_at'] = user.created_at.isoformat() if user.created_at else None
        if user.role == 'sponsor':
            data.update({'company_name': user.company_name, 'industry': user.industry, 'sponsor_approved': user.sponsor_approved})
        elif user.role == 'influencer':
            data.update({'influencer_name': user.influencer_name, 'category': user.category, 'niche': user.niche, 'reach': user.reach})
        return data

    def serialize_campaign_basic(campaign):
         return {'id': campaign.id, 'name': campaign.name, 'budget': campaign.budget, 'visibility': campaign.visibility, 'is_flagged': campaign.is_flagged}

    def serialize_campaign_detail(campaign):
        data = serialize_campaign_basic(campaign)
        data.update({'description': campaign.description, 'goals': campaign.goals, 'sponsor_id': campaign.sponsor_id,
                     'start_date': campaign.start_date.isoformat() if campaign.start_date else None,
                     'end_date': campaign.end_date.isoformat() if campaign.end_date else None,
                     'created_at': campaign.created_at.isoformat() if campaign.created_at else None})
        return data

    def serialize_ad_request_detail(ad_request):
        return {
            'id': ad_request.id, 'campaign_id': ad_request.campaign_id, 'influencer_id': ad_request.influencer_id,
            'initiator_id': ad_request.initiator_id, 'message': ad_request.message, 'requirements': ad_request.requirements,
            'payment_amount': ad_request.payment_amount, 'status': ad_request.status, 'last_offer_by': ad_request.last_offer_by,
            'created_at': ad_request.created_at.isoformat() if ad_request.created_at else None,
            'updated_at': ad_request.updated_at.isoformat() if ad_request.updated_at else None,
            # Include basic related info (avoid large joins for now)
            'campaign_name': ad_request.campaign.name if ad_request.campaign else None,
            'influencer_name': ad_request.target_influencer.influencer_name if ad_request.target_influencer else None,
        }

    # --- CLI Command for Admin Creation ---
    @app.cli.command("create-admin")
    def create_admin_command():
        """Creates the admin user from .env variables."""
        admin_username = Config.ADMIN_USERNAME
        admin_password = Config.ADMIN_PASSWORD
        if not admin_username or not admin_password: print("Error: ADMIN_USERNAME/PASSWORD missing in .env"); return
        if User.query.filter_by(username=admin_username, role='admin').first(): print(f"Admin '{admin_username}' exists."); return

        admin_user = User(username=admin_username, role='admin', is_active=True, sponsor_approved=True)
        admin_user.set_password(admin_password)
        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin user '{admin_username}' created.")

    # --- Routes ---

    # == Authentication ==
    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'influencer') # Defaults to influencer

        if not username or not password: return jsonify({"message": "Username and password required"}), 400
        if User.query.filter_by(username=username).first(): return jsonify({"message": "Username already exists"}), 409
        if role not in ['influencer', 'sponsor']: return jsonify({"message": "Invalid role"}), 400

        user = User(username=username, role=role)
        user.set_password(password)
        message = ""

        if role == 'sponsor':
            user.company_name = data.get('company_name')
            user.industry = data.get('industry')
            user.sponsor_approved = False # Requires approval
            message = "Sponsor registered. Account requires admin approval."
        else: # influencer
            user.influencer_name = data.get('influencer_name')
            user.category = data.get('category')
            user.niche = data.get('niche')
            user.reach = data.get('reach')
            message = "Influencer registered successfully."

        db.session.add(user)
        db.session.commit()
        return jsonify({"message": message}), 201

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password): return jsonify({"message": "Invalid credentials"}), 401
        if not user.is_active: return jsonify({"message": "Account deactivated"}), 403
        # Check sponsor approval status only if user is a sponsor
        if user.role == 'sponsor' and not user.sponsor_approved: return jsonify({"message": "Sponsor account pending approval"}), 403

        access_token = create_access_token(identity=user.id, additional_claims={'role': user.role})
        return jsonify(access_token=access_token, user_role=user.role), 200

    # == Profile Management ==
    @app.route('/api/profile', methods=['GET'])
    @jwt_required()
    def get_profile():
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        if not user: return jsonify({"message": "User not found"}), 404
        return jsonify(serialize_user_profile(user)), 200

    @app.route('/api/profile', methods=['PUT'])
    @jwt_required()
    def update_profile():
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        if not user: return jsonify({"message": "User not found"}), 404

        data = request.get_json()
        # Update fields based on role - prevent users from changing role/approval status
        if user.role == 'sponsor':
            user.company_name = data.get('company_name', user.company_name)
            user.industry = data.get('industry', user.industry)
        elif user.role == 'influencer':
            user.influencer_name = data.get('influencer_name', user.influencer_name)
            user.category = data.get('category', user.category)
            user.niche = data.get('niche', user.niche)
            if 'reach' in data: # Allow updating reach, maybe validate later
                 try: user.reach = int(data['reach'])
                 except (ValueError, TypeError): pass

        db.session.commit()
        return jsonify({"message": "Profile updated successfully", "profile": serialize_user_profile(user)}), 200

    @app.route('/api/influencers/<int:influencer_id>/profile', methods=['GET'])
    @jwt_required() # Any logged-in user can view public profile
    def get_public_influencer_profile(influencer_id):
        user = User.query.filter_by(id=influencer_id, role='influencer', is_active=True).first()
        if not user: return jsonify({"message": "Active influencer not found"}), 404
        # Return only public-safe info
        return jsonify({'id': user.id, 'influencer_name': user.influencer_name, 'category': user.category,
                        'niche': user.niche, 'reach': user.reach }), 200

    # == Admin Actions ==
    @app.route('/api/admin/stats', methods=['GET'])
    @jwt_required()
    @admin_required
    def get_admin_stats():
        # Basic counts - can be expanded with date ranges, etc.
        total_users = db.session.query(func.count(User.id)).scalar()
        active_sponsors = User.query.filter_by(role='sponsor', is_active=True, sponsor_approved=True).count()
        pending_sponsors = User.query.filter_by(role='sponsor', sponsor_approved=False).count()
        active_influencers = User.query.filter_by(role='influencer', is_active=True).count()
        public_campaigns = Campaign.query.filter_by(visibility='public').count()
        private_campaigns = Campaign.query.filter_by(visibility='private').count()
        flagged_users = User.query.filter_by(is_flagged=True).count()
        flagged_campaigns = Campaign.query.filter_by(is_flagged=True).count()
        ad_request_stats = db.session.query(AdRequest.status, func.count(AdRequest.id)).group_by(AdRequest.status).all()

        return jsonify({
            'total_users': total_users, 'active_sponsors': active_sponsors, 'pending_sponsors': pending_sponsors,
            'active_influencers': active_influencers, 'public_campaigns': public_campaigns, 'private_campaigns': private_campaigns,
            'flagged_users': flagged_users, 'flagged_campaigns': flagged_campaigns,
            'ad_requests_by_status': dict(ad_request_stats)
        }), 200

    @app.route('/api/admin/pending_sponsors', methods=['GET'])
    @jwt_required()
    @admin_required
    def admin_get_pending_sponsors():
        pending = User.query.filter_by(role='sponsor', sponsor_approved=False, is_active=True).all()
        return jsonify([serialize_user_profile(user) for user in pending]), 200

    @app.route('/api/admin/sponsors/<int:sponsor_id>/approve', methods=['PATCH'])
    @jwt_required()
    @admin_required
    def admin_approve_sponsor(sponsor_id):
        sponsor = db.session.get(User, sponsor_id)
        if not sponsor or sponsor.role != 'sponsor': return jsonify({"message": "Sponsor not found"}), 404
        if sponsor.sponsor_approved is True: return jsonify({"message": "Sponsor already approved"}), 400
        sponsor.sponsor_approved = True
        sponsor.is_active = True # Ensure active on approval
        db.session.commit()
        return jsonify({"message": "Sponsor approved"}), 200

    @app.route('/api/admin/sponsors/<int:sponsor_id>/reject', methods=['PATCH'])
    @jwt_required()
    @admin_required
    def admin_reject_sponsor(sponsor_id):
        sponsor = db.session.get(User, sponsor_id)
        if not sponsor or sponsor.role != 'sponsor': return jsonify({"message": "Sponsor not found"}), 404
        if sponsor.sponsor_approved is not False: return jsonify({"message": "Can only reject pending sponsors"}), 400
        sponsor.is_active = False # Deactivate rejected sponsors
        sponsor.sponsor_approved = None # Reset approval status, maybe? Or keep False. Keep False.
        db.session.commit()
        return jsonify({"message": "Sponsor rejected and deactivated"}), 200

    @app.route('/api/admin/users/<int:user_id>/flag', methods=['PATCH'])
    @jwt_required()
    @admin_required
    def admin_flag_user(user_id):
        user = db.session.get(User, user_id)
        if not user or user.role == 'admin': return jsonify({"message": "User not found or cannot flag admin"}), 404
        user.is_flagged = True
        db.session.commit()
        return jsonify({"message": "User flagged"}), 200

    @app.route('/api/admin/users/<int:user_id>/unflag', methods=['PATCH'])
    @jwt_required()
    @admin_required
    def admin_unflag_user(user_id):
        user = db.session.get(User, user_id)
        if not user: return jsonify({"message": "User not found"}), 404
        user.is_flagged = False
        db.session.commit()
        return jsonify({"message": "User unflagged"}), 200

    @app.route('/api/admin/campaigns/<int:campaign_id>/flag', methods=['PATCH'])
    @jwt_required()
    @admin_required
    def admin_flag_campaign(campaign_id):
        campaign = db.session.get(Campaign, campaign_id)
        if not campaign: return jsonify({"message": "Campaign not found"}), 404
        campaign.is_flagged = True
        db.session.commit()
        return jsonify({"message": "Campaign flagged"}), 200

    @app.route('/api/admin/campaigns/<int:campaign_id>/unflag', methods=['PATCH'])
    @jwt_required()
    @admin_required
    def admin_unflag_campaign(campaign_id):
        campaign = db.session.get(Campaign, campaign_id)
        if not campaign: return jsonify({"message": "Campaign not found"}), 404
        campaign.is_flagged = False
        db.session.commit()
        return jsonify({"message": "Campaign unflagged"}), 200

    # == Sponsor: Campaign Management ==
    @app.route('/api/sponsor/campaigns', methods=['POST'])
    @jwt_required()
    @sponsor_required
    def sponsor_create_campaign():
        data = request.get_json(); sponsor_id = get_jwt_identity()
        required = ['name', 'budget', 'start_date', 'visibility']
        if not all(f in data for f in required): return jsonify({"message": "Missing fields"}), 400
        try:
            start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')) if data.get('end_date') else None
            budget = float(data['budget'])
            if data['visibility'] not in ['public', 'private']: raise ValueError("Invalid visibility")
        except (ValueError, TypeError): return jsonify({"message": "Invalid date, budget, or visibility"}), 400

        campaign = Campaign(sponsor_id=sponsor_id, name=data['name'], budget=budget, start_date=start_date,
                            end_date=end_date, visibility=data['visibility'],
                            description=data.get('description'), goals=data.get('goals'))
        db.session.add(campaign); db.session.commit()
        return jsonify({"message": "Campaign created", "campaign": serialize_campaign_detail(campaign)}), 201

    @app.route('/api/sponsor/campaigns', methods=['GET'])
    @jwt_required()
    @sponsor_required
    def sponsor_get_campaigns():
        sponsor_id = get_jwt_identity()
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id).order_by(Campaign.created_at.desc()).all()
        return jsonify([serialize_campaign_detail(c) for c in campaigns]), 200

    @app.route('/api/sponsor/campaigns/<int:campaign_id>', methods=['GET'])
    @jwt_required()
    @sponsor_required
    def sponsor_get_campaign(campaign_id):
        sponsor_id = get_jwt_identity()
        campaign = Campaign.query.filter_by(id=campaign_id, sponsor_id=sponsor_id).first()
        if not campaign: return jsonify({"message": "Campaign not found or access denied"}), 404
        return jsonify(serialize_campaign_detail(campaign)), 200

    @app.route('/api/sponsor/campaigns/<int:campaign_id>', methods=['PUT'])
    @jwt_required()
    @sponsor_required
    def sponsor_update_campaign(campaign_id):
        sponsor_id = get_jwt_identity(); data = request.get_json()
        campaign = Campaign.query.filter_by(id=campaign_id, sponsor_id=sponsor_id).first()
        if not campaign: return jsonify({"message": "Campaign not found/denied"}), 404

        # Selective update
        if 'name' in data: campaign.name = data['name']
        if 'description' in data: campaign.description = data['description']
        if 'goals' in data: campaign.goals = data['goals']
        if 'visibility' in data and data['visibility'] in ['public', 'private']: campaign.visibility = data['visibility']
        if 'budget' in data:
            try: campaign.budget = float(data['budget'])
            except (ValueError, TypeError): pass # ignore invalid budget on update
        for date_field in ['start_date', 'end_date']:
             if date_field in data:
                  try:
                      date_val = datetime.fromisoformat(data[date_field].replace('Z', '+00:00')) if data[date_field] else None
                      setattr(campaign, date_field, date_val)
                  except (ValueError, TypeError): pass

        db.session.commit()
        return jsonify({"message": "Campaign updated", "campaign": serialize_campaign_detail(campaign)}), 200

    @app.route('/api/sponsor/campaigns/<int:campaign_id>', methods=['DELETE'])
    @jwt_required()
    @sponsor_required
    def sponsor_delete_campaign(campaign_id):
        sponsor_id = get_jwt_identity()
        campaign = Campaign.query.filter_by(id=campaign_id, sponsor_id=sponsor_id).first()
        if not campaign: return jsonify({"message": "Campaign not found/denied"}), 404
        db.session.delete(campaign); db.session.commit() # Cascade deletes AdRequests
        return jsonify({"message": "Campaign deleted"}), 200

    # == Sponsor: Ad Request Management ==
    @app.route('/api/sponsor/campaigns/<int:campaign_id>/ad_requests', methods=['POST'])
    @jwt_required()
    @sponsor_required
    def sponsor_create_ad_request(campaign_id):
        sponsor_id = get_jwt_identity()
        campaign = Campaign.query.filter_by(id=campaign_id, sponsor_id=sponsor_id).first()
        if not campaign: return jsonify({"message": "Campaign not found/denied"}), 404

        data = request.get_json()
        required = ['influencer_id', 'requirements', 'payment_amount']
        if not all(f in data for f in required): return jsonify({"message": "Missing fields"}), 400
        influencer = User.query.filter_by(id=data['influencer_id'], role='influencer', is_active=True).first()
        if not influencer: return jsonify({"message": "Active influencer not found"}), 404
        try: payment = float(data['payment_amount'])
        except (ValueError, TypeError): return jsonify({"message": "Invalid payment amount"}), 400

        # Check if a pending/accepted request already exists for this combo? Optional.
        existing_request = AdRequest.query.filter_by(
            campaign_id=campaign.id,
            influencer_id=influencer.id,
            status='Pending' # Or status in ['Pending', 'Accepted', 'Negotiating'] ?
        ).first()
        if existing_request:
            return jsonify({"message": "Pending ad request already exists for this influencer on this campaign"}), 409

        ad_request = AdRequest(
            campaign_id=campaign.id, influencer_id=influencer.id, initiator_id=sponsor_id, last_offer_by='sponsor',
            message=data.get('message'), requirements=data['requirements'], payment_amount=payment, status='Pending'
        )
        db.session.add(ad_request); db.session.commit()
        return jsonify({"message": "Ad request created", "ad_request": serialize_ad_request_detail(ad_request)}), 201

    @app.route('/api/sponsor/ad_requests', methods=['GET']) # Get all ad requests initiated by sponsor
    @jwt_required()
    @sponsor_required
    def sponsor_get_all_ad_requests():
        sponsor_id = get_jwt_identity()
        status_filter = request.args.get('status')
        campaign_id_filter = request.args.get('campaign_id')

        query = AdRequest.query.join(Campaign).filter(Campaign.sponsor_id == sponsor_id) # Filter by sponsor via campaign

        if status_filter: query = query.filter(AdRequest.status == status_filter)
        if campaign_id_filter:
             try: query = query.filter(AdRequest.campaign_id == int(campaign_id_filter))
             except ValueError: pass

        requests = query.order_by(AdRequest.updated_at.desc()).all()
        return jsonify([serialize_ad_request_detail(r) for r in requests]), 200

    @app.route('/api/sponsor/ad_requests/<int:ad_request_id>', methods=['PUT']) # Sponsor responds to negotiation
    @jwt_required()
    @sponsor_required
    def sponsor_negotiate_ad_request(ad_request_id):
        sponsor_id = get_jwt_identity()
        ad_request = db.session.get(AdRequest, ad_request_id)
        if not ad_request: return jsonify({"message": "Ad Request not found"}), 404
        if ad_request.campaign.sponsor_id != sponsor_id: return jsonify({"message": "Access denied"}), 403

        # Allow sponsor action only if status is 'Negotiating' and last offer was by influencer
        if ad_request.status != 'Negotiating' or ad_request.last_offer_by != 'influencer':
             return jsonify({"message": "Cannot modify request now or not sponsor's turn"}), 400

        data = request.get_json()
        action = data.get('action') # 'accept' (accept influencer's offer), 'reject', 'negotiate' (counter-offer)

        if action == 'accept':
            ad_request.status = 'Accepted'
            message = "Offer accepted"
        elif action == 'reject':
            ad_request.status = 'Rejected'
            message = "Offer rejected"
        elif action == 'negotiate':
            # Sponsor makes counter-offer
            new_payment = data.get('payment_amount')
            new_message = data.get('message')
            new_requirements = data.get('requirements') # Allow changing requirements?

            if new_payment is None: return jsonify({"message": "Payment amount required for counter-offer"}), 400
            try: ad_request.payment_amount = float(new_payment)
            except (ValueError, TypeError): return jsonify({"message": "Invalid payment amount"}), 400

            if new_message: ad_request.message = new_message
            if new_requirements: ad_request.requirements = new_requirements # Be careful allowing this

            ad_request.status = 'Negotiating' # Remains negotiating
            ad_request.last_offer_by = 'sponsor'
            message = "Counter-offer sent to influencer"
        else:
            return jsonify({"message": "Invalid action. Use 'accept', 'reject', or 'negotiate'."}), 400

        ad_request.updated_at = datetime.utcnow()
        db.session.commit()
        # Add notification logic later
        return jsonify({"message": message, "ad_request": serialize_ad_request_detail(ad_request)}), 200


    @app.route('/api/sponsor/ad_requests/<int:ad_request_id>', methods=['DELETE'])
    @jwt_required()
    @sponsor_required
    def sponsor_delete_ad_request(ad_request_id):
        sponsor_id = get_jwt_identity()
        ad_request = db.session.get(AdRequest, ad_request_id)
        if not ad_request: return jsonify({"message": "Ad Request not found"}), 404
        # Check ownership via campaign
        if ad_request.campaign.sponsor_id != sponsor_id: return jsonify({"message": "Access denied"}), 403
        if ad_request.status not in ['Pending', 'Rejected']: return jsonify({"message": "Cannot delete active request"}), 400

        db.session.delete(ad_request); db.session.commit()
        return jsonify({"message": "Ad Request deleted"}), 200

    # == Influencer: Ad Request Management ==
    @app.route('/api/influencer/ad_requests', methods=['GET'])
    @jwt_required()
    @influencer_required
    def influencer_get_ad_requests():
        influencer_id = get_jwt_identity()
        status_filter = request.args.get('status')
        query = AdRequest.query.filter_by(influencer_id=influencer_id)
        if status_filter: query = query.filter(AdRequest.status == status_filter)
        requests = query.order_by(AdRequest.updated_at.desc()).all()
        return jsonify([serialize_ad_request_detail(r) for r in requests]), 200

    @app.route('/api/influencer/ad_requests/<int:ad_request_id>', methods=['PATCH'])
    @jwt_required()
    @influencer_required
    def influencer_action_ad_request(ad_request_id):
        influencer_id = get_jwt_identity()
        ad_request = AdRequest.query.filter_by(id=ad_request_id, influencer_id=influencer_id).first()
        if not ad_request: return jsonify({"message": "Ad Request not found/denied"}), 404

        # Check allowed states for action
        allowed_states = ['Pending']
        if ad_request.status == 'Negotiating' and ad_request.last_offer_by == 'sponsor':
             allowed_states.append('Negotiating') # Allow response if sponsor made last offer

        if ad_request.status not in allowed_states:
             return jsonify({"message": f"Cannot action request in status '{ad_request.status}' or not influencer's turn"}), 400

        data = request.get_json()
        action = data.get('action') # 'accept', 'reject', 'negotiate'

        if action == 'accept':
            ad_request.status = 'Accepted'
            message = "Ad Request accepted"
        elif action == 'reject':
            ad_request.status = 'Rejected'
            message = "Ad Request rejected"
        elif action == 'negotiate':
            # Influencer makes counter-offer
            new_payment = data.get('payment_amount')
            new_message = data.get('message')
            if new_payment is None: return jsonify({"message": "Payment amount required to negotiate"}), 400
            try: ad_request.payment_amount = float(new_payment)
            except (ValueError, TypeError): return jsonify({"message": "Invalid payment amount"}), 400

            if new_message: ad_request.message = new_message
            ad_request.status = 'Negotiating' # Set/Keep status
            ad_request.last_offer_by = 'influencer'
            message = "Negotiation offer sent to sponsor"
        else:
            return jsonify({"message": "Invalid action. Use 'accept', 'reject', or 'negotiate'."}), 400

        ad_request.updated_at = datetime.utcnow()
        db.session.commit()
        # Add notification logic later
        return jsonify({"message": message, "ad_request": serialize_ad_request_detail(ad_request)}), 200

    # == Influencer: Apply to Public Campaigns ==
    @app.route('/api/influencer/campaigns/<int:campaign_id>/apply', methods=['POST'])
    @jwt_required()
    @influencer_required
    def influencer_apply_campaign(campaign_id):
        influencer_id = get_jwt_identity()
        campaign = Campaign.query.filter_by(id=campaign_id, visibility='public').first()
        if not campaign: return jsonify({"message": "Public campaign not found"}), 404

        data = request.get_json()
        requirements = data.get('requirements', "Influencer proposal based on campaign goals.") # Default or require input?
        payment_amount = data.get('payment_amount')
        message = data.get('message', "Interested in collaborating on this campaign.")

        if payment_amount is None: return jsonify({"message": "Proposed payment amount required"}), 400
        try: payment = float(payment_amount)
        except (ValueError, TypeError): return jsonify({"message": "Invalid payment amount"}), 400

        # Check if already applied/request exists
        existing_request = AdRequest.query.filter_by(
            campaign_id=campaign.id, influencer_id=influencer_id, status='Pending'
        ).first()
        if existing_request: return jsonify({"message": "You already have a pending application for this campaign"}), 409

        ad_request = AdRequest(
            campaign_id=campaign.id, influencer_id=influencer_id, initiator_id=influencer_id, # Influencer initiated
            last_offer_by='influencer', message=message, requirements=requirements,
            payment_amount=payment, status='Pending' # Sponsor needs to accept/reject this application
        )
        db.session.add(ad_request); db.session.commit()
        # Add notification to sponsor later
        return jsonify({"message": "Application submitted successfully", "ad_request": serialize_ad_request_detail(ad_request)}), 201


    # == Search Routes ==
    @app.route('/api/search/influencers', methods=['GET'])
    @jwt_required() # Any logged-in user can search
    def search_influencers():
        query = User.query.filter_by(role='influencer', is_active=True, is_flagged=False) # Exclude flagged
        if niche := request.args.get('niche'): query = query.filter(User.niche.ilike(f'%{niche}%'))
        if category := request.args.get('category'): query = query.filter(User.category == category)
        if reach_min_str := request.args.get('reach_min'):
            try: query = query.filter(User.reach >= int(reach_min_str))
            except (ValueError, TypeError): pass
        # Add pagination later
        influencers = query.order_by(User.reach.desc()).limit(50).all()
        return jsonify([serialize_user_profile(i) for i in influencers]), 200

    @app.route('/api/search/campaigns', methods=['GET'])
    @jwt_required() # Any logged-in user can search public campaigns
    def search_campaigns():
        query = Campaign.query.filter_by(visibility='public', is_flagged=False) # Exclude flagged
        if budget_min_str := request.args.get('budget_min'):
             try: query = query.filter(Campaign.budget >= float(budget_min_str))
             except (ValueError, TypeError): pass
        # Add other filters like category/niche if Campaigns get these fields later
        # Add pagination later
        campaigns = query.order_by(Campaign.created_at.desc()).limit(50).all()
        return jsonify([serialize_campaign_detail(c) for c in campaigns]), 200

    # Simple Health Check
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "OK"}), 200

    ```

2.  **Create `sponnect/backend/run.py` (Optional but Recommended):**
    ```
    # run.py
    from app import app

    if __name__ == '__main__':
        # Debug mode is controlled by FLASK_DEBUG in .env when using `flask run`
        # Or set directly here if running via `python run.py`
        app.run(debug=app.config['DEBUG'])
    ```

---

## Step 5: Database Initialization and Admin Creation

1.  **Initialize Database (in WSL terminal, inside `sponnect/backend`):**
    *   Set `FLASK_APP=app.py` (e.g., `export FLASK_APP=app.py` or ensure it's in `.env`).
    *   Run `flask db init` (only once per project, if not already done).
    *   Run `flask db migrate -m "Implement core features v2"`
    *   Run `flask db upgrade`

2.  **Create Admin User:**
    *   Run `flask create-admin`

---

## Step 6: Running the Application

1.  **Start the Server (in WSL terminal, inside `sponnect/backend`):**
    *   Run `flask run` (uses `.env` for config)

---

## Final Notes for AI Agent

*   This script generates the consolidated backend for Sponnect, including negotiation, flagging, and all core user/admin flows specified in the problem statement, *except* for background jobs (Celery) and caching (Redis).
*   The `sponnect/frontend` directory is ready for frontend development.
*   **Deferred/Excluded:** Background Jobs, Caching, advanced validation/error handling, comprehensive tests, detailed logging, real-time notifications, file uploads (if needed for campaigns/profiles).
*   The serializers are basic; consider Marshmallow for robust serialization/validation later.
*   Admin user creation relies on the `flask create-admin` CLI command and `.env` variables.
*   Ensure `.env` is correctly populated before running migrations or the app.

---
