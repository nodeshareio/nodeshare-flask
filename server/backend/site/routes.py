from flask import render_template, flash, redirect, url_for, request, send_from_directory, jsonify, session
from backend import db, app, limiter, role_required
from backend.site import site
from datetime import datetime
from flask_login import current_user, login_required
from backend.models import Node, Role, User
from backend.site.forms import NodeForm

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@site.route('/')
def index():

    return render_template("index.html")


@site.route('/profile/<id>')
@login_required
def profile(id):
    user = User.query.get(1)
    return render_template('profile.html', user=user)

@site.route('/nodes/<id>', methods=['GET', 'POST'])
def node(id):
 
    node = Node.query.get(id)
    return render_template('node.html', node=node)



@site.route('/nodes', methods=['GET', 'POST'])
def nodes():
    
    page = request.args.get('page', 1, type=int)
    nodes = Node.query.filter_by(approved=True).order_by(Node.id.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('site.nodes', page=nodes.next_num) \
        if nodes.has_next else None
    prev_url = url_for('site.nodes', page=nodes.prev_num) \
        if nodes.has_prev else None
    return render_template('browse_nodes.html', title='Browse Nodes',
                           nodes=nodes.items,
                           next_url=next_url, prev_url=prev_url)

        

@site.route('/nodes/submit', methods=['GET', 'POST'])
@login_required
def submit_node():

    form = NodeForm()
    if form.validate_on_submit():
        node = Node(title = form.title.data, description = form.description.data, data = form.data.data) # TODO: sanitize!
        node.user_id = current_user.id
        db.session.add(node)
        db.session.commit()
        flash(f'{node.title} submitted!', 'success')
        return redirect(url_for('site.profile', id = current_user.id))

    return render_template('submit_node.html', form=form)