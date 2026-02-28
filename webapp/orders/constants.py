# constants.py

# Stati die eine Beobachtungsanfrage annehmen kann

ORDER_STATUS_CREATED = '0'        # User hat Anfrage erstellt
ORDER_STATUS_WAITING = '1'        # Anfrage wartet auf Bestätigung
ORDER_STATUS_APPROVED = '2'       # Anfrage ist akzeptiert
ORDER_STATUS_REJECTED = '3'       # Anfrage ist abgelehnt
ORDER_STATUS_PU_ASSIGNED = '4'    # Anfrage ist Poweruser zugewiesen
ORDER_STATUS_PU_ACCEPTED = '5'    # Poweruser hat Anfrage akzeptiert
ORDER_STATUS_PU_REJECTED = '6'    # Poweruser hat Anfrage abgelehnt
ORDER_STATUS_CONFIRMED = '7'      # User ist benachrichtigt
ORDER_STATUS_CANCELLED = '8'      # Anfrage ist storniert
ORDER_STATUS_FAILED = '9'         # Auftrag konnte nicht ausgeführt werden
ORDER_STATUS_EXECUTED = '10'      # Auftrag ist ausgeführt
ORDER_STATUS_PICURES_READY = '11' # Die aufgenommenen Bilder sind verfügbar
ORDER_STATUS_DOCUMENTED = '12'    # Auftrag ist abgeschlossen und dokumentiert

ORDER_STATUS_CHOICES = [
    (ORDER_STATUS_CREATED, 'Entwurf'),
    (ORDER_STATUS_WAITING, 'Abgeschickt'),
    (ORDER_STATUS_APPROVED, 'Genehmigt'),
    (ORDER_STATUS_REJECTED, 'Abgelehnt'),
    (ORDER_STATUS_PU_ASSIGNED, 'PU zugewiesen'),
    (ORDER_STATUS_PU_REJECTED, 'PU abgelehnt'),
    (ORDER_STATUS_PU_ACCEPTED, 'PU hat akzeptiert'),
    (ORDER_STATUS_CONFIRMED, 'Akzeptiert'),
    (ORDER_STATUS_CANCELLED, 'Ausgefallen'),
    (ORDER_STATUS_FAILED, 'Fehlerhaft'),
    (ORDER_STATUS_EXECUTED, 'Ausgeführt'),
    (ORDER_STATUS_PICURES_READY, 'Bilder verfügbar'),
    (ORDER_STATUS_DOCUMENTED, 'Dokumentiert')
]

ORDER_STATUS_LABELS = dict(ORDER_STATUS_CHOICES)

# definierte User Rollen
USER_ROLE_ADMIN = 'admin'
USER_ROLE_APPROVER = 'approver'
USER_ROLE_POWERUSER = 'poweruser'
USER_ROLE_USER = 'user'
USER_ROLE_GUEST = 'guest'

USER_ROLE_CHOICES = [
    (USER_ROLE_ADMIN, 'Admin'),
    (USER_ROLE_APPROVER, 'Approver'),
    (USER_ROLE_POWERUSER, 'Poweruser'),
    (USER_ROLE_USER, 'User'),
    (USER_ROLE_GUEST, 'Guest')
]

USER_ROLE_LABELS = dict(USER_ROLE_CHOICES)

# definierte Poweruser Stati
PU_AKTIV = 'AKTIV'
PU_PASSIV = 'PASSIV'

PU_STATUS_CHOICES = [
    (PU_AKTIV, 'aktiv'),
    (PU_PASSIV, 'passiv'),
]

PU_STATUS_LABELS = dict(PU_STATUS_CHOICES)

# Arten der Belegung
RT_OBSERVATION = 'B'
RT_PRESENTATION = 'F'
RT_MAINTENANCE = 'W'
RT_SCIENTIFIC_WORK = 'S'
RT_RESERVED = 'R'
RT_GEORG = 'G'
RT_TEMPLATE = 'M'

REQUEST_CHOICES = [
(RT_OBSERVATION, 'Beobachtung'),
(RT_PRESENTATION, 'Führung' )
]

REQUEST_CHOICES_LABELS = dict(ORDER_STATUS_CHOICES)