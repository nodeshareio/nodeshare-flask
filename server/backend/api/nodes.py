from flask import jsonify, request, url_for
from backend.models import Node
from backend.api import api
from backend.api.errors import bad_request
from backend import app, db, mqtt
from backend.api.auth import token_auth
import json
from werkzeug.http import HTTP_STATUS_CODES
import os 
from werkzeug.utils import secure_filename
import re

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_node_id_from_preview_filename(filename): 
    print(f"Retreiving Node ID from {filename}")
    return int(re.findall(r'[0-9]+', filename)[0])

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
    data = json.loads(request.data) or json.loads('{"error": "no data"}')
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
        template = '{{"node_id": "{node_id}", "node_text": "{node_text}" }}'
        payload = template.format(node_id = node.id, node_text=node.data)
        mqtt.publish('nodeshare/submit', payload) #json string
    except:
        print("[  INFO  ] DB Commit Failure: Node not submitted")
    res_msg = {'success':'node submitted'}
    response = jsonify(res_msg)   
    response.status_code = 201
    return response

@api.route('/approve', methods=['POST'])
@token_auth.login_required
def approve_node():
    
    data = json.loads(request.data) or json.loads('{"error": "no data"}')
    print(f"approved  data: {data}")
    if 'ns_string' not in data:
        return bad_request('Node Text Required!')
    if 'node_id' not in data:
        return bad_request('ID Required!')
    print("[  INFO  ]  Node Approved")  
    print(f"[  APPROVED NODE TEXT  ]  {data['ns_string']}")  
    node = Node.query.get(int(data['node_id']))
    node.approved = True
    try:
        db.session.commit()
    except:
        print("[  INFO  ] DB Commit Failure: Node not submitted")
    response = jsonify(data)
    response.status_code = 201
    return response 

@api.route("/preview/<filename>", methods=["POST"])
@token_auth.login_required
def upload_preview(filename):
    """Upload a file."""
    status_code = 201 #wishful thinking
    
    if "/" in filename:
        data = {'error':'no subdirectories allowed'}
        response = jsonify(data)
        status_code = 400
        return response
    print(request.files)
    data = request.files or json.loads('{"error": "no data"}')

    if 'error'  in data:
        response = jsonify(data)
        response.status_code = 400
        return response

    try:
        if 'preview' not in request.files:
            data = {'error':'no preview data'}
            response = jsonify(data)
            response.status_code = 400
            return response
        print("trying to upload preview")
        file = request.files['preview']
        filename = file.filename
        print(request.files['preview'].filename)
        if filename == '':
            data = {'error':'no selected file'}
            response = jsonify(data)
            status_code = 400
        print(f"Allowed?: {allowed_file(filename)}")
        if file and allowed_file(filename):
            filename = secure_filename(filename)
            print(f"Saving File: {filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            data = {'success': 'approved'}
            id = get_node_id_from_preview_filename(filename)
            node = Node.query.get(id)
            node.sample_path = filename
            db.session.commit()
        response = jsonify(data)
        # Return 201 CREATED
        response.status_code = status_code
        return response

    except:
        data = {'error':'preview not uploaded'}
        response = jsonify(data)
        response.status_code = 400
        return response 





