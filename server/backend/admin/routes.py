from flask import render_template, url_for, request, redirect, flash    
from backend.admin import admin
from backend import app, db, role_required
from flask_login import login_required, current_user
from backend.models import  User, Node, Role
import datetime



@admin.route('/', methods=['GET', 'POST'])
@login_required
@role_required("ADMIN")
def index():
    return render_template('admin/admin.html', title='Admin Page')


@admin.route('/deletenode/<id>', methods=['POST'])
@login_required
@role_required("ADMIN")
def delete_node(id):
    node = Node.query.get(id)
    ADMIN = Role.query.filter_by(name="ADMIN").first()
    if (ADMIN in current_user.role) or current_user.id == node.creator.id:
        title = node.title
        try:
            db.session.delete(node)
            db.session.commit()
            flash(f"Task {node} deleted.", 'success')
            return redirect(url_for('admin.index'))
        except:
            flash("Task deletion failed.", 'success')
            return redirect(url_for('admin.index'))
    return redirect(url_for('admin.index'))


@admin.route('/approve_nodes', methods=['GET', 'POST'])
@login_required
@role_required("ADMIN")
def approve_nodes():
    nodes = Node.query.filter_by(approved=False).all()
    return render_template('admin/approve_nodes.html', title='Admin Page', nodes = nodes)

@admin.route('/approve_node/<id>', methods=['POST'])
@login_required
def approve_node(id):
    # TODO: add creator to Task model - only allow delete if creator or admin
    node = Node.query.get(id)
    ADMIN = Role.query.filter_by(name="ADMIN").first()
    if (ADMIN in current_user.roles):
        node.approved = True
        try:
            db.session.commit()
            flash(f"Node {node.title} approved.", 'success')
            return redirect(url_for('admin.approve_nodes'))
        except:
            flash("Approval failed.", 'success')
            return redirect(url_for('admin.approved_nodes'))
    return redirect(url_for('admin.approved_nodes'))