import json
from flask import render_template, Response, request, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy import select
from webapp.inout import bp
from webapp import db
from webapp.model.db import User, UserPreferences, Group, Role, Post, Site, Observatory, Telescope, Filterset, Poweruser, ObservationRequest, ObservationRequestPosition, ObservationHistory, SystemParameters, SystemParametersHistory, MotivationTypes, ObjectTypes, ObservationRequestLog, CatalogueMeta, Catalogue, user_group, role_group
from datetime import datetime, date, time
from webapp.users.utils import role_required

@bp.route('/inout/export', methods=['POST'])
@role_required('admin')
def export_data():
    data = {}

    models = [User, UserPreferences, Group, Role, Post, Site, Observatory, Telescope,
              Filterset, Poweruser, ObservationRequest, ObservationRequestPosition,
              ObservationHistory, SystemParameters, SystemParametersHistory, MotivationTypes,
              ObjectTypes, ObservationRequestLog, CatalogueMeta, Catalogue]

    for model in models:
        table_name = model.__tablename__
        records = model.query.all()
        data[table_name] = [record_to_dict(record) for record in records]

    # Also export the association tables
    data['user_group'] = [{'user_id': row[0], 'group_id': row[1]} for row in db.session.query(user_group).all()]
    data['role_group'] = [{'role_id': row[0], 'group_id': row[1]} for row in db.session.query(role_group).all()]

    json_data = json.dumps(data, indent=4, default=str)

    return Response(
        json_data,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment;filename=database_export.json'}
    )

@bp.route('/inout/import', methods=['POST'])
@role_required('admin')
def import_data():
    """
        Import data into database, which has been exported from same version.
        This works in two cases only:
            Case 1: some record has been deleted and needs to be restored. Note, that this will only work if
            no additional data has been added in the meantime.
            Case 2: the backend database has been replaced and data needs to be imported in the new database.
    """
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('admin.index'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('admin.index'))
    if file:
        data = json.load(file)
        
        models = {
            'user': User, 'user_preferences': UserPreferences, 'group': Group, 'role': Role, 'post': Post, 'site': Site,
            'observatory': Observatory, 'telescope': Telescope, 'filterset': Filterset, 'poweruser': Poweruser,
            'observation_request': ObservationRequest, 'observation_request_position': ObservationRequestPosition,
            'ObservationHistory': ObservationHistory, 'system_parameters': SystemParameters,
            'system_parameters_history': SystemParametersHistory, 'motivation_types': MotivationTypes,
            'object_types': ObjectTypes, 'observation_request_log': ObservationRequestLog, 'catalogue_meta': CatalogueMeta,
            'catalogue': Catalogue
        }
        
        ordered_tables = [
            'role', 'group', 'user', 'user_preferences', 'post', 'site', 'observatory', 'telescope', 'filterset',
            'poweruser', 'observation_request', 'observation_request_position', 'ObservationHistory',
            'system_parameters', 'system_parameters_history', 'motivation_types', 'object_types',
            'observation_request_log', 'catalogue_meta', 'catalogue'
        ]

        for table_name in ordered_tables:
            if table_name in data and table_name in models:
                print(f'Importing {table_name}')
                model = models[table_name]
                for record in data[table_name]:
                    # Convert string dates back to datetime objects
                    for c in model.__table__.columns:
                        col_name = c.name
                        if col_name in record and isinstance(record[col_name], str):
                            if isinstance(c.type, db.DateTime):
                                try:
                                    record[col_name] = datetime.fromisoformat(record[col_name])
                                except (ValueError, TypeError):
                                    flash(f"Warning: Could not parse datetime string '{record[col_name]}' for {table_name}.{col_name}. Setting to None.", "warning")
                                    record[col_name] = None
                            elif isinstance(c.type, db.Time):
                                try:
                                    record[col_name] = time.fromisoformat(record[col_name])
                                except (ValueError, TypeError):
                                    flash(f"Warning: Could not parse time string '{record[col_name]}' for {table_name}.{col_name}. Setting to None.", "warning")
                                    record[col_name] = None
                            elif isinstance(c.type, db.Date):
                                try:
                                    record[col_name] = date.fromisoformat(record[col_name])
                                except (ValueError, TypeError):
                                    flash(f"Warning: Could not parse date string '{record[col_name]}' for {table_name}.{col_name}. Setting to None.", "warning")
                                    record[col_name] = None

                    pk_name = model.__mapper__.primary_key[0].name
                    pk_value = record.get(pk_name)
                    if pk_value is not None:
                        exists = db.session.get(model, pk_value)
                        if not exists:
                            # make sure, the password field is set to empty string, if missing in imported record.
                            if table_name == 'user' and 'password' not in record:
                                record['password'] = ''

                            # skip columns in input which do not exist
                            valid_columns = [c.name for c in model.__table__.columns]
                            filtered_record = {k: v for k, v in record.items() if k in valid_columns}
                            
                            instance = model(**filtered_record)
                            db.session.add(instance)
                    else:
                        print(f'primary key {pk_name} is None - skipping')
            else:
                print(f'Skipping {table_name} (unknown table)')

        
        db.session.commit()

        # Now handle the association tables: only import, if mapping does not already exist.
        if 'user_group' in data:
            for record in data['user_group']:
                user_id = record.get('user_id')
                group_id = record.get('group_id')
                stmt = select(user_group).where(user_group.c.user_id == user_id).where(user_group.c.group_id == group_id)
                exists = db.session.execute(stmt).first()
                if not exists:
                    db.session.execute(user_group.insert().values(**record))
        
        if 'role_group' in data:
            for record in data['role_group']:
                role_id = record.get('role_id')
                group_id = record.get('group_id')
                stmt = select(role_group).where(role_group.c.role_id == role_id).where(role_group.c.group_id == group_id)
                exists = db.session.execute(stmt).first()
                if not exists:
                    db.session.execute(role_group.insert().values(**record))

        db.session.commit()
        flash('Data imported successfully. Existing records were ignored.')
    return redirect(url_for('admin.index'))

def record_to_dict(record):
    return {c.name: getattr(record, c.name) for c in record.__table__.columns}