from flask import Blueprint, jsonify

bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@bp.route('/sync_members', methods=['POST'])
def sync_members():
    # TODO: call WeCom SDK to fetch members and upsert
    return jsonify({'status': 'sync_started'})

@bp.route('/push_card', methods=['POST'])
def push_card():
    # TODO: compose card and call WeCom SDK to push
    return jsonify({'status': 'push_enqueued'})