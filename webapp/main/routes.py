from datetime import datetime

from flask import render_template, request, url_for
from flask_login import login_required
from flask_login import current_user
from webapp.main import main
from webapp.model.db import db, Post, SystemParameters, ObservationRequest, PoweruserMeldung, User
from webapp.orders.constants import USER_ROLE_ADMIN, ORDER_STATUS_LABELS, ORDER_STATUS_WAITING, \
    ORDER_STATUS_PU_REJECTED, ORDER_STATUS_PU_ACCEPTED
from webapp.orders.constants import ORDER_STATUS_APPROVED, ORDER_STATUS_PU_ASSIGNED
from sqlalchemy.exc import IntegrityError
from collections import defaultdict

@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)

# -------------------------------------------------------------
#
# -------------------------------------------------------------
@main.route("/poweruser", methods=['GET','POST'])
@login_required
def poweruser():

    if request.method == "POST":
        action = request.form.get("action")
        if action != "pu_meldung":
            return '<span id="pu-feedback-0" class="text-danger ms-2">Unbekannte Aktion</span>', 400

        order_id = request.form.get("order_id", type=int)
        availability = request.form.get("availability", type=int)

        if not order_id or availability not in (1, 2, 3):
            return (
                f'<span id="pu-feedback-{order_id or 0}" class="text-danger ms-2">Ungültige Eingabe</span>',
                400,
            )

        meldung = PoweruserMeldung.query.filter_by(
            observation_request_id=order_id,
            poweruser_user_id=current_user.id
        ).first()

        if meldung is None:
            meldung = PoweruserMeldung(
                observation_request_id=order_id,
                poweruser_user_id=current_user.id,
                availability=availability
            )
            db.session.add(meldung)
        else:
            meldung.availability = availability

        db.session.commit()

        return (
            f'<span id="pu-feedback-{order_id}">'
            f'<span class="text-success ms-2">In Datenbank gespeichert</span>'
            f'</span>'
        )

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
@main.route("/approver", methods=["GET"])
@login_required
def approver():

    all_orders = (
        ObservationRequest.query
        .filter(ObservationRequest.status.in_([ORDER_STATUS_WAITING, ORDER_STATUS_APPROVED, ORDER_STATUS_PU_ASSIGNED, ORDER_STATUS_PU_REJECTED, ORDER_STATUS_PU_ACCEPTED]))
        .all()
    )
    for order in all_orders: order.status_label = ORDER_STATUS_LABELS.get(order.status, "??")
       

    order_ids = [o.id for o in all_orders]

    pu_meldungen_by_order = defaultdict(list)
    if order_ids:
        rows = (
            db.session.query(
                PoweruserMeldung.observation_request_id,
                PoweruserMeldung.poweruser_user_id,
                PoweruserMeldung.availability,
                User.name,
                User.firstname,
                User.surname,
            )
            .join(User, User.id == PoweruserMeldung.poweruser_user_id)
            .filter(PoweruserMeldung.observation_request_id.in_(order_ids))
            .all()
        )

        for r in rows:
            display_name = r.name
            if (not display_name) and (r.firstname or r.surname):
                display_name = f"{r.firstname or ''} {r.surname or ''}".strip()

            pu_meldungen_by_order[r.observation_request_id].append({
                "user_id": r.poweruser_user_id,
                "name": display_name or f"User {r.poweruser_user_id}",
                "availability": r.availability,
            })

    return render_template("approver.html", orders=all_orders, pu_meldungen_by_order=pu_meldungen_by_order)

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
