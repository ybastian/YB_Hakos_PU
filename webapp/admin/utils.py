from flask_admin.contrib.sqla import ModelView
from flask_admin import expose, AdminIndexView
from flask_admin.menu import MenuLink
from flask import redirect, request, url_for
from flask_login import current_user
from sqlalchemy.orm.collections import InstrumentedList
from webapp.orders.constants import USER_ROLE_ADMIN

# Liste kommagetrennt formatieren
def names(item_list):
    if item_list:
        teststr = item_list[0].name
        for i in item_list[1:]:
            teststr += f", {i.name}"
        return teststr
    else:
        return "None"


def namesX(item):
    if item:
        if isinstance(item, list) or isinstance(item, InstrumentedList):
            teststr = item[0].name
            for i in item[1:]:
                teststr += f", {i.name}"
            return teststr
        elif item:  # Einzelnes Objekt
            return item.name
    return "None"


class GenericModelView(ModelView):
    page_size = 50  # the number of entries to display on the list view
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    column_hide_backrefs = False
    can_export = True

    def is_accessible(self):
        # return current_user.is_authenticated and current_user.has_role("admin")
        return current_user.is_authenticated and current_user.has_role(USER_ROLE_ADMIN)

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('home', next=request.url))

class UserModelView(GenericModelView):
    column_list: tuple[str, ...] = ('name', 'surname', 'firstname', 'email', 'vds_number', 'groups')
    column_exclude_list: tuple[str, ...] = ['password']  # List View
    form_excluded_columns: tuple[str, ...] = ['password']  # Form View
    column_details_exclude_list: tuple[str, ...] = ['password']  # Detail View

    column_descriptions = dict(
        name='Username',
        surname='Nachname',
        firstname="Vorname",
        email="Email",
        vds_number="VdS Nummer",
        groups="Gruppen"
    )

    column_labels = dict(
        name='Username',
        surname='Nachname',
        firstname="Vorname",
        email="Email",
        vds_number="VdS Nummer",
        groups="Gruppen"
    )
    column_formatters = dict(
        groups=(lambda v, c, m, p: names(m.groups)) # format list
    )


class GroupModelView(GenericModelView):
    column_list: tuple[str, ...] = ('name', 'roles')
    column_labels = dict(
         name='Gruppe',
         roles='Rolle'
    )
    column_descriptions = dict(
         name='Die Gruppe fasst mehere Rollen zusammen',
         roles='Die Rolle definiert bestimmte Zugangsrechte'
    )
    column_formatters = dict(
        roles=(lambda v, c, m, p: names(m.roles)) # format list
    )


class RoleModelView(GenericModelView):
    column_list: tuple[str, ...] = ('name', 'groups')
    column_labels = dict(
         name='Rollen (Rechte) Bezeichnung'
    )
    column_descriptions: dict[str, str] = dict(
         name='Die Rolle stellt Recht auf bestimmte Funktionen und Bereiche dar',
         groups='Die Rolle ist bisher diesen Gruppen zugeordnet'
    )
    column_formatters = dict(
        groups=(lambda v, c, m, p: names(m.groups)) # format list
    )


class SiteModelView(GenericModelView):
    column_list: tuple[str, ...] = ('name', 'longitude', 'lattitude', 'observatories')
    column_labels = dict(
         name='Ort',
         longitude='Längengrad',
         lattitude='Breitengrad',
         observatories='Observatorien'
    )
    column_formatters = dict(
        observatories=(lambda v, c, m, p: names(m.observatories)) # format list
    )


class ObservatoryModelView(GenericModelView):
    form_excluded_columns: tuple[str, ...] = ['observation_request']
    column_list: tuple[str, ...] = ('name', 'site', 'telescopes')
    column_labels = dict(
        name='Observatorium',
        site='Ort',
        telescopes='Teleskope'
    )
    column_formatters = dict(
        site=(lambda v, c, m, p: namesX(m.site)),
        telescopes=(lambda v, c, m, p: names(m.telescopes))
    )


class TelescopeModelView(GenericModelView):
    form_excluded_columns: tuple[str, ...] = ['observation_request_position']  # List View
    column_list: tuple[str, ...] =('name', 'aperature_mm', 'focal_length_mm','camera_name','filtersets','observatory', 'status' )
    column_labels = dict(
        name='Bezeichnung',
        aperature_mm='Durchmesser (mm)',
        focal_length_mm='Brennweite (mm)',
        camera_name = 'Kamera',
        status='Status',
        observatory ='Observatorium',
        filtersets = "Filter"
    )
    column_formatters = dict(
        observatory=(lambda v, c, m, p: m.observatory.name if m.observatory else "None")
    )


class ObservationHistoryModelView(GenericModelView):
    can_create = can_create_inline = can_view_details = can_edit = can_delete = False
    column_list: tuple[str, ...] = ( 'Datum', 'Objekt', 'Teleskop', 'Rubrik', 'Bildersteller', 'Observer')
    # column_formatters = dict(
    #     Datum=(lambda v, c, m, p: m.Datum.strftime('%d.%m.%Y'))
    # )

class PowerUserModelView(GenericModelView):
    can_create = can_create_inline = can_view_details = can_edit = can_delete = False
    column_list: tuple[str, ...] = ( 'name', 'email', 'mobilfone', 'fone', 'Einweisung', 'Status')
    column_labels = dict(
        mobilfone='Handy',
        fone='Festnetz'
    )


class SystemParametersModelView(GenericModelView):
    column_list: tuple[str, ...] = ( 'parameter', 'value')
    column_labels = dict(
        parameter='Parameter',
        value='Wert'
    )


class SystemParametersHistoryModelView(GenericModelView):
    can_create = can_create_inline = can_view_details = can_edit = can_delete = False
    column_list:  tuple[str, ...] = ( 'parameter', 'value', 'history_reason','history_timestamp')
    column_labels = dict(
        parameter='Parameter',
        value='Wert',
        history_reason='Insert/Update/Delete',
        history_timestamp='Zeitstempel'
    )


class FiltersetModelView(GenericModelView):
    form_excluded_columns: tuple[str, ...] = ['observation_request_position']  # List View
    column_list: tuple[str, ...] = ( 'name', 'telescope', 'quantity' )
    column_labels = dict(
        name='Filterset',
        telescope='Teleskop',
        quantity='Anzahl Filter im Set'
    )
    column_formatters = dict(
        telescope=(lambda v, c, m, p: m.telescope.name if m.telescope else "None")
    )
    column_descriptions = dict(
         name='Einzelner Filter oder ganze Palette. Anweisung an den Poweruser',
         telescope='ist an dem Teleskop verbaut',
         quantity ='Wert wieviel Belichtungen pro Durchgang erforderlich sind.\n' 
                   'Anzahl Filter pro Set'
    )

class ObjectTypesModelView(GenericModelView):
    column_list: tuple[str, ...] = ('Objecttype',)
    column_labels = {'Objecttype': 'Rubrik'}

class MotivationModelTypesView(GenericModelView):
    column_list: tuple[str, ...] = ('Motivation',)
    column_labels = {'Motivation': 'Motivation'}

class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

class OrderModelView(GenericModelView):
#   column_exclude_list = form_excluded_columns = column_details_exclude_list = ['id']
    form_excluded_columns = ('user_id', 'positions' )
    can_delete = False
    column_list = ( 'name',
                    'date_request',
                    'request_observatory',
                    'request_type',
                    'request_reason',
                    'poweruser_request',
                    'remark',
                    'status',
                    'id'
                    )
    column_labels = dict(
        name='Beteiligte',
        date_request='Wunschdatum',
        request_observatory='Observatorium',
        request_type='Art der Nutzung',
        request_reason='Motivation',
        poweruser_request='Wunsch Poweruser',
        remark='Bemerkungen',
        status='Status',
        id = 'Requester ID'
        )

    column_formatters = dict(
        request_observatory=(lambda v, c, m, p: m.request_observatory_id if m.request_observatory_id else "-"),
        poweruser_request=(lambda v, c, m, p: m.request_poweruser_id if m.request_poweruser_id else "egal"),
    )

    column_descriptions = dict(
        name='Mitwirkende',
        request_type='(B)eobachtung, (F)ührung, (W)artung',
        request_reason='Pritty Pictures, Erfahrung sammeln, Kleinplanetensuche...'
    )

def on_model_change(self, form, model, is_created):
    if is_created:
#        model.user_id = current_user.id
        model.user_id = lambda v, c, m, p: current_user.id
    return super().on_model_change(form, model, is_created)  # type: ignore

class OrderPositionModelView(GenericModelView):
    column_list = ( 'telescope_id',
                    'filterset_id',
                    'target',
                    'target_coordinates',
                    'target_coordinates_lock',
                    'exposure_count',
                    'exposure_time',
                    'exposure_gain',
                    'exposure_offset',
                    'exposure_dither',
                    'exposure_focus'
                    )

    column_labels = dict(
        telescope_id='Teleskop',
        filterset_id='Filter',
        target='Ziel',
        target_coordinates='Position',
        target_coordinates_lock='Koord. fix',
        exposure_count='Anzahl',
        exposure_time='Bel. Zeit',
        exposure_gain='Gain',
        exposure_offset='Offset',
        exposure_dither='Dither',
        exposure_focus='Focus'
    )

    column_formatters = dict(
        telescope_id=(lambda v, c, m, p: m.telescope.name if m.telescope else "-")
    )

    column_descriptions = dict(
        target='Katalogobjekt',
        target_coordinates='Genaue Himmelskoordinaten',
        target_coordinates_lock='Koordinaten beibehalten. z.B. bei Mosaik oder Komet',
        exposure_count='Anzahl gleicher Bilder',
        exposure_time='Belichtungszeit in Sekunden',
        exposure_gain='Gain der Kamera',
        exposure_offset='Offset der Kamera',
        exposure_dither='Dithern alle n Bilder',
        exposure_focus = 'Fokussieren alle n Bilder'
    )

def init_admin(app, admin):
    from webapp import db
    from webapp.model.db import ( User, Group, Role, Poweruser,
                                Site, Observatory, Telescope,
                                Filterset,
                                ObservationHistory,
                                SystemParameters,
                                SystemParametersHistory,
                                ObjectTypes,
                                MotivationTypes,
                                ObservationRequest,
                                ObservationRequestPosition
                                )


    admin.init_app(app, index_view=MyHomeView())

    admin.add_link(MenuLink(name='Home', endpoint='main.home'))

    admin.add_view(UserModelView(User, db.session))
    admin.add_view(GroupModelView(Group, db.session))
    admin.add_view(RoleModelView(Role, db.session))
    admin.add_view(SiteModelView(Site, db.session))
    admin.add_view(ObservatoryModelView(Observatory, db.session))
    admin.add_view(TelescopeModelView(Telescope, db.session))
    admin.add_view(FiltersetModelView(Filterset, db.session))
    admin.add_view(PowerUserModelView(Poweruser, db.session))
    admin.add_view(SystemParametersModelView(SystemParameters, db.session))
    admin.add_view(SystemParametersHistoryModelView(SystemParametersHistory, db.session))
    admin.add_view(MotivationModelTypesView(MotivationTypes, db.session))
    admin.add_view(ObjectTypesModelView(ObjectTypes, db.session))
    admin.add_view(OrderModelView(ObservationRequest, db.session))
    admin.add_view(OrderPositionModelView(ObservationRequestPosition, db.session))
    admin.add_view(ObservationHistoryModelView(ObservationHistory, db.session))

