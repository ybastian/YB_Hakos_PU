from flask_login import current_user
from datetime import datetime, timedelta
from webapp.model.db import Catalogue
from sqlalchemy import func
import re
from webapp import db
from .constants import ORDER_STATUS_CREATED, ORDER_STATUS_APPROVED, ORDER_STATUS_WAITING, ORDER_STATUS_PU_ACCEPTED
from webapp.model.db import UserPreferences

# --------------------------------------------------------------------------
#  Umformung von dezimal Koordinaten in die Stunden / Minuten und Winkelgrad
# --------------------------------------------------------------------------
def deg_to_hms(ra_deg):
    hours = ra_deg / 15
    h = int(hours)
    m = int((hours - h) * 60)
    s = (hours - h - m/60) * 3600
    return f"{h:02d}:{m:02d}:{s:06.3f}"

def deg_to_dms(dec_deg):
    sign = '+' if dec_deg >= 0 else '-'
    dec_deg = abs(dec_deg)
    d = int(dec_deg)
    m = int((dec_deg - d) * 60)
    s = (dec_deg - d - m/60) * 3600
    return f"{sign}{d:02d}:{m:02d}:{s:05.2f}"

# --------------------------------------------------------------------------
# Neuen Antragskopf mit Defaultwerten initialisieren
# --------------------------------------------------------------------------
def init_new_order_service():
    order = ObservationRequest()
    order.user_id = current_user.id
    try:
        order.requester_name = current_user.firstname + ' ' + current_user.surname
    except Exception as e:
        order.requester_name = f"Unknown ({order.user_id})"
    order.positions = []
    order.date_created = datetime.now()
    order.request_date = datetime.now()
    order.status = ORDER_STATUS_CREATED
    order.observatory_name = None
    order.poweruser_name = None
    order.request_poweruser_id = None
    order.request_observatory_id = None
    #order.request_purpose = ''
    return order

# --------------------------------------------------------------------------
# Neuen Antrags-Positionssarz mit Defaultwerten initialisieren
# Angenomme Defaultwerte. Könnte man auch aus Template Datensätzen holen
# --------------------------------------------------------------------------
def init_new_orderpos_service():
    pos = ObservationRequestPosition()
    pos.telescope_id = -1
    pos.filterset_id = -1
    pos.target = ''
    pos.target_objecttype = ''
    pos.target_coordinates = ''
    pos.target_coordinates_lock = '0'
    pos.exposure_count = 20
    pos.exposure_time = 300
    pos.exposure_starttime = None
    pos.exposure_gain = 10
    pos.exposure_offset = 0
    pos.exposure_dither = 1
    pos.exposure_focus = 0
    return [pos]

# --------------------------------------------------------------------------
# Kopieren eines Antrags
# --------------------------------------------------------------------------
def copy_order_service(order_id):
    orig_order = ObservationRequest.query.get_or_404(order_id)
    if orig_order:
        new_order = ObservationRequest()
        for column in ObservationRequest.__table__.columns:
            setattr(new_order, column.name, getattr(orig_order, column.name))
        new_order.user_id = current_user.id
        new_order.id = None  # neue ID beim Commit
        new_order.name += ' Copy'
        new_order.status = ORDER_STATUS_CREATED
        new_order.date_created = datetime.now()
        db.session.add(new_order)
        db.session.flush()  # jetzt ist new_order.id gesetzt

        orig_positions = (
            ObservationRequestPosition
            .query
            .filter_by(observation_request_id=order_id)
            .order_by(ObservationRequestPosition.row_no)
            .all()
        )

        if orig_positions:
            for pos in orig_positions:
                position_new = ObservationRequestPosition()
                for column in ObservationRequestPosition.__table__.columns:
                    setattr(position_new, column.name, getattr(pos, column.name))
                position_new.id = None
                position_new.observation_request_id = new_order.id
                db.session.add(position_new)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return 1, f'Es ist ein Fehler aufgetreten:\n{e}.\nBitte melden Sie sich beim Systemadministrator.'
        return 0, "Antrag \nerfolgreich\n kopiert."


# --------------------------------------------------------------------------
# Löschen eines Antrags
# --------------------------------------------------------------------------

def delete_order_service(order_id):
    order = ObservationRequest.query.get_or_404(order_id)
    db.session.delete(order)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return 1, f'Es ist ein Fehler aufgetreten:\n{e}.\nBitte melden Sie sich beim Systemadministrator.'
    return 0, "Antrag \nerfolgreich\n gelöscht."

# --------------------------------------------------------------------------
# Suche nach Objekt in Katalogen, Rückgabe des gefundenen Datensatzes
# --------------------------------------------------------------------------

def catalogue_query(sky_object):
    norm_name = re.sub(r'[\W]', '', sky_object, flags=re.UNICODE).upper()
    return (
        Catalogue.query
        .filter(
            func.replace(
                func.replace(
                    func.replace(func.upper(Catalogue.name), '-', ''),
                    ' ',
                    ''
                ),
                '.',
                ''
            ) == norm_name
        )
        .first()
    )

# ------------------------------------------------------------------------------------------------------
# Ergänzung der zu einer Liste von Objekten gehörenden Koordinaten, Rückgabe in Stunden, Minuten und so
# ------------------------------------------------------------------------------------------------------
#from astropy.coordinates import SkyCoord
#from astropy import units as u

def resolve_coordinates_service( orderpositions ):
    count = len(orderpositions)
    resolved = 0
    ambigious = 0
    for item in orderpositions:
        if not item.target_coordinates_lock.data :
            norm_object  = re.sub(r'[^\w]', '', item.target.data, flags=re.UNICODE).upper()
            coordinates = catalogue_query(norm_object)
            if coordinates:
# Mit Astropy
#                item.target_coordinates.data = SkyCoord(ra=coordinates.ra * u.degree, dec=coordinates.dec * u.degree)
                item.target_coordinates.data = deg_to_hms(coordinates.ra) + ' ' + deg_to_dms(coordinates.dec)
                resolved += 1
            else:
                ambigious += 1
                item.target_coordinates.data = '???'

    return orderpositions, count, resolved, ambigious

import calendar
from webapp.model.db import ObservationRequest, ObservationRequestPosition

# ------------------------------------------------------------------
# User preference laden  ( könnte besser ins User Modul )
# ------------------------------------------------------------------
def get_user_preference_service(user_id, key, default=None):
    if not key:
        raise ValueError("Parameter 'key' is required")
    pref = UserPreferences.query.filter_by(user_id=user_id, key=key).first()
    return pref.value if pref else default

# ------------------------------------------------------------------
# User preference speichern
# ------------------------------------------------------------------

def set_user_preference_service( user_id, key, value, default=None ):
    if not key:
        raise ValueError("Parameter 'key' is required")
    pref = UserPreferences.query.filter_by(user_id=user_id, key=key).first()
    if not pref:
        pref = UserPreferences(user_id=current_user.id, key=key)
        db.session.add(pref)
    pref.value = str(value)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return 1, f'Es ist ein Fehler aufgetreten:\n{e}.\nBitte melden Sie sich beim Systemadministrator.'
    return 0, None


# ----------------------------------------------------------------------------
#  Mondphasenberechnung
# ----------------------------------------------------------------------------

def moon_phases(year, month):
    # Referenz-Neumond: 25. Juni 2025, 12:31 UTC
    ref_new_moon = datetime(2025, 6, 25, 12, 31)
    synodic_month = 29.53059  # mittlere synodische Periode in Tagen

    # Start und Ende des Monats
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    # Suche nach Neumond und Vollmond im gewünschten Monat
    new_moon_days = set()
    full_moon_days = set()

    # Wir durchsuchen einen Zeitraum von 2 Monaten um den Zielmonat herum
    days_before = 30
    search_start = start_date - timedelta(days=days_before)
    search_end = end_date + timedelta(days=days_before)

    # Berechne die Zahl k für den nächsten Neumond nach Referenz
    k = int((search_start - ref_new_moon).days / synodic_month)
    while True:
        # Zeitpunkt des k-ten Neumonds
        new_moon = ref_new_moon + timedelta(days=k * synodic_month)
        if new_moon > search_end:
            break
        # Neumond im Zielmonat?
        if new_moon.year == year and new_moon.month == month:
            new_moon_days.add(new_moon.day)
        # Vollmond ca. 14.77 Tage nach Neumond
        full_moon = new_moon + timedelta(days=synodic_month / 2)
        if full_moon.year == year and full_moon.month == month:
            full_moon_days.add(full_moon.day)
        k += 1

    return new_moon_days, full_moon_days

# ------------------------------------------------------------------------------------------------------
# Kalender, der die gebuchten und in Planung befindlichen Tage sowohl Voll- und Neumond Tage in einem
# vorgegebenen Monat darstellt.
# ------------------------------------------------------------------------------------------------------

def calendar_service(year, month):

    orders = ObservationRequest.query.filter(
        db.extract('year', ObservationRequest.request_date) == year,
        db.extract('month', ObservationRequest.request_date) == month,
    ).all()
    approved_days = set()
    planned_days = set()
    # gebuchte Tage

    for order in orders:
        if order.status == ORDER_STATUS_APPROVED:
            approved_days.add(order.request_date.day)
        elif order.status in (ORDER_STATUS_CREATED, ORDER_STATUS_WAITING, ORDER_STATUS_PU_ACCEPTED):
            planned_days.add(order.request_date.day)
# hier einfach ausgerechnet. Besser mit astropy?
    new_moon_days, full_moon_days = moon_phases(year, month)

    cal = calendar.monthcalendar(year, month)
    return cal, planned_days, approved_days, new_moon_days, full_moon_days

