from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField, SelectField, BooleanField
from wtforms.fields.datetime import DateField, TimeField
from wtforms.fields.simple import HiddenField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, NumberRange, ValidationError
from datetime import date
from .constants import REQUEST_CHOICES

from webapp.model.db import  Telescope, Filterset, Observatory, \
    ObjectTypes, MotivationTypes, User
from .constants import PU_AKTIV


def telescope_query(observatory_id):
    if observatory_id is None:
        return []
    return (
        Telescope.query
        .filter_by(observatory_id=observatory_id)
        .order_by(Telescope.name)
        .all()
    )

def observatory_query():  # Im Kopfsatz
    return(
        Observatory.query
        .order_by(Observatory.name)
        .all()
    )

def poweruser_query():  # Im Kopfsatz
    return User.by_role('poweruser')



def objecttype_query():
    return (
        ObjectTypes.query
        .order_by(ObjectTypes.Objecttype)
        .all()
    )

def motivation_query():
    return MotivationTypes.query.order_by(MotivationTypes.Motivation).all()

def filterset_query(telescope_id):
    if telescope_id == 4:
        x= 8
    return (
        Filterset.query
        .filter( Filterset.telescope_id == telescope_id)
        .order_by(Filterset.name)
        .all()
    )


def date_in_future(form, field):
    if field.data is not None and field.data <= date.today():
        raise ValidationError('Das Datum muss in der Zukunft liegen.')

# Kopfsatz eines Antrags
class ObservationRequestHead(FlaskForm):
    class Meta:
        csrf = False

    status_label = HiddenField()
    request_date = DateField('Datum', format='%Y-%m-%d', validators=[DataRequired() ])
    requester_name = StringField('Beteiligte', validators=[DataRequired()])
    observatory_name = SelectField('Observatorium', choices=[], validators=[DataRequired()])
    #request_purpose = SelectField('Motivation', choices=[])
    poweruser_name = SelectField('Wunsch Poweruser', choices=[])
    request_type = SelectField('Type', choices=REQUEST_CHOICES)
    remark = TextAreaField('Anmerkungen')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.request_purpose.choices = [('', 'Auswählen oder leer lassen')] + [
        #    (x.Motivation, x.Motivation) for x in motivation_query()
        #]
        self.observatory_name.choices = [('', 'Auswählen')] + [
            (str(x.id), x.name) for x in observatory_query()
        ]
        self.poweruser_name.choices = [('', 'Auswählen oder leer lassen')] + [
            (str(x.id), x.name) for x in poweruser_query()
        ]


# Positionen des Antrags
class ObservationRequestPositionForm(FlaskForm):
    class Meta:
        csrf = False
    telescope = SelectField('Teleskop', choices=[],  coerce=int, validators=[DataRequired()])
    filterset = SelectField('Filterset', choices=[], coerce=int, validators=[DataRequired()])
    target = StringField('Objekt-Name', validators=[DataRequired()])
    target_objecttype = SelectField('Objekttyp', choices=[], validators=[DataRequired()])
    target_coordinates = StringField('Target_coordinates')
    target_coordinates_lock = BooleanField('target_coordinates_lock')
    exposure_starttime = TimeField('exposure_starttime', format='%H:%M')
    exposure_count  = IntegerField('Menge', validators=[InputRequired(), NumberRange(min=1)])
    exposure_time   = IntegerField('exposure_time', validators=[InputRequired(), NumberRange(min=1)])
    mosaic = BooleanField('Mosaik')
    exposure_gain   = IntegerField('exposure_gain', validators=[InputRequired(), NumberRange(min=0)])
    exposure_offset = IntegerField('exposure_offset', validators=[InputRequired(), NumberRange(min=0)])
    exposure_focus  = IntegerField('exposure_focus', validators=[InputRequired(), NumberRange(min=0)])
    exposure_dither = IntegerField('exposure_dither', validators=[InputRequired(), NumberRange(min=0)])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_objecttype.choices = [('-1', 'Auswählen oder leerlassen')] + [
            (x.Objecttype, x.Objecttype) for x in objecttype_query()
        ]
        self.filterset.choices = [('-2', 'Auswählen')] + [
            (x.name, x.name) for x in filterset_query(-1)
        ]


# Kopf und Positionen
class ObservationRequestPositionsForm(FlaskForm):
    order_id = HiddenField()
    head = FormField(ObservationRequestHead)
    positions = FieldList(FormField(ObservationRequestPositionForm), min_entries=0)
    submit = SubmitField('Speichern')

