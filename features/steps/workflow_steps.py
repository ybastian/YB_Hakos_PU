# workflow_steps.py
# Steps for the full workflow test: create → submit → approve → poweruser meldung.
# Scenarios must be tagged @db (see features/environment.py).

from behave import when, then
from webapp import db


@when(u'I submit the last created Antrag')
def submit_last_antrag(context):
    assert hasattr(context, 'last_order_id'), \
        'No last_order_id on context — run "I create the following Antraege:" first'
    response = context.client.post('/actionhandler', data={
        'action': 'submit_order',
        'order_id': str(context.last_order_id),
    }, follow_redirects=False)
    # submit_order redirects to /orders on success
    assert response.status_code == 302, \
        f'Expected redirect after submit_order, got {response.status_code}:\n' \
        + response.data.decode(errors='replace')[:500]


@when(u'I logout')
def logout(context):
    context.client.get('/logout', follow_redirects=True)


@then(u'the approver page shows the Antrag as "{section}"')
def approver_page_shows_antrag(context, section):
    response = context.client.get('/approver', follow_redirects=True)
    assert response.status_code == 200, \
        f'GET /approver returned {response.status_code}'
    assert section.encode() in response.data, \
        f'"{section}" not found on approver page'
    # Also verify the requester name is visible
    assert b'Joe Tester' in response.data, \
        '"Joe Tester" not found on approver page'


@when(u'the approver approves the last Antrag')
def approver_approves(context):
    assert hasattr(context, 'last_order_id'), \
        'No last_order_id on context'
    response = context.client.post(
        f'/approver/{context.last_order_id}/approve',
        follow_redirects=False,
    )
    assert response.status_code == 302, \
        f'Expected redirect after approve, got {response.status_code}:\n' \
        + response.data.decode(errors='replace')[:500]


@then(u'the poweruser page shows the Antrag')
def poweruser_page_shows_antrag(context):
    response = context.client.get('/poweruser', follow_redirects=True)
    assert response.status_code == 200, \
        f'GET /poweruser returned {response.status_code}'
    assert b'Joe Tester' in response.data, \
        '"Joe Tester" not found on poweruser page'


@when(u'the poweruser saves availability "{label}" for the last Antrag')
def poweruser_saves_availability(context, label):
    label_to_int = {
        'möglich': 1,
        'vielleicht': 2,
        'nicht möglich': 3,
    }
    availability = label_to_int.get(label.lower())
    assert availability is not None, \
        f'Unknown availability label "{label}" — use möglich / vielleicht / nicht möglich'
    assert hasattr(context, 'last_order_id'), \
        'No last_order_id on context'
    response = context.client.post('/poweruser', data={
        'action': 'pu_meldung',
        'order_id': str(context.last_order_id),
        'availability': str(availability),
    }, follow_redirects=False)
    assert response.status_code == 200, \
        f'Expected 200 after pu_meldung, got {response.status_code}:\n' \
        + response.data.decode(errors='replace')[:500]


@then(u'the PoweruserMeldung for the last Antrag has availability {expected_availability:d}')
def poweruser_meldung_has_availability(context, expected_availability):
    from webapp.model.db import PoweruserMeldung
    assert hasattr(context, 'last_order_id'), \
        'No last_order_id on context'
    meldung = PoweruserMeldung.query.filter_by(
        observation_request_id=context.last_order_id,
    ).first()
    assert meldung is not None, \
        f'No PoweruserMeldung found for order_id={context.last_order_id}'
    assert meldung.availability == expected_availability, \
        f'Expected availability={expected_availability}, got {meldung.availability}'
