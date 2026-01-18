from flask import Blueprint, request, jsonify
from ..main import db
from ..models import Tenant

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/callback', methods=['POST'])
def callback():
    # TODO: validate and parse WeCom auth callback, store tenant info
    data = request.get_json() or {}
    corp_id = data.get('corp_id', 'corp_demo')
    tenant = Tenant(corp_id=corp_id, name=data.get('corp_name', 'Demo Corp'), plan='free')
    db.session.add(tenant)
    db.session.commit()
    return jsonify({'status': 'ok', 'tenant_id': tenant.id})