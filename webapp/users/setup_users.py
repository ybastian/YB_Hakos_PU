from flask import current_app
from sqlalchemy.exc import OperationalError
from webapp import db, bcrypt
from webapp.model.db import User, Group, Role
from webapp.orders.constants import *

"""
Setup_users: Create a minimal set of users, groups, and roles, if database is empty.
             Create admin user, or overwrite admin password, if it already exists.
             Make sure admin user is in admin_group. This ensures, that application stays
             functional, even if users/groups are dropped by accident.
             
             Note: additional one-time setup is done with the init-db.py script.
"""
def setup_users():
    app=current_app
    try:
        with app.app_context():
            # create all roles and groups needed
            for choice in USER_ROLE_CHOICES:
                role_name = choice[0]
                role = Role.query.filter_by(name=role_name).first()
                if not role:
                    role = Role(name=role_name)
                    db.session.add(role)
                    db.session.commit()

                # groups are named after roles (e.g.: "admin" role and "admin_group" group)
                group_name = role_name + "_group"
                group = Group.query.filter_by(name=group_name).first()
                if not group:
                    group = Group(name=group_name)
                    db.session.add(group)
                    db.session.commit()

                # add role to group
                if role not in group.roles:
                    group.roles.append(role)
                    db.session.add(group)
                    db.session.commit()

            # setup admin user, if name and password are set
            # always reset password to configured password; password must be complex enough
            pwd_complex = len(app.config['ADMIN_USER']) > 3 \
                          and len(app.config['ADMIN_PASSWORD']) > 8 \
                          and sum(c.isupper() for c in app.config['ADMIN_PASSWORD']) > 0 \
                          and sum(c.islower() for c in app.config['ADMIN_PASSWORD']) > 0 \
                          and sum(c.isdigit() for c in app.config['ADMIN_PASSWORD']) > 0

            admin_user = User.query.filter_by(name=app.config['ADMIN_USER']).first()
            if pwd_complex:
                hashed_password = bcrypt.generate_password_hash(app.config['ADMIN_PASSWORD']).decode('utf-8')
                if admin_user:
                    admin_user.password = hashed_password
                    admin_user.email = app.config['ADMIN_EMAIL']
                    db.session.commit()
                else:
                    print(f"INFO: Create new admin user {app.config['ADMIN_USER']}")
                    admin_user = User(name=app.config['ADMIN_USER'], email=app.config['ADMIN_EMAIL'], password=hashed_password)
                    db.session.add(admin_user)
                    db.session.commit()
            else:
                print("WARNING: password is not complex enough, cannot set up admin user.")
                print("         Requirements: at least 9 characters, must contain uppercase/lowercase/digit.")
            if not admin_user:
                print("WARNING: NO ADMIN USER DEFINED")


            # assign admin_group to admin user
            if admin_user:
                admin_group = Group.query.filter_by(name=USER_ROLE_ADMIN + "_group").first()
                if admin_group not in admin_user.groups:
                    admin_user.groups.append(admin_group)
                    db.session.add(admin_user)
                    db.session.commit()

    except OperationalError:
        print("WARNING: Database not initialized")
