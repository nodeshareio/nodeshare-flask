from flask import jsonify, request, url_for
from backend.models import Node
from backend.api import api
from backend.api.errors import bad_request
from backend import db
from backend.api.auth import token_auth
import json
from werkzeug.http import HTTP_STATUS_CODES


@api.route('/submit', methods=['POST'])
@token_auth.login_required
def submit_node():
    print(f"REQUEST DATA {request.data}")
    data = json.loads(request.data) or {'error: no data'}
    print(f"data: {data}")
    if 'ns_string' not in data:
        return bad_request('must include nodetext')
    if Node.query.filter_by(data=data['ns_string']).first():
        return bad_request('[  ERROR  ]  node text exists')
    print("[  INFO  ]  submit request")  
    print(f"[  NODE TEXT  ]  {data['ns_string']}")  
    node = Node()
    node.from_dict(data, approved=False)
    db.session.add(node)
    db.session.commit()
    response = jsonify(data)
    response.status_code = 201
    return response