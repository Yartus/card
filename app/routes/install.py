from flask import Blueprint, request, jsonify

bp = Blueprint('install', __name__, url_prefix='/install')

@bp.route('/', methods=['GET'])
def install():
    # TODO: use WeCom SDK to generate install URL
    tenant_name = request.args.get('tenant_name', 'demo')
    auth_url = 'https://wecom.fake/authorize?tenant=' + tenant_name
    return jsonify({'tenant_name': tenant_name, 'auth_url': auth_url})