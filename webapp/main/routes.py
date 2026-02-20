from datetime import datetime

from flask import render_template, request, url_for
from flask_login import login_required
from flask_login import current_user
from webapp.main import main
from webapp.model.db import Post, SystemParameters, ObservationRequest
from webapp.orders.constants import USER_ROLE_ADMIN, ORDER_STATUS_LABELS, ORDER_STATUS_WAITING, \
    ORDER_STATUS_PU_REJECTED, ORDER_STATUS_PU_ACCEPTED
from webapp.orders.constants import ORDER_STATUS_APPROVED, ORDER_STATUS_PU_ASSIGNED
from webapp.model.db import User

@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    guest_users = User.by_role("GuestRole")
    guest_count = len(guest_users)
    return render_template('home.html', guest_users=guest_users, guest_count=guest_count, posts=posts)

# -------------------------------------------------------------
#
# -------------------------------------------------------------
@main.route("/poweruser", methods=['GET'])
@login_required
def poweruser():

    all_orders = (
        ObservationRequest.query
        .filter(ObservationRequest.status.in_([ORDER_STATUS_APPROVED, ORDER_STATUS_PU_ASSIGNED]))
        .all()
    )
    for order in all_orders: order.status_label = ORDER_STATUS_LABELS.get(order.status, "??")
    return render_template('poweruser.html', title='Poweruser', orders=all_orders)

# -------------------------------------------------------------
#
# -------------------------------------------------------------
@main.route("/approver", methods=['GET'])
@login_required
def approver():

    all_orders = (
        ObservationRequest.query
        .filter(ObservationRequest.status.in_([ORDER_STATUS_WAITING, ORDER_STATUS_PU_ASSIGNED, ORDER_STATUS_PU_REJECTED, ORDER_STATUS_PU_ACCEPTED]))
        .all()
    )
    for order in all_orders: order.status_label = ORDER_STATUS_LABELS.get(order.status, "??")
    return render_template('approver.html', title='Approver', orders=all_orders)

# -------------------------------------------------------------
#
# -------------------------------------------------------------
@main.route("/faq")
def faq():
    vds_link = SystemParameters.query.filter_by(parameter='vds_link').first()
    if vds_link:
        vds_link = vds_link.value
    else:
        vds_link = "#"
    return render_template('faq.html', title='FAQ', vds_link=vds_link)

@main.route("/status")
def status():
    from flask import session
    print(session)
    print(f"{current_user.name=}")
    print(f"Admin User? {current_user.has_role(USER_ROLE_ADMIN)}")
    print( "Du bist" + f" current_user.groups")
    return home()

@main.route("/fgrequest")
@login_required
def fgrequest():
    return render_template('create_obs_request.html', title='FG Request')

@main.route("/servicerequest")
@login_required
def servicerequest():
    return render_template('create_service.html', title='Service Request')

@main.route("/request_georg")
@login_required
def request_georg():
    return render_template('create_request_georg.html', title='Request Georg')

@main.route("/add-row")
def add_row():
    return render_template("aufnahme_zeile.html")

@main.route("/gast")
@login_required
def gast():    
    guest_users = User.by_role("GuestRole") or []
    guest_count = len(guest_users)
    return render_template("gast.html", title="Neuregistrierungen", guest_users=guest_users, guest_count=guest_count)