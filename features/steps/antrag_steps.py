# antrag_steps.py
# Steps for testing Antrag (ObservationRequest) creation with in-memory database.
# Scenarios must be tagged @db (see features/environment.py).

from behave import given, when, then
from webapp import db
from webapp.model.db import Site, Observatory


@given(u'the following observatories exist:')
def create_observatories_from_table(context):
    for row in context.table:
        site = Site(name=row['site'], longitude=0.0, lattitude=0.0)
        db.session.add(site)
        db.session.flush()  # assign site.id before referencing it
        observatory = Observatory(name=row['name'], site_id=site.id)
        db.session.add(observatory)
    db.session.commit()


@when(u'I login as "{email}" with password "{password}"')
def login_as(context, email, password):
    response = context.client.post('/login', data={
        'email': email,
        'password': password,
        'submit': True,
    }, follow_redirects=True)
    assert b'Abmelden' in response.data, \
        f'Login failed for {email} — "Abmelden" not found in response'


@when(u'I create the following Antraege:')
def create_antraege_from_table(context):
    import re
    obs = Observatory.query.first()
    assert obs is not None, 'No observatory found — add a "Given the following observatories exist:" step first'
    for row in context.table:
        response = context.client.post('/actionhandler', data={
            'action': 'save_order',
            'request_date': row['date'],
            'requester_name': row['requester_name'],
            'observatory_name': str(obs.id),
            'poweruser_name': '',
            'request_type': row['type'],
            'remark': row.get('remark', ''),
        }, follow_redirects=False)
        # save_order redirects to the edit page (302) on success
        assert response.status_code == 302, \
            f'Expected redirect after save_order, got {response.status_code}:\n' \
            + response.data.decode(errors='replace')[:500]
        # Capture the order ID from the redirect Location header
        location = response.headers.get('Location', '')
        m = re.search(r'/orders/(\d+)/edit', location)
        if m:
            context.last_order_id = int(m.group(1))


@then(u'the orders list contains:')
def orders_list_contains(context):
    response = context.client.get('/orders', follow_redirects=True)
    assert response.status_code == 200
    for row in context.table:
        name = row['name']
        assert name.encode() in response.data, \
            f'"{name}" not found in orders list'


@then(u'the observatory_reservation table contains:')
def observatory_reservation_contains(context):
    from webapp.model.db import ObservatoryReservation
    from datetime import date, datetime
    for row in context.table:
        expected_date = date.fromisoformat(row['date'])
        # The date column stores a date object (via date_sanitize).
        # Cast both sides to string in ISO format for a reliable SQLite comparison.
        reservation = ObservatoryReservation.query.filter(
            db.cast(ObservatoryReservation.date, db.String).like(f'{expected_date}%')
        ).first()
        assert reservation is not None, \
            f'No reservation found for date {row["date"]} in observatory_reservation table'
