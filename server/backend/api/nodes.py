from flask import jsonify, request, url_for
from backend.models import Node
from backend.api import api
from backend.api.errors import bad_request
from backend import db, mqtt
from backend.api.auth import token_auth
import json
from werkzeug.http import HTTP_STATUS_CODES 


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    topic = 'nodeshare/submit/ack'
    print(f"Subscribing to {topic}")
    mqtt.subscribe(topic)

@mqtt.on_topic('nodeshare/submit/ack')
def handle_submit_ack(client, userdata, message):
    if message.payload == 'failed submission':
        print('Node Denied!')
    else:
        print('Node Approved!')

@api.route('/submit', methods=['POST'])
@token_auth.login_required
def submit_node():
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
    try:
        db.session.add(node)
        db.session.commit()
        mqtt.publish('nodeshare/submit', node.data)
    except:
        print("[  INFO  ] DB Commit Failure: Node not submitted")
    response = jsonify(data)
    response.status_code = 201
    return response