# Pflichtenheft

Das Pflichtenheft beschreibt die Anforderungen (Requirements) dir wir an unsere Software stellen.

Unterschieden wird zwischen Anforderungen die einen direkten Nutzen ergeben (Geschäftsanforderungen)
und indirekte Anforderungen, die sich als Folge daraus ergeben. Für die indirekten Anforderungen sollte
immer ein Bezug auf ein oder mehr Geschäftsanforderungen oder andere indirekte Anforderungen genannt
werden. Die Trennung ist wichtig, weil es hilft auf das Wesentliche zu fokussieren und das Ziel nicht
zu verlieren indem nutzlose "Features" entwickelt werden!

Jede Anforderung kann dann als Task "abgearbeitet" werden, letztendlich ist es also eine Todo-Liste.

**Wichtig** ist es zunächst alle Geschäftsanforderungen zu definieren. Bei Bedarf gerne gleich auch indirekte
Anforderungen erfassen. Um Referenzieren zu können, bitte laufende Nummern setzen und diese niemals
neu nummerieren!

## Geschäftsanforderungen

Alle Anforderungen mit direktem Nutzen.

### G1: Datenschutz wird eingehalten

### G2: Ein Antrag kann als Draft erstellt werden und enthält folgende Informationen:

- Antragsteller, Email (aus Login übernommen, nicht änderbar)
- Details... TBD
- ...?

### G3: Antrag kann nur eingereicht werden, wenn Termin frei ist

### G4: Der Kalender wird laufend aktualisiert

### G5: Poweruser erhalten eine Email mit Liste geprüfter Anträge

- die Liste enthält alle bis dann gestellten Anträge die noch keinen PU haben
- die Email wird vom Prüfer ausgelöst, wenn alle Anträge geprüft sind

### G6: User haben zugeordente Rollen und verfügbare Funktionen sind entsprechend freigeschaltet
(Beispiel: nur die Rolle Genehmiger, die eine kleine Gruppe von Benutzern hat, kann einen Antrag genehmigen)

### G7: Technische Umsetzung muss einfach sein


## Indirekte Anforderungen

Ergeben sich konkrete weitere Anforderungen aus den Geschäftsanforderungen oder deren technischen
Umsetzung, sind diese hier aufzulisten.

### I1: Login nur für VdS Mitglieder die den Datenschutzrichtlinien und AGB zustimmen (G1)

### I2: Eine Seite mit AGB existiert oder ist verlinkt zur VdS AGB (I1)

### I3: Eine Seite mit Impressum existiert (G1)

### I4: Login ist erst nach Freischaltung nach Prüfung der VdS Mitgliedschaft möglich (I1)

### I5: Nur eingeloggte Benutzer sehen die Anträge

### I8: wir verwenden Frameworks wie Flask, Bootstrap und SQLAlchemy (G7)

- Flask stellt einen Webserver und Routen zur Verfügung (Pfade im Website)
- Bootstrap stellt CSS Definitionen für den HTML Design bereit
- SQLAlchemy abstraphiert Datenbank Befehle in Python Objekte (keine SQL Befehle kodieren)
- weitere...?

