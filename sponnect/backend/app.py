# app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_jwt, verify_jwt_in_request
)
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func # For stats count
from math import ceil # For pagination calculation


from config import Config
from models import db, User, Campaign, AdRequest

# --- App Initialization ---
app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "http://localhost:5173"}})
app.config.from_object(Config)

# --- Extension Initialization ---
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)


def serialize_pagination(pagination_obj):
    """Helper to generate pagination metadata."""
    return {
        'page': pagination_obj.page,
        'per_page': pagination_obj.per_page,
        'total_pages': pagination_obj.pages,
        'total_items': pagination_obj.total,
        'has_prev': pagination_obj.has_prev,
        'has_next': pagination_obj.has_next,
        'prev_num': pagination_obj.prev_num,
        'next_num': pagination_obj.next_num
    }


# --- Add Negotiation History ---
class NegotiationHistory(db.Model):
    __tablename__ = 'negotiation_history'
    id = db.Column(db.Integer, primary_key=True)
    ad_request_id = db.Column(db.Integer, db.ForeignKey('ad_requests.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_role = db.Column(db.String(20), nullable=False)  # 'sponsor' or 'influencer'
    action = db.Column(db.String(20), nullable=False)  # 'propose', 'counter', 'accept', 'reject'
    message = db.Column(db.Text, nullable=True)
    payment_amount = db.Column(db.Float, nullable=True)
    requirements = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    ad_request = db.relationship('AdRequest', backref=db.backref('negotiation_history', lazy='dynamic', cascade='all, delete-orphan'))
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<NegotiationHistory {self.id} AdRequest:{self.ad_request_id} Action:{self.action}>'

# Create migration for the new model
with app.app_context():
    db.create_all()

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

def serialize_negotiation_history(history_item):
    return {
        'id': history_item.id,
        'ad_request_id': history_item.ad_request_id,
        'user_id': history_item.user_id,
        'user_role': history_item.user_role,
        'action': history_item.action,
        'message': history_item.message,
        'payment_amount': history_item.payment_amount,
        'requirements': history_item.requirements,
        'created_at': history_item.created_at.isoformat() if history_item.created_at else None,
        'username': history_item.user.username if history_item.user else None,
    }

# --- CLI Command for Admin Creation ---
@app.cli.command("create-admin")
def create_admin_command():
    """Creates the admin user from .env variables."""
    admin_email = Config.ADMIN_EMAIL
    admin_password = Config.ADMIN_PASSWORD
    if not admin_email or not admin_password:
        print("Error: ADMIN_EMAIL and ADMIN_PASSWORD missing in .env")
        return

    with app.app_context():  # Important: establish app context
        if User.query.filter_by(email=admin_email, role='admin').first():
            print(f"Admin '{admin_email}' already exists.")
            return

        admin_user = User(
            username=Config.ADMIN_USERNAME,  # Use ADMIN_USERNAME from config
            email=Config.ADMIN_EMAIL,
            role='admin',
            is_active=True,
            sponsor_approved=True
        )
        admin_user.set_password(admin_password)
        db.session.add(admin_user)
        try:
            db.session.commit()
            print(f"Admin user '{admin_email}' created.")
        except Exception as e:  # Handle potential database errors
            print(f"Error creating admin user: {e}")
            db.session.rollback()  # Rollback changes in case of error


# --- Routes ---

# == Authentication ==
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'influencer')  # Defaults to influencer

    if not username or not password or not email:  # Require email now
        return jsonify({"message": "Username, email, and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 409

    if User.query.filter_by(email=email).first():  # Check for existing email
        return jsonify({"message": "Email already exists"}), 409


    if role not in ['influencer', 'sponsor']:
        return jsonify({"message": "Invalid role"}), 400

    user = User(username=username, email=email, role=role)  # Store email!
    user.set_password(password)  # Ensure proper password hashing (see previous responses)
    message = ""

    if role == 'sponsor':
        user.company_name = data.get('company_name')
        user.industry = data.get('industry')
        user.sponsor_approved = False  # Requires approval
        message = "Sponsor registered. Account requires admin approval."
    else:  # influencer
        user.influencer_name = data.get('influencer_name')
        user.category = data.get('category')
        user.niche = data.get('niche')
        user.reach = data.get('reach')
        message = "Influencer registered successfully."

    db.session.add(user)
    db.session.commit()
    return jsonify({"message": message, "user_id": user.id}), 201  # Return user ID

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')  # Get email separately
    password = data.get('password')

    if not password:
        return jsonify({"message": "Password is required"}), 400

    if username:
        user = User.query.filter_by(username=username).first()
    elif email:
        user = User.query.filter_by(email=email).first()
    else:
        return jsonify({"message": "Username or email is required"}), 400 # More specific



    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    # ... (rest of the login logic remains the same)
    if not user.is_active:
        return jsonify({"message": "Account deactivated"}), 403
    # Check sponsor approval status only if user is a sponsor
    if user.role == 'sponsor' and not user.sponsor_approved:
        return jsonify({"message": "Sponsor account pending approval"}), 403

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
    db.session.add(ad_request)
    db.session.flush()  # Get the ad_request ID before committing
    
    # Create initial history record
    history = NegotiationHistory(
        ad_request_id=ad_request.id,
        user_id=sponsor_id,
        user_role='sponsor',
        action='propose',
        message=data.get('message'),
        payment_amount=payment,
        requirements=data['requirements']
    )
    db.session.add(history)
    
    db.session.commit()
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

    # Create history record
    history = NegotiationHistory(
        ad_request_id=ad_request.id,
        user_id=sponsor_id,
        user_role='sponsor',
        action=action,
        message=data.get('message'),
        payment_amount=data.get('payment_amount', ad_request.payment_amount),
        requirements=data.get('requirements')
    )
    db.session.add(history)

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

    # Create history record
    history = NegotiationHistory(
        ad_request_id=ad_request.id,
        user_id=influencer_id,
        user_role='influencer',
        action=action,
        message=data.get('message'),
        payment_amount=data.get('payment_amount', ad_request.payment_amount),
        requirements=None  # Influencers don't typically modify requirements
    )
    db.session.add(history)

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
    db.session.add(ad_request)
    db.session.flush()  # Get the ad_request ID before committing
    
    # Create initial history record
    history = NegotiationHistory(
        ad_request_id=ad_request.id,
        user_id=influencer_id,
        user_role='influencer',
        action='propose',
        message=message,
        payment_amount=payment,
        requirements=requirements
    )
    db.session.add(history)
    
    db.session.commit()
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

# == ChartJS Data Endpoints ==
@app.route('/api/charts/user-growth', methods=['GET'])
@jwt_required()
@admin_required
def chart_user_growth():
    """Returns time-series data of user registrations for ChartJS"""
    # Get time period from query params (default: last 6 months)
    months = int(request.args.get('months', 6))
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30 * months)
    
    # Query users by role and registration date
    influencers_by_month = db.session.query(
        func.strftime('%Y-%m', User.created_at).label('month'),
        func.count().label('count')
    ).filter(
        User.role == 'influencer',
        User.created_at >= start_date,
        User.created_at <= end_date
    ).group_by('month').order_by('month').all()
    
    sponsors_by_month = db.session.query(
        func.strftime('%Y-%m', User.created_at).label('month'),
        func.count().label('count')
    ).filter(
        User.role == 'sponsor',
        User.created_at >= start_date,
        User.created_at <= end_date
    ).group_by('month').order_by('month').all()
    
    # Generate all months in range (for complete labels even if no data)
    all_months = []
    current = start_date.replace(day=1)
    while current <= end_date:
        all_months.append(current.strftime('%Y-%m'))
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    
    # Convert query results to dict for easier lookup
    inf_data = {m: c for m, c in influencers_by_month}
    spo_data = {m: c for m, c in sponsors_by_month}
    
    # Format data for ChartJS
    chart_data = {
        'labels': all_months,
        'datasets': [
            {
                'label': 'Influencers',
                'data': [inf_data.get(m, 0) for m in all_months],
                'borderColor': 'rgba(75, 192, 192, 1)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            },
            {
                'label': 'Sponsors',
                'data': [spo_data.get(m, 0) for m in all_months],
                'borderColor': 'rgba(153, 102, 255, 1)',
                'backgroundColor': 'rgba(153, 102, 255, 0.2)',
            }
        ]
    }
    
    return jsonify(chart_data), 200

@app.route('/api/charts/campaign-distribution', methods=['GET'])
@jwt_required()
@admin_required
def chart_campaign_distribution():
    """Returns budget distribution data of campaigns for ChartJS"""
    # Define budget ranges for grouping
    ranges = [
        (0, 1000),
        (1000, 5000),
        (5000, 10000),
        (10000, 50000),
        (50000, float('inf'))
    ]
    
    range_labels = [
        'Under $1K',
        '$1K-$5K',
        '$5K-$10K',
        '$10K-$50K',
        'Over $50K'
    ]
    
    # Count campaigns in each budget range
    counts = []
    for i, (min_val, max_val) in enumerate(ranges):
        if max_val == float('inf'):
            count = Campaign.query.filter(Campaign.budget >= min_val).count()
        else:
            count = Campaign.query.filter(Campaign.budget >= min_val, Campaign.budget < max_val).count()
        counts.append(count)
    
    # Prepare data for ChartJS Pie/Doughnut chart
    chart_data = {
        'labels': range_labels,
        'datasets': [{
            'data': counts,
            'backgroundColor': [
                'rgba(255, 99, 132, 0.6)',
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(153, 102, 255, 0.6)',
            ],
            'borderColor': [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
            ],
            'borderWidth': 1
        }]
    }
    
    return jsonify(chart_data), 200

@app.route('/api/charts/ad-request-status', methods=['GET'])
@jwt_required()
@admin_required
def chart_ad_request_status():
    """Returns distribution of ad request statuses for ChartJS"""
    # Get counts by status
    status_counts = db.session.query(
        AdRequest.status,
        func.count().label('count')
    ).group_by(AdRequest.status).all()
    
    # Convert to lists for ChartJS
    statuses = [status for status, _ in status_counts]
    counts = [count for _, count in status_counts]
    
    # Prepare data for ChartJS
    chart_data = {
        'labels': statuses,
        'datasets': [{
            'label': 'Ad Requests by Status',
            'data': counts,
            'backgroundColor': [
                'rgba(54, 162, 235, 0.6)',  # Pending - Blue
                'rgba(75, 192, 192, 0.6)',  # Accepted - Green
                'rgba(255, 99, 132, 0.6)',  # Rejected - Red
                'rgba(255, 206, 86, 0.6)',  # Negotiating - Yellow
            ],
            'borderColor': [
                'rgba(54, 162, 235, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(255, 99, 132, 1)',
                'rgba(255, 206, 86, 1)',
            ],
            'borderWidth': 1
        }]
    }
    
    return jsonify(chart_data), 200

@app.route('/api/charts/campaign-activity', methods=['GET'])
@jwt_required()
@admin_required
def chart_campaign_activity():
    """Returns time-series data of campaign creation and ad requests for ChartJS"""
    # Get time period from query params (default: last 6 months)
    months = int(request.args.get('months', 6))
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30 * months)
    
    # Query campaigns by creation date
    campaigns_by_month = db.session.query(
        func.strftime('%Y-%m', Campaign.created_at).label('month'),
        func.count().label('count')
    ).filter(
        Campaign.created_at >= start_date,
        Campaign.created_at <= end_date
    ).group_by('month').order_by('month').all()
    
    # Query ad requests by creation date
    requests_by_month = db.session.query(
        func.strftime('%Y-%m', AdRequest.created_at).label('month'),
        func.count().label('count')
    ).filter(
        AdRequest.created_at >= start_date,
        AdRequest.created_at <= end_date
    ).group_by('month').order_by('month').all()
    
    # Generate all months in range
    all_months = []
    current = start_date.replace(day=1)
    while current <= end_date:
        all_months.append(current.strftime('%Y-%m'))
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    
    # Convert query results to dict for easier lookup
    camp_data = {m: c for m, c in campaigns_by_month}
    req_data = {m: c for m, c in requests_by_month}
    
    # Format data for ChartJS
    chart_data = {
        'labels': all_months,
        'datasets': [
            {
                'label': 'New Campaigns',
                'data': [camp_data.get(m, 0) for m in all_months],
                'borderColor': 'rgba(255, 99, 132, 1)',
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'type': 'line'
            },
            {
                'label': 'Ad Requests',
                'data': [req_data.get(m, 0) for m in all_months],
                'borderColor': 'rgba(54, 162, 235, 1)',
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'type': 'bar'
            }
        ]
    }
    
    return jsonify(chart_data), 200

@app.route('/api/charts/conversion-rates', methods=['GET'])
@jwt_required()
@admin_required
def chart_conversion_rates():
    """Returns conversion rates from ad requests to accepted partnerships"""
    # Get time period from query params (default: last 6 months)
    months = int(request.args.get('months', 6))
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30 * months)
    
    # Group by month and count total requests
    total_by_month = db.session.query(
        func.strftime('%Y-%m', AdRequest.created_at).label('month'),
        func.count().label('count')
    ).filter(
        AdRequest.created_at >= start_date,
        AdRequest.created_at <= end_date
    ).group_by('month').order_by('month').all()
    
    # Group by month and count accepted requests
    accepted_by_month = db.session.query(
        func.strftime('%Y-%m', AdRequest.created_at).label('month'),
        func.count().label('count')
    ).filter(
        AdRequest.created_at >= start_date,
        AdRequest.created_at <= end_date,
        AdRequest.status == 'Accepted'
    ).group_by('month').order_by('month').all()
    
    # Generate all months in range
    all_months = []
    current = start_date.replace(day=1)
    while current <= end_date:
        all_months.append(current.strftime('%Y-%m'))
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    
    # Convert query results to dict for easier lookup
    total_data = {m: c for m, c in total_by_month}
    accepted_data = {m: c for m, c in accepted_by_month}
    
    # Calculate conversion rates (as percentage)
    conversion_rates = []
    for month in all_months:
        total = total_data.get(month, 0)
        accepted = accepted_data.get(month, 0)
        rate = (accepted / total * 100) if total > 0 else 0
        conversion_rates.append(round(rate, 1))
    
    # Format data for ChartJS
    chart_data = {
        'labels': all_months,
        'datasets': [{
            'label': 'Conversion Rate (%)',
            'data': conversion_rates,
            'borderColor': 'rgba(75, 192, 192, 1)',
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            'borderWidth': 2,
            'fill': False,
            'tension': 0.1
        }]
    }
    
    return jsonify(chart_data), 200

@app.route('/api/charts/dashboard-summary', methods=['GET'])
@jwt_required()
@admin_required
def chart_dashboard_summary():
    """Returns summarized data for dashboard charts"""
    # Get stats for different user types
    total_influencers = User.query.filter_by(role='influencer').count()
    active_influencers = User.query.filter_by(role='influencer', is_active=True).count()
    
    total_sponsors = User.query.filter_by(role='sponsor').count()
    approved_sponsors = User.query.filter_by(role='sponsor', sponsor_approved=True).count()
    
    # Get campaign stats
    public_campaigns = Campaign.query.filter_by(visibility='public').count()
    private_campaigns = Campaign.query.filter_by(visibility='private').count()
    
    # Get ad request stats
    total_requests = AdRequest.query.count()
    accepted_requests = AdRequest.query.filter_by(status='Accepted').count()
    pending_requests = AdRequest.query.filter_by(status='Pending').count()
    rejected_requests = AdRequest.query.filter_by(status='Rejected').count()
    negotiating_requests = AdRequest.query.filter_by(status='Negotiating').count()
    
    # Prepare data for multiple chart types
    chart_data = {
        'userSummary': {
            'labels': ['Active Influencers', 'Inactive Influencers', 'Approved Sponsors', 'Pending Sponsors'],
            'datasets': [{
                'data': [
                    active_influencers,
                    total_influencers - active_influencers,
                    approved_sponsors,
                    total_sponsors - approved_sponsors
                ],
                'backgroundColor': [
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.6)',
                    'rgba(153, 102, 255, 0.2)'
                ]
            }]
        },
        'campaignVisibility': {
            'labels': ['Public', 'Private'],
            'datasets': [{
                'data': [public_campaigns, private_campaigns],
                'backgroundColor': ['rgba(54, 162, 235, 0.6)', 'rgba(255, 99, 132, 0.6)']
            }]
        },
        'adRequestStatus': {
            'labels': ['Accepted', 'Pending', 'Rejected', 'Negotiating'],
            'datasets': [{
                'data': [accepted_requests, pending_requests, rejected_requests, negotiating_requests],
                'backgroundColor': [
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(255, 206, 86, 0.6)'
                ]
            }]
        },
        'conversionRate': {
            'value': round((accepted_requests / total_requests * 100), 1) if total_requests > 0 else 0,
            'label': 'Acceptance Rate'
        }
    }
    
    return jsonify(chart_data), 200

# == Negotiation History Endpoints ==
@app.route('/api/ad_requests/<int:ad_request_id>/history', methods=['GET'])
@jwt_required()
def get_negotiation_history(ad_request_id):
    """Get negotiation history for an ad request (available to both parties involved)"""
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    # Find the ad request
    ad_request = db.session.get(AdRequest, ad_request_id)
    if not ad_request:
        return jsonify({"message": "Ad request not found"}), 404
    
    # Check if user is authorized to view this history (either the sponsor or the influencer)
    is_sponsor = user_role == 'sponsor' and ad_request.campaign.sponsor_id == user_id
    is_influencer = user_role == 'influencer' and ad_request.influencer_id == user_id
    is_admin = user_role == 'admin'
    
    if not (is_sponsor or is_influencer or is_admin):
        return jsonify({"message": "You are not authorized to view this negotiation history"}), 403
    
    # Get history sorted by creation date
    history = NegotiationHistory.query.filter_by(ad_request_id=ad_request_id).order_by(NegotiationHistory.created_at).all()
    
    # Include ad request details for context
    result = {
        'ad_request': serialize_ad_request_detail(ad_request),
        'history': [serialize_negotiation_history(item) for item in history]
    }
    
    return jsonify(result), 200

@app.route('/api/sponsor/campaigns/<int:campaign_id>/negotiation_summary', methods=['GET'])
@jwt_required()
@sponsor_required
def sponsor_campaign_negotiation_summary(campaign_id):
    """Get summary of negotiations for a sponsor's campaign"""
    sponsor_id = get_jwt_identity()
    
    # Check campaign ownership
    campaign = Campaign.query.filter_by(id=campaign_id, sponsor_id=sponsor_id).first()
    if not campaign:
        return jsonify({"message": "Campaign not found or access denied"}), 404
    
    # Get all ad requests for this campaign
    ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id).all()
    
    # For each ad request, get the latest negotiation history
    results = []
    for ad_request in ad_requests:
        latest_history = NegotiationHistory.query.filter_by(ad_request_id=ad_request.id).order_by(NegotiationHistory.created_at.desc()).first()
        
        if latest_history:
            results.append({
                'ad_request': serialize_ad_request_detail(ad_request),
                'latest_action': {
                    'user_role': latest_history.user_role,
                    'action': latest_history.action,
                    'payment_amount': latest_history.payment_amount,
                    'created_at': latest_history.created_at.isoformat() if latest_history.created_at else None,
                }
            })
    
    return jsonify(results), 200

@app.route('/api/influencer/negotiations', methods=['GET'])
@jwt_required()
@influencer_required
def influencer_negotiations():
    """Get all negotiations the influencer is involved in"""
    influencer_id = get_jwt_identity()
    
    # Get all ad requests where this user is the influencer
    ad_requests = AdRequest.query.filter_by(influencer_id=influencer_id).all()
    
    # For each ad request, get the latest negotiation
    results = []
    for ad_request in ad_requests:
        latest_history = NegotiationHistory.query.filter_by(ad_request_id=ad_request.id).order_by(NegotiationHistory.created_at.desc()).first()
        
        if latest_history:
            results.append({
                'ad_request': serialize_ad_request_detail(ad_request),
                'latest_action': {
                    'user_role': latest_history.user_role,
                    'action': latest_history.action,
                    'payment_amount': latest_history.payment_amount,
                    'created_at': latest_history.created_at.isoformat() if latest_history.created_at else None,
                }
            })
    
    return jsonify(results), 200

# Simple Health Check
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK"}), 200


# == Admin Actions (Additions/Modifications) ==

@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
@admin_required
def admin_list_users():
    """List and search users with filters and pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search_term = request.args.get('search', None, type=str)
        role_filter = request.args.get('role', None, type=str)
        flagged_filter = request.args.get('flagged', None, type=str) # 'true' or 'false'
        status_filter = request.args.get('status', None, type=str) # 'active', 'inactive', 'pending_approval', 'approved'

        query = User.query.filter(User.role != 'admin') # Exclude admin itself

        # Apply Filters
        if role_filter and role_filter in ['sponsor', 'influencer']:
            query = query.filter(User.role == role_filter)

        if flagged_filter is not None:
            query = query.filter(User.is_flagged == (flagged_filter.lower() == 'true'))

        if status_filter:
            if status_filter == 'active':
                query = query.filter(User.is_active == True)
            elif status_filter == 'inactive':
                query = query.filter(User.is_active == False)
            elif status_filter == 'pending_approval':
                query = query.filter(User.role == 'sponsor', User.sponsor_approved == False, User.is_active == True)
            elif status_filter == 'approved':
                 query = query.filter(User.role == 'sponsor', User.sponsor_approved == True, User.is_active == True)

        # Apply Search (simple search on username, sponsor/influencer name)
        if search_term:
            search_like = f"%{search_term}%"
            query = query.filter(
                or_(
                    User.username.ilike(search_like),
                    User.company_name.ilike(search_like),
                    User.influencer_name.ilike(search_like)
                )
            )

        # Apply Sorting (optional, e.g., by creation date or username)
        query = query.order_by(User.created_at.desc())

        # Apply Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False) # error_out=False avoids 404 on invalid page [2, 8]

        return jsonify({
            'users': [serialize_user_profile(user) for user in pagination.items],
            'pagination': serialize_pagination(pagination)
        }), 200

    except Exception as e:
        # Log the exception e
        return jsonify({"message": "An error occurred while fetching users."}), 500


@app.route('/api/admin/users/<int:user_id>/deactivate', methods=['PATCH'])
@jwt_required()
@admin_required
def admin_deactivate_user(user_id):
    user = db.session.get(User, user_id)
    if not user or user.role == 'admin':
        return jsonify({"message": "User not found or cannot deactivate admin"}), 404
    if not user.is_active:
         return jsonify({"message": "User already inactive"}), 400

    user.is_active = False
    db.session.commit()
    return jsonify({"message": "User deactivated successfully"}), 200

@app.route('/api/admin/users/<int:user_id>/activate', methods=['PATCH'])
@jwt_required()
@admin_required
def admin_activate_user(user_id):
    user = db.session.get(User, user_id)
    if not user or user.role == 'admin':
        return jsonify({"message": "User not found"}), 404
    if user.is_active:
         return jsonify({"message": "User already active"}), 400

    # Special check for sponsors: only activate if they are approved
    if user.role == 'sponsor' and not user.sponsor_approved:
         return jsonify({"message": "Cannot activate a sponsor whose registration is not approved"}), 400

    user.is_active = True
    db.session.commit()
    return jsonify({"message": "User activated successfully"}), 200


# Keep existing flag/unflag endpoints as they are functionally correct [1]
# @app.route('/api/admin/users/<int:user_id>/flag', methods=['PATCH']) ...
# @app.route('/api/admin/users/<int:user_id>/unflag', methods=['PATCH']) ...


# == Sponsor: Handling Influencer Applications ==

@app.route('/api/sponsor/campaigns/<int:campaign_id>/applications', methods=['GET'])
@jwt_required()
@sponsor_required
def sponsor_get_campaign_applications(campaign_id):
    """Get AdRequests initiated by influencers for a specific campaign."""
    sponsor_id = get_jwt_identity()

    # Verify campaign exists and belongs to the sponsor
    campaign = Campaign.query.filter_by(id=campaign_id, sponsor_id=sponsor_id).first()
    if not campaign:
        return jsonify({"message": "Campaign not found or access denied"}), 404

    # Get filters and pagination params
    status_filter = request.args.get('status', 'Pending') # Default to pending applications
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Query AdRequests for this campaign initiated by influencers
    query = AdRequest.query.filter(
        AdRequest.campaign_id == campaign_id,
        AdRequest.initiator_id == AdRequest.influencer_id # Ensure influencer started it
    )

    if status_filter:
        query = query.filter(AdRequest.status == status_filter)

    query = query.order_by(AdRequest.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'applications': [serialize_ad_request_detail(req) for req in pagination.items],
        'pagination': serialize_pagination(pagination)
    }), 200

@app.route('/api/sponsor/applications/<int:ad_request_id>/accept', methods=['PATCH'])
@jwt_required()
@sponsor_required
def sponsor_accept_application(ad_request_id):
    """Sponsor accepts an influencer's application (AdRequest)."""
    sponsor_id = get_jwt_identity()
    ad_request = db.session.get(AdRequest, ad_request_id)

    if not ad_request:
        return jsonify({"message": "Application (Ad Request) not found"}), 404
    # Verify ownership via campaign
    if ad_request.campaign.sponsor_id != sponsor_id:
        return jsonify({"message": "Access denied"}), 403
    # Verify it's a pending application initiated by the influencer
    if not (ad_request.status == 'Pending' and ad_request.initiator_id == ad_request.influencer_id):
        return jsonify({"message": "Application is not pending or was not initiated by the influencer"}), 400

    ad_request.status = 'Accepted' # Now it's an active agreement
    ad_request.updated_at = datetime.utcnow()

    # Log this action in history
    history = NegotiationHistory(
        ad_request_id=ad_request.id,
        user_id=sponsor_id,
        user_role='sponsor',
        action='accept_application', # Distinguish from accepting a negotiation counter-offer
        message="Sponsor accepted influencer's initial application.",
        payment_amount=ad_request.payment_amount,
        requirements=ad_request.requirements
    )
    db.session.add(history)
    db.session.commit()

    # Add notification logic here if implemented

    return jsonify({
        "message": "Influencer application accepted",
        "ad_request": serialize_ad_request_detail(ad_request)
    }), 200

@app.route('/api/sponsor/applications/<int:ad_request_id>/reject', methods=['PATCH'])
@jwt_required()
@sponsor_required
def sponsor_reject_application(ad_request_id):
    """Sponsor rejects an influencer's application (AdRequest)."""
    sponsor_id = get_jwt_identity()
    ad_request = db.session.get(AdRequest, ad_request_id)

    if not ad_request:
        return jsonify({"message": "Application (Ad Request) not found"}), 404
    # Verify ownership via campaign
    if ad_request.campaign.sponsor_id != sponsor_id:
        return jsonify({"message": "Access denied"}), 403
    # Verify it's a pending application initiated by the influencer
    if not (ad_request.status == 'Pending' and ad_request.initiator_id == ad_request.influencer_id):
        return jsonify({"message": "Application is not pending or was not initiated by the influencer"}), 400

    ad_request.status = 'Rejected'
    ad_request.updated_at = datetime.utcnow()

    # Log this action in history
    history = NegotiationHistory(
        ad_request_id=ad_request.id,
        user_id=sponsor_id,
        user_role='sponsor',
        action='reject_application',
        message="Sponsor rejected influencer's initial application.",
        payment_amount=ad_request.payment_amount,
        requirements=ad_request.requirements
    )
    db.session.add(history)
    db.session.commit()

    # Add notification logic here if implemented

    return jsonify({"message": "Influencer application rejected"}), 200
