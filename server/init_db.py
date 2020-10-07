#!/usr/bin/env python
"""Create a initial admin user"""
from getpass import getpass
from backend import db, app
from backend.models import User, UserRoles, Role
import sys


def create_admin_role():
    print("Creating Admin Role")
    try:
        admin = Role(name="ADMIN")
        db.session.add(admin)
        db.session.commit()
        print(f"Admin Role Created")
        return True
    
    except:
        print("Failure: Roles not created.")
        return False


def main():
    with app.app_context():
        db.metadata.create_all(db.engine)
        
        try:    
            create_admin_role()
        except:
            print("admin role exists... moving on")
        if User.query.all():
            create = input('A user already exists! Create another? (y/n):')
            if create == 'n':
                return
        username = input("Enter Display Name:")
        email = input("Enter email address (for login):")
        password = getpass()
        assert password == getpass('Password (again):')
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        admin_role = Role.query.filter_by(name="ADMIN").first().id
        new_role = UserRoles(user_id=user.id, role_id=admin_role)
        db.session.add(new_role)
        db.session.commit()
        print("Admin user Created")
    

if __name__ == '__main__':
    sys.exit(main())
