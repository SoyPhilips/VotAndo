from flask import Blueprint, request, jsonify
from .models import db, Proposal, Vote, AuditLog, User
import jwt
import os
from datetime import datetime

api_bp = Blueprint('api', __name__)
SECRET_KEY = os.environ.get('SECRET_KEY', 'vota-ciudadano-super-secret-key')

def get_current_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except:
        return None

@api_bp.route('/proposals', methods=['GET'])
def get_proposals():
    proposals = Proposal.query.all()
    return jsonify([p.to_dict() for p in proposals])

@api_bp.route('/proposals', methods=['POST'])
def create_proposal():
    user_payload = get_current_user()
    if not user_payload or not user_payload.get('is_admin'):
        return jsonify({'error': 'Unauthorized. Admin only.'}), 403

    data = request.get_json()
    try:
        new_proposal = Proposal(
            title=data['title'],
            description=data['description'],
            category=data['category'],
            start_date=datetime.fromisoformat(data['start_date']),
            end_date=datetime.fromisoformat(data['end_date']),
            status='active'
        )
        db.session.add(new_proposal)
        db.session.commit()

        log = AuditLog(action='PROPOSAL_CREATE', user_id=user_payload['user_id'], details=f'Created: {new_proposal.title}', ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()

        return jsonify(new_proposal.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_bp.route('/vote', methods=['POST'])
def cast_vote():
    data = request.get_json()
    proposal_id = data.get('proposal_id')
    proposal = Proposal.query.get(proposal_id)

    if not proposal or proposal.status != 'active':
        return jsonify({'error': 'Invalid or inactive proposal'}), 400

    user_payload = get_current_user()
    
    if user_payload:
        # Identified vote
        user_id = user_payload['user_id']
        existing_vote = Vote.query.filter_by(proposal_id=proposal_id, user_id=user_id).first()
        if existing_vote:
            return jsonify({'error': 'You have already voted for this proposal'}), 400
        
        is_anonymous = False
    else:
        # Anonymous vote check (basic IP-based or Cookie-based)
        # Requirement: use cookies or session. We'll check for a custom header/cookie from frontend
        anon_id = request.headers.get('X-Anon-Voter-ID')
        if not anon_id:
             return jsonify({'error': 'Anonymous ID required'}), 400
        
        # Check if this anon ID already voted for this proposal in this session
        existing_vote = Vote.query.filter_by(proposal_id=proposal_id, ip_address=anon_id).first()
        if existing_vote:
            return jsonify({'error': 'You have already voted for this proposal anonymously'}), 400
        
        user_id = None
        is_anonymous = True

    vote_hash = Vote.generate_hash(proposal_id, user_id if user_id else 'anon', datetime.utcnow().timestamp())
    
    new_vote = Vote(
        proposal_id=proposal_id,
        user_id=user_id,
        is_anonymous=is_anonymous,
        vote_hash=vote_hash,
        ip_address=request.headers.get('X-Anon-Voter-ID') if is_anonymous else request.remote_addr
    )
    
    db.session.add(new_vote)
    
    log = AuditLog(
        action='VOTE_CAST', 
        user_id=user_id, 
        details=f'Voted on proposal {proposal_id} (Anon: {is_anonymous})', 
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({'message': 'Vote cast successfully', 'hash': vote_hash})

@api_bp.route('/results/<int:proposal_id>', methods=['GET'])
def get_results(proposal_id):
    proposal = Proposal.query.get_or_404(proposal_id)
    total_votes = len(proposal.votes)
    anon_votes = Vote.query.filter_by(proposal_id=proposal_id, is_anonymous=True).count()
    id_votes = total_votes - anon_votes

    return jsonify({
        'proposal_id': proposal_id,
        'total_votes': total_votes,
        'anonymous_votes': anon_votes,
        'identified_votes': id_votes,
        'status': proposal.status
    })

@api_bp.route('/proposal-request', methods=['POST'])
def create_proposal_request():
    user_payload = get_current_user()
    if not user_payload:
        return jsonify({'error': 'Debes iniciar sesión para realizar esta solicitud'}), 401
    
    from .models import ProposalRequest
    data = request.get_json()
    reason = data.get('reason')

    if not reason:
        return jsonify({'error': 'Debes proporcionar una razón'}), 400

    # Check if there's already a pending request
    existing = ProposalRequest.query.filter_by(user_id=user_payload['user_id'], status='pending').first()
    if existing:
        return jsonify({'error': 'Ya tienes una solicitud pendiente'}), 400

    new_request = ProposalRequest(
        user_id=user_payload['user_id'],
        reason=reason
    )
    db.session.add(new_request)
    db.session.commit()

    log = AuditLog(action='PROPOSAL_REQ_CREATE', user_id=user_payload['user_id'], details=f'Reason: {reason[:50]}...', ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()

    return jsonify({'message': 'Solicitud enviada correctamente', 'status': 'pending'})

@api_bp.route('/my-requests', methods=['GET'])
def get_my_requests():
    user_payload = get_current_user()
    if not user_payload:
        return jsonify({'error': 'Unauthorized'}), 401
    
    from .models import ProposalRequest
    reqs = ProposalRequest.query.filter_by(user_id=user_payload['user_id']).all()
    return jsonify([{
        'id': r.id,
        'reason': r.reason,
        'status': r.status,
        'created_at': r.created_at.isoformat()
    } for r in reqs])
