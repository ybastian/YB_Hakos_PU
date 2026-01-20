from flask import (render_template, url_for, flash,
                   redirect, request, abort, jsonify)
from werkzeug.datastructures import MultiDict
import re
from flask_login import current_user, login_required
from flask import current_app
from datetime import date, datetime
from webapp import db
from webapp.model.db import ObservationRequest, ObservationRequestPosition
from . import orders  #  Blueprint-Objekt
from .orderform import (ObservationRequestPositionsForm ,ObservationRequestHead,
                        telescope_query, filterset_query, poweruser_query)
from .constants import ORDER_STATUS_LABELS, ORDER_STATUS_CREATED, ORDER_STATUS_WAITING, ORDER_STATUS_PU_ACCEPTED, \
    ORDER_STATUS_REJECTED, USER_ROLE_ADMIN, ORDER_STATUS_APPROVED
from .orderservices import (copy_order_service, delete_order_service, calendar_service, resolve_coordinates_service,
                            init_new_order_service, init_new_orderpos_service,
                            set_user_preference_service, get_user_preference_service)

_POS_KEY_RE = re.compile(r"^(positions)-(\d+)-(.*)$")

def _normalize_positions_formdata(formdata: MultiDict) -> MultiDict:
    """
    WTForms FieldList bricht ab, sobald ein Index fehlt (z.B. 0,2 ohne 1).
    Diese Funktion nummeriert positions-* beim POST neu durch.
    """
    indices = set()

    for key in formdata.keys():
        m = _POS_KEY_RE.match(key)
        if m:
            indices.add(int(m.group(2)))

    if not indices:
        return formdata

    mapping = {old: new for new, old in enumerate(sorted(indices))}
    normalized = MultiDict()

    for key in formdata.keys():
        values = formdata.getlist(key)
        m = _POS_KEY_RE.match(key)

        if m:
            new_key = f"positions-{mapping[int(m.group(2))]}-{m.group(3)}"
        else:
            new_key = key

        for v in values:
            normalized.add(new_key, v)

    return normalized



# # ------------------------------------------------------------------
# # User preference laden
# # ------------------------------------------------------------------
@orders.route('/orders/user_preference', methods=['GET'])
@login_required
def get_user_preference():
    key = request.args.get('key')
    value = get_user_preference_service(current_user.id, key, False )
    return jsonify(success=True, value=value)
# ------------------------------------------------------------------
# User preference speichern
# ------------------------------------------------------------------
@orders.route('/orders/user_preference', methods=['POST'])
@login_required
def set_user_preference():
    data = request.get_json()
    key = data.get('key')
    value = data.get('value')
    default = data.get('default')  # falls benötigt

    status, message = set_user_preference_service(current_user.id, key, value, default)

    if status == 1:
        # Fehlerfall
        print(f"ERROR: {message}")
        return jsonify(success=False, error="Ein fehler ist aufgetreten; siehe logfile."), 500
    else:
        # Erfolg
        return jsonify(success=True)

# --------------------------------------------------------------
# Teleskope zum Observatorium
# --------------------------------------------------------------
@orders.route('/orders/get_telescopes/<int:observatory_id>')
def get_telescopes():
    data = request.get_json()
    observatory_id = data.get('observatory_id')
    telescopes = telescope_query(observatory_id)
    return jsonify([{'id': t.id, 'name': t.name} for t in telescopes])

# --------------------------------------------------------------
# Filtersets zum Teleskop
# --------------------------------------------------------------
@orders.route('/orders/get_filtersets', methods=['POST'])
@login_required
def get_filtersets():
    data = request.get_json()
    telescope_id = data.get('telescope_id')
    filtersets = filterset_query(telescope_id)
    return jsonify([{'id': f.id, 'name': f.name} for f in filtersets])

# --------------------------------------------------------------------
# Beobachtungsantrag bearbeiten
# --------------------------------------------------------------------
@orders.route('/orders', methods=['GET'])
@login_required
def edit_order():
    user_orders = ObservationRequest.query.filter_by(user_id=current_user.id).all()
    for order in user_orders: order.status_label = ORDER_STATUS_LABELS.get(order.status, "??")
    return render_template('orders.html', title='Teleskopzeit Beantragung', orders=user_orders )

# --------------------------------------------------------------------
# Beobachtungsantrag kopieren
# --------------------------------------------------------------------
@orders.route("/orders/<int:order_id>/copy_order", methods=['POST'])
@login_required
def copy_order(order_id):
    order = ObservationRequest.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    rc, message = copy_order_service(order_id)
    if  rc == 0:
        flash(message, 'success')
    else:
        flash(message,'danger')
    return redirect('/orders')

# --------------------------------------------------------------------
# Beobachtungsantrag löschen
# --------------------------------------------------------------------
@orders.route("/orders/<int:order_id>/delete_order", methods=['POST'])
@login_required
def delete_order(order_id):
    order = ObservationRequest.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    rc, message = delete_order_service(order_id)
    if  rc == 0:
        flash(message, 'success')
    else:
        flash(message,'danger')
    return redirect('/orders')

# --------------------------------------------------------------------
# Beobachtungsantrag erstellem, abschicken, sichern oder anzeigen
# --------------------------------------------------------------------
@orders.route( '/actionhandler', methods=['POST'])
@login_required
def actionhandler():
    action = request.form.get("action")
    order_id = request.form.get("order_id")
    form = ObservationRequestHead()

#   Start with new observation request
    if action == "create_order":
        order= init_new_order_service()
        form = ObservationRequestHead(obj=order)
        return render_template('create_order.html', form=form, order_id=None)

#   User submits order to get the approval
    elif action == "submit_order":
        order_head = ObservationRequest.query.get(order_id)
        if order_head.user_id != current_user.id:
            abort(403)
        order_head.status = ORDER_STATUS_WAITING
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Es ist ein Fehler aufgetreten: {e}. Bitte melden Sie sich beim Systemadministrator.', 'error')

#   Read entries from gui and save as new observation request ( no positions so far )
    elif action == "save_order":
        order_head = ObservationRequest()
        order_head.user_id = current_user.id
        order_head.request_date = form.request_date.data
        order_head.name = form.requester_name.data
        order_head.request_observatory_id = form.observatory_name.data
        order_head.request_purpose = form.request_purpose.data
        order_head.request_poweruser_id = form.poweruser_name.data
        order_head.request_type = form.request_type.data
        order_head.remark = form.remark.data
        order_head.status = ORDER_STATUS_CREATED
        db.session.add(order_head)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Es ist ein Fehler aufgetreten: {e}. Bitte melden Sie sich beim Systemadministrator.', 'error')

        return redirect(url_for('orders.edit_order_pos', order_id=order_head.id))
    return redirect('/orders')

# --------------------------------------------------------------------
# Beobachtungsantrag bearbeiten, Zeilen hinzufügen oder entfernen
# Der Kopfsatz muss schon vorhanden sein.
# Positionen werden, wenn vorhanden aus der DB geladen.
# Wenn keine Position existiert, wird eine neue mit zum Observatoruim passende
# Parametern erstellt
# --------------------------------------------------------------------
@orders.route('/orders/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_order_pos(order_id):

    app = current_app
    action = request.form.get("action")
    order_head = ObservationRequest.query.get(order_id)
    if order_head is None:
        abort(403)
    if order_head.user_id != current_user.id and not current_user.has_role(USER_ROLE_ADMIN):
        abort(403)

    expert_mode = get_user_preference_service(current_user.id, "expert_mode", "False")
    form = ObservationRequestPositionsForm()
    selected_observatory_id = order_head.request_observatory_id

    if request.method == 'GET':

        head_data = {
            'status': order_head.status,
            'status_label': ORDER_STATUS_LABELS.get(order_head.status, "??"),
            'request_date': order_head.request_date,
            'requester_name': order_head.name,
            'observatory_name': order_head.request_observatory_id,
            'request_purpose': order_head.request_purpose,
            'poweruser_name': order_head.request_poweruser_id,
            'request_type': order_head.request_type,
            'remark': order_head.remark
        }

        position_data = []
        position_items = ObservationRequestPosition.query.filter_by(observation_request_id=order_id).all()
        if len(position_items) == 0:
            position_items = init_new_orderpos_service()
            telescope_id = telescope_query(selected_observatory_id)[0].id
            position_items[0].telescope_id = telescope_id
            choices = filterset_query(telescope_id)
            position_items[0].filterset_id = filterset_query(telescope_id)[0].id

        for pos in position_items:
            position_data.append({
                'telescope': pos.telescope_id,
                'target': pos.target,
                'filterset': pos.filterset_id,
                'target_objecttype': pos.target_objecttype,
                'target_coordinates': pos.target_coordinates,
                'target_coordinates_lock': pos.target_coordinates_lock != "0",
                'exposure_count': pos.exposure_count,
                'exposure_time': pos.exposure_time,
                'exposure_starttime': pos.exposure_starttime,
                'exposure_gain': pos.exposure_gain,
                'exposure_offset': pos.exposure_offset,
                'exposure_dither': pos.exposure_dither,
                'exposure_focus': pos.exposure_focus
            })

        form.process(data={
            'order_id': order_id,
            'head': head_data,
            'positions': position_data
        })
        for pos_form in form.positions:
            selected_telescope_id = pos_form.telescope.data
            selected_filterset_id = pos_form.filterset.data
            choices = telescope_query(selected_observatory_id)
            pos_form.telescope.choices = [(x.id, x.name) for x in choices]
            choices = filterset_query(selected_telescope_id)
            if not selected_filterset_id:  # Kein Filterset ausgewählt
                pos_form.filterset.choices = [('', 'Auswählen')] + [(x.id, x.name) for x in choices]
            else:  # Es ist ein Filterset ausgewählt
                pos_form.filterset.choices = [(x.id, x.name) for x in choices]

        selected_id = str(selected_observatory_id)
        for x in form.head.observatory_name.choices:
            if x[0] == selected_id:
                name_str = x[1]  # keine weitere Auswahl ermöglichen
                form.head.observatory_name.choices = [(x[0], x[1])]
                break

        selected_poweruser_id = str(order_head.request_poweruser_id)
        form.head.poweruser_name.choices = [('', 'Auswählen oder leer lassen')] + [
            (str(x.id), x.name) for x in poweruser_query()
        ]
        if selected_poweruser_id:
            form.head.poweruser_name.data = selected_poweruser_id

        return render_template('edit_order_pos.html', expert_mode=expert_mode, form=form )

    #    Maske auslesen, alle bisherigen Positionen löschen und entsprechend der aktuellen Liste neu anlegen
    if request.method == 'POST':
        if action == "save_order":
            #  Kopfsatz Update
            order_head.request_date = form.head.request_date.data
            order_head.name = form.head.requester_name.data
            order_head.request_purpose = form.head.request_purpose.data
            order_head.request_poweruser_id = form.head.poweruser_name.data
            order_head.request_type = form.head.request_type.data
            order_head.remark = form.head.remark.data

            deleted_count = ObservationRequestPosition.query.filter_by(observation_request_id=order_id).delete()
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash(f'Es ist ein Fehler aufgetreten: {e}. Bitte melden Sie sich beim Systemadministrator.', 'error')

            with app.app_context():
                for idx, pos_form in enumerate(form.positions):
                    position_new = ObservationRequestPosition(
                       row_no = idx + 1,  # Reihenfolge im Formular = Reihenfolge in der DB
                       observation_request_id = order_id,
                       telescope_id = pos_form.telescope.data,
                       target = pos_form.target.data,
                       filterset_id = pos_form.filterset.data,
                       target_objecttype = pos_form.target_objecttype.data,
                       target_coordinates = pos_form.target_coordinates.data,
                       target_coordinates_lock = pos_form.target_coordinates_lock.data,
                       exposure_count = pos_form.exposure_count.data,
                       exposure_time = pos_form.exposure_time.data,
                       exposure_starttime=pos_form.exposure_starttime.data,
                       exposure_gain = pos_form.exposure_gain.data,
                       exposure_offset = pos_form.exposure_offset.data,
                       exposure_dither = pos_form.exposure_dither.data,
                       exposure_focus = pos_form.exposure_focus.data
                    )
                    db.session.add(position_new)

                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    flash(f'Es ist ein Fehler aufgetreten: {e}. Bitte melden Sie sich beim Systemadministrator.',
                          'error')

                flash('Deine Eingaben sind gespeichert!', 'success')
                return redirect(url_for('orders.edit_order_pos', order_id=order_head.id))

        if action == "resolve_coordinates":
              form.positions, count, resolved, ambigious = resolve_coordinates_service(form.positions)
              flash(
                        f'Von {count} Objekten wurden bei {resolved} Koordinaten zugeordnet. {ambigious} ohne Zuordnung.',
                        'success')

              for pos_form in form.positions:
                  selected_telescope_id = pos_form.telescope.data
                  selected_filterset_id = pos_form.filterset.data
                  choices = telescope_query(selected_observatory_id)
                  pos_form.telescope.choices = [(x.id, x.name) for x in choices]
                  choices = filterset_query(selected_telescope_id)
                  if not selected_filterset_id:  # Kein Filterset ausgewählt
                      pos_form.filterset.choices = [('', 'Auswählen')] + [(x.id, x.name) for x in choices]
                  else:  # Es ist ein Filterset ausgewählt
                      pos_form.filterset.choices = [(x.id, x.name) for x in choices]

                #        selected_observatory_id = order_head.request_observatory_id
              selected_id = str(selected_observatory_id)
              for x in form.head.observatory_name.choices:
                  if x[0] == selected_id:
                      name_str = x[1]  # keine weitere Auswahl ermöglichen
                      form.head.observatory_name.choices = [(selected_id, name_str)]
                      break
              return render_template('edit_order_pos.html', expert_mode=expert_mode, form=form)

        if action == "submit_order":
            order_head = ObservationRequest.query.get(order_id)
            order_head.status = ORDER_STATUS_WAITING
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash(f'Es ist ein Fehler aufgetreten: {e}. Bitte melden Sie sich beim Systemadministrator.', 'error')
    return redirect('/orders')


# --------------------------------------------------------------------
# Beobachtungsanträge für angemeldeten User auflisten
# --------------------------------------------------------------------
@orders.route('/orders', methods=['GET'])
@login_required
def show_orders():
    if request.method == 'GET':
        user_orders = ObservationRequest.query.filter_by(user_id=current_user.id).all()
        return render_template('orders.html', title='Teleskopzeit Beantragung', orders=user_orders )


# --------------------------------------------------------------------
# Beobachtungsantrag mit allen Positionen anzeigen
# --------------------------------------------------------------------
@orders.route('/orders/<int:order_id>/positions', methods=['GET'])
@login_required
def show_order_positions(order_id):
    user_order = ObservationRequest.query.get(order_id)
    user_order.status_label = ORDER_STATUS_LABELS.get(user_order.status, "??")
    positions = ObservationRequestPosition.query.filter_by(observation_request_id=order_id).all()
    return render_template('order_positions.html', order=user_order, order_position=positions)


# --------------------------------------------------------------------
# Poweruser weist sich Antrag zu
# --------------------------------------------------------------------
@orders.route('/poweruser/<int:order_id>/pu_accept', methods=['POST'])
@login_required
def pu_accept(order_id):
    order_head = ObservationRequest.query.get(order_id)
    order_head.status = ORDER_STATUS_PU_ACCEPTED
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Es ist ein Fehler aufgetreten: {e}. Bitte melden Sie sich beim Systemadministrator.', 'error')
    else:
        flash('Antrag übernommen', 'success')
    return redirect(url_for('main.poweruser'))


# --------------------------------------------------------------------
# Der Kontrolleur ( Approver ) weist Antrag zurück
# --------------------------------------------------------------------
@orders.route('/approver/<int:order_id>/reject', methods=['POST'])
@login_required
def reject_order(order_id):
    order_head = ObservationRequest.query.get(order_id)
    order_head.status = ORDER_STATUS_REJECTED
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Es ist ein Fehler aufgetreten: {e}. Bitte melden Sie sich beim Systemadministrator.', 'error')
    else:
        flash('Antrag abgelehnt', 'success')
    return redirect(url_for('main.approver'))

# --------------------------------------------------------------------
# Der Kontrolleur ( Approver ) akzeptiert Antrag
# --------------------------------------------------------------------
@orders.route('/approver/<int:order_id>/approve', methods=['POST'])
@login_required
def approve_order(order_id):
    order_head = ObservationRequest.query.get(order_id)
    order_head.status = ORDER_STATUS_APPROVED
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Es ist ein Fehler aufgetreten: {e}. Bitte melden Sie sich beim Systemadministrator.', 'error')
    else:
        flash('Antrag bestätigt', 'success')
    return redirect(url_for('main.approver'))


# --------------------------------------------------------------------
# Belegungskalender anzeigen
# --------------------------------------------------------------------
@orders.route('/orders/show_calendar', methods=['GET'])
def show_calendar():

    year = request.args.get('year', default=datetime.now().year, type=int)
    month = request.args.get('month', default=datetime.now().month, type=int)
    picker = request.args.get('picker', default=False, type=bool)
    target_id = request.args.get('target_id', default='request_date', type=str)
    display_id = request.args.get('display_id', default='selected_date_display', type=str)

    cal, planned_days, approved_days, new_moon_days, full_moon_days = calendar_service(year, month)
    today = date.today()
    referrer = request.referrer

    template = '_calendar.html' if request.headers.get('HX-Request') else 'calendar.html'

    return render_template(
        template,
                           datetime=datetime,
                           cal=cal,
                           planned_days=planned_days,
                           approved_days=approved_days,
                           full_moon_days=full_moon_days,
                           new_moon_days=new_moon_days,
                           month=month, year=year,
                           today_day=today.day,today_month=today.month,today_year=today.year,
                           referrer=referrer,
                           picker=picker,
                           target_id=target_id,
                           display_id=display_id)

