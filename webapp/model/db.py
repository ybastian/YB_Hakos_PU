from datetime import datetime, timezone
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flask import current_app
from webapp import login_manager, db
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint, CheckConstraint, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

"""
    A user is an individual. Do not share users.
"""
class User(db.Model, UserMixin):
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(60), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    image_file: Mapped[str] = mapped_column(db.String(60), nullable=False, default='default.jpg')
    password: Mapped[str] = mapped_column(db.String(60), nullable=False)
    surname: Mapped[str] = mapped_column(db.String(40), nullable=True)
    firstname: Mapped[str] = mapped_column(db.String(40), nullable=True)
    vds_number: Mapped[int] = mapped_column(db.Integer, nullable=True)
    last_login: Mapped[datetime] = mapped_column(db.DateTime, nullable=True, default=datetime.now(timezone.utc))
    posts = db.relationship('Post', backref='author', lazy=True)
    groups = db.relationship('Group', secondary='user_group', back_populates='users')
    preferences = db.relationship('UserPreferences', backref='user', cascade="all, delete-orphan")

    def has_role(self, name):
        for group in self.groups:
            if group.has_role(name):
                return True
        return False

    def get_reset_token(self):
        s = Serializer(secret_key=current_app.config['SECRET_KEY'])
        token = s.dumps({'user_id': self.id})
        return token

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(secret_key=current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except BadSignature | SignatureExpired:
            return None
        return User.query.get(user_id)

    @staticmethod
    def by_role(role_name):
        return db.session.query(User).join(User.groups).join(Group.roles).filter(Role.name == role_name).all()

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.image_file}')"

    def __str__(self):
       return f"{self.name}"

    def __init__(
        self,
        name: str,
        email: str,
        password: str,
        firstname: str = None,
        surname: str = None,
        vds_number: int = None,
        image_file: str = 'default.jpg',
        last_login: datetime = None
    ):
        self.name = name
        self.email = email
        self.password = password
        self.firstname = firstname
        self.surname = surname
        self.vds_number = vds_number
        self.image_file = image_file
        self.last_login = last_login if last_login is not None else datetime.now(timezone.utc)


class UserPreferences(db.Model):
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    key = db.Column(db.String(100))
    value = db.Column(db.String(100))


"""
    A group is a collection of akin people. At the same time, the group is a collection of
     permissions or "roles" the group can perform. When the people in the group are not "equal",
     it is better to create more groups.
"""
class Group(db.Model):
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(30), unique=True, nullable=False)
    users = db.relationship('User', secondary='user_group', back_populates='groups')
    roles = db.relationship('Role', secondary='role_group', back_populates='groups')

    def has_role(self, name):
        role = Role.query.filter_by(name=name).first()
        if role:
            return role in self.roles
        else:
            print("ERROR: No such role '{}'".format(name))
            return False

    def __repr__(self):
       return f"Group('{self.name}')"

    def __str__(self):
       return f"{self.name}"


user_group = db.Table(
    'user_group',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)

"""
    A role should be defined precisely. If needed, a group can have multiple roles. Ideally, each role would
    only be checked for in one place of the code. Roles should be grouped together in a group to make assignments
    easier.
"""
class Role(db.Model):
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(30), unique=True, nullable=False)
    groups = db.relationship('Group', secondary='role_group', back_populates='roles')

    def __repr__(self):
        return f"Role('{self.name}')"

    def __str__(self):
        return f"{self.name}"

role_group = db.Table(
    'role_group',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)


class Post(db.Model):
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(db.String(100), nullable=False)
    date_posted: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    content: Mapped[str] = mapped_column(db.Text, nullable=False)
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

    def __str__(self):
       return f"{self.title}"

"""
    A site is a place with one or more observatories
"""
class Site(db.Model):
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False)
    longitude: Mapped[float] = mapped_column(db.Float)
    lattitude: Mapped[float] = mapped_column(db.Float)
    observatories = db.relationship('Observatory', back_populates='site')

    def __repr__(self):
        return f"Site('{self.name}', l={self.longitude}, b={self.lattitude})"

    def __str__(self):
        return f"{self.name}"

"""
    An observatory is a place with a mount but potentially multiple telescopes on the mount
"""
class Observatory(db.Model):
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(30), unique=True, nullable=False)
    site_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('site.id'), nullable=False)
    # telescopes = db.relationship('Telescope', back_populates='observatory', lazy='joined')
    telescopes: Mapped[List["Telescope"]] = relationship(
    'Telescope',
    back_populates='observatory',
    lazy='joined'
    )
    site = db.relationship('Site', back_populates='observatories', lazy='joined')

    def __repr__(self):
        return f"Observatory('{self.name}')"

    def __str__(self):
        return f"{self.name}"

"""
    A telescope is an Optical Tube Assembly consisting of telescope and camera
"""
# class Telescope(db.Model):
#     id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
#     name: Mapped[str] = mapped_column(db.String(30), unique=True, nullable=False)
#     observatory_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('observatory.id'), nullable=False)
#     aperature_mm: Mapped[float] = mapped_column(db.Float, nullable=False)
#     focal_length_mm: Mapped[float] = mapped_column(db.Float, nullable=False)
#     camera_name: Mapped[str] = mapped_column(db.String(30), nullable=False)
#     status: Mapped[str] = mapped_column(db.String(2), nullable=False, default="0")
#     __table_args__ = (
#         UniqueConstraint('id', 'observatory_id', name='uq_id_observatory'),  # Unique über zwei Spalten
#         {'sqlite_autoincrement': True}
#     )
#     observatory = db.relationship('Observatory', back_populates='telescopes', lazy='joined')
#     filtersets = db.relationship('Filterset',
#                                  back_populates='telescope',
#                                  cascade = 'all, delete-orphan',
#                                  lazy = 'joined')
class Telescope(db.Model):
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(30), unique=True, nullable=False)
    observatory_id: Mapped[Optional[int]] = mapped_column(
        db.Integer,
        db.ForeignKey('observatory.id'),
        nullable=True
    )
    aperature_mm: Mapped[float] = mapped_column(db.Float, nullable=False)
    focal_length_mm: Mapped[float] = mapped_column(db.Float, nullable=False)
    camera_name: Mapped[str] = mapped_column(db.String(30), nullable=False)
    status: Mapped[str] = mapped_column(db.String(2), nullable=False, default="0")
    observatory: Mapped[Optional["Observatory"]] = relationship(
        'Observatory',
        back_populates='telescopes',
        lazy='joined'
    )
    filtersets: Mapped[List["Filterset"]] = relationship(
        'Filterset',
        back_populates='telescope',
        cascade='all, delete-orphan',
        lazy='joined'
    )
    def __repr__(self):
       return f"Telescope('{self.name}')"

    def __str__(self):
       return f"{self.name}"


# class Filterset(db.Model):
#     id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
#     name: Mapped[str] = mapped_column(db.String(50), unique=False, nullable=False)
#     telescope_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('telescope.id'), nullable=False)
#     quantity: Mapped[int] = mapped_column(db.Integer, nullable=False, default=1)
#     __table_args__ = (
#         UniqueConstraint('id', 'telescope_id', name='uq_id_telescope'),  # Unique über zwei Spalten
#         CheckConstraint('quantity >= 1', name='check_quantity_min'),
#         {'sqlite_autoincrement': True}
#     )
#     telescope: Mapped[List["Telescope"]] = relationship(
#         "Telescope",
#         back_populates="filtersets",
#         lazy='joined'
#     )

class Filterset(db.Model):
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    telescope_id: Mapped[Optional[int]] = mapped_column(
        db.Integer,
        db.ForeignKey('telescope.id'),
        nullable=True
    )
    quantity: Mapped[int] = mapped_column(db.Integer, nullable=False, default=1)
    telescope: Mapped[Optional["Telescope"]] = relationship(
        "Telescope",
        back_populates="filtersets",
        lazy='joined'
    )
    def __repr__(self):
       return f"Filterset('{self.name}')"

    def __str__(self):
       return f"{self.name}"


## -----------------------
#  Poweruser
## -----------------------

class Poweruser(db.Model, UserMixin):
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    mobilfone: Mapped[str] = mapped_column(db.String(20), nullable=False)
    fone: Mapped[str] = mapped_column(db.String(20), nullable=True)
    Einweisung: Mapped[str] = mapped_column(db.String(30), nullable=True)
    Status: Mapped[str] = mapped_column(db.String(20), nullable=True)
    last_login: Mapped[datetime] = mapped_column(db.DateTime, nullable=True, default=datetime.now(timezone.utc))

    def __str__(self):
       return f"{self.name}"

"""
    An ObservationsRequest is a proposed observation for one or more telescopes
    It is in one of the following states:
        - draft: not yet requested
        - waiting: waiting to be rejected or approved
        - rejected: an rejected proposal can become draft again or simply deleted
        - approved: waiting to be performed
        - documentation needed: the propose was performed and needs to be documented
        - finished: once the observation is documented it is finished
"""


# ---------------------------------------------------------------
# ObservationRequest Kopfsatz
# ---------------------------------------------------------------
class ObservationRequest(db.Model):
    __tablename__ = 'observation_request'
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    request_date: Mapped[datetime] = mapped_column(db.DateTime, nullable=False)
    request_observatory_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('observatory.id'), nullable=False)
    request_type: Mapped[str] = mapped_column(db.String(10), unique=False, nullable=False)  # Beobachtung, Führung, Wartung ...
    #request_purpose: Mapped[str] = mapped_column(db.String(100), unique=False, nullable=False)  # Pritty pictures, Wissenschaft, Forschung ..
    request_poweruser_id: Mapped[str] = mapped_column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    remark: Mapped[str] = mapped_column(db.String(2000), nullable=True)
    status: Mapped[str] = mapped_column(db.String(10), nullable=False, default='0')
    positions = relationship(
        'ObservationRequestPosition',
        backref='observationrequest',
        cascade="all, delete-orphan",
        lazy='joined'
    )
    observatory_name = relationship('Observatory', backref='observation_request')

# ---------------------------------------------------------------
#  observationRequestPosition zum Kopfsatz gehörende Positionen
# ---------------------------------------------------------------
class ObservationRequestPosition(db.Model):
    __tablename__ = 'observation_request_position'
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    observation_request_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('observation_request.id'), nullable=False)
    row_no: Mapped[int] = mapped_column(db.Integer, nullable=False)
    telescope_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('telescope.id'), nullable=False)
    filterset_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('filterset.id'), nullable=True)
    target_objecttype: Mapped[str] = mapped_column(db.String(200), unique=False, nullable=True)
    target: Mapped[str] = mapped_column(db.String(200), unique=False, nullable=True)
    target_coordinates: Mapped[str] = mapped_column(db.String(200), unique=False, nullable=True)
    target_coordinates_lock: Mapped[str] = mapped_column(db.String(1), unique=False, nullable=True, default='0')
    exposure_count: Mapped[int] = mapped_column(db.Integer, unique=False, nullable=True)
    exposure_time: Mapped[int] = mapped_column(db.Integer, unique=False, nullable=True)
    mosaic: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=False)
    exposure_gain: Mapped[int] = mapped_column(db.Integer, unique=False, nullable=True, default='0')
    exposure_offset: Mapped[int] = mapped_column(db.Integer, unique=False, nullable=True, default='0')
    exposure_dither: Mapped[int] = mapped_column(db.Integer, unique=False, nullable=True, default='1')
    exposure_focus: Mapped[int] = mapped_column(db.Integer, unique=False, nullable=True, default='1')
    exposure_starttime = mapped_column(Time, nullable=True)

    # --- Koordinaten-Spalten (existieren in SQLite) ---
    ra_h: Mapped[Optional[int]] = mapped_column(db.Integer, nullable=True)
    ra_m: Mapped[Optional[int]] = mapped_column(db.Integer, nullable=True)
    ra_s: Mapped[Optional[float]] = mapped_column(db.Float, nullable=True)

    dec_sign: Mapped[Optional[str]] = mapped_column(db.String(1), nullable=True)
    dec_d: Mapped[Optional[int]] = mapped_column(db.Integer, nullable=True)
    dec_m: Mapped[Optional[int]] = mapped_column(db.Integer, nullable=True)
    dec_s: Mapped[Optional[float]] = mapped_column(db.Float, nullable=True)

    # --- Block + Zeile im Block (existieren in SQLite) ---
    block_no: Mapped[int] = mapped_column(db.Integer, nullable=False, default=1)
    row_in_block: Mapped[int] = mapped_column(db.Integer, nullable=False, default=1)

    telescope = relationship('Telescope', backref='observation_request_position')
    filterset = relationship('Filterset', backref='observation_request_position')


# Aus Altdaten extrahiert
class ObservationHistory(db.Model):
    __tablename__ = 'ObservationHistory'
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Datum: Mapped[str] = mapped_column(db.String(25), nullable=False)
    Objekt: Mapped[str] = mapped_column(db.String(80), unique=False, nullable=True)
    Rubrik: Mapped[str] = mapped_column(db.String(160), unique=False, nullable=True)
    Teleskop: Mapped[str] = mapped_column(db.String(100), unique=False, nullable=True)
    EinzelbelichtungSekunden: Mapped[str] = mapped_column(db.String(60), unique=False, nullable=True)
    Bildanzahl: Mapped[str] = mapped_column(db.String(5), unique=False, nullable=True)
    Filter: Mapped[str] = mapped_column(db.String(60), unique=False, nullable=True)
    Bildersteller: Mapped[str] = mapped_column(db.String(80), unique=False, nullable=True)
    Observer: Mapped[str] = mapped_column(db.String(80), unique=False, nullable=True)
    NeuentdeckteKleinplaneten: Mapped[str] = mapped_column(db.String(80), unique=False, nullable=True)


class SystemParameters(db.Model):
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    parameter: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(db.String(150), nullable=False)


class SystemParametersHistory(db.Model):
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    parameter: Mapped[str] = mapped_column(db.String(50), unique=False, nullable=False)
    value: Mapped[str] = mapped_column(db.String(50), nullable=True)
    history_reason: Mapped[str] = mapped_column(db.String(1))  # I, U, D
    history_timestamp: Mapped[datetime] = mapped_column(db.DateTime, nullable=True, default=datetime.now(timezone.utc))


class MotivationTypes(db.Model):
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Motivation: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False)

    def __str__(self):
       return f"{self.Motivation}"


class ObjectTypes(db.Model):
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Objecttype: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False)

    def __str__(self):
       return f"{self.Objecttype}"


class ObservationRequestLog(db.Model):
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('observation_request.id'))
    timestamp: Mapped[datetime] = mapped_column(db.DateTime, nullable=True, default=datetime.now(timezone.utc))
    type = db.Column(db.String(10))
    subtype = db.Column(db.String(10))
    text = db.Column(db.String(500))


class CatalogueMeta(db.Model):
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(db.String(100), unique=False, nullable=False)
    source: Mapped[str] = mapped_column(db.String(100), unique=False, nullable=False)
    description: Mapped[str] = mapped_column(db.String(100), unique=False, nullable=False)
    version: Mapped[int] = mapped_column(db.Integer, unique=False, nullable=True)
    license: Mapped[str] = mapped_column(db.String(100), unique=False, nullable=False)
    maintainer: Mapped[str] = mapped_column(db.String(100), unique=False, nullable=False)
    equinoxes: Mapped[str] = mapped_column(db.String(50), unique=False, nullable=False, default='J2000')
    timestamp: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)


class Catalogue(db.Model):
    __table_args__ = {'sqlite_autoincrement': True}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    catalogue_meta_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('catalogue_meta.id'), nullable=False)
    name: Mapped[str] = mapped_column(db.String(30), unique=True, nullable=False)
    long_name: Mapped[str] = mapped_column(db.String(100), unique=False, nullable=True)
    type: Mapped[int] = mapped_column(db.Integer, unique=False, nullable=False)
    ra: Mapped[int] = mapped_column(db.Float, unique=False, nullable=False)
    dec: Mapped[int] = mapped_column(db.Float, unique=False, nullable=False)


'''
statement =
DROP TRIGGER "main"."trg_u_system_parameters";
DROP TRIGGER "main"."trg_d_system_parameters";
DROP TRIGGER "main"."trg_i_system_parameters";

CREATE TRIGGER trg_i_system_parameters AFTER INSERT ON system_parameters
BEGIN
    INSERT INTO system_parameters_history(parameter, value, history_reason, history_timestamp)
    VALUES(NEW.parameter, NEW.value, 'I', CURRENT_TIMESTAMP);
END;

CREATE TRIGGER trg_u_system_parameters AFTER UPDATE ON system_parameters
BEGIN
    INSERT INTO system_parameters_history(parameter, value, history_reason, history_timestamp)
    VALUES(OLD.parameter, OLD.value, 'U', CURRENT_TIMESTAMP);
END;

CREATE TRIGGER trg_d_system_parameters AFTER DELETE ON system_parameters
BEGIN
    INSERT INTO system_parameters_history(parameter, value, history_reason, history_timestamp)
    VALUES(OLD.parameter, OLD.value, 'D', CURRENT_TIMESTAMP);
END;

'''
