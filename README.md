# Wochenmail

Sendet einmal pro Woche eine automatisch formatierte E-Mail mit den Veranstaltungen der kommenden Woche.

Der Versand läuft über GitHub Actions ([`.github/workflows/wochenmail.yml`](.github/workflows/wochenmail.yml)). Der Workflow startet jeden Montag kurz nach Mitternacht (Europe/Berlin) und kann zusätzlich manuell über **Actions → Wochenmail → Run workflow** ausgelöst werden.

> **Hinweis:** GitHub deaktiviert geplante Workflows nach 60 Tagen ohne Aktivität im Repository. Der Workflow muss dann unter **Actions** wieder aktiviert werden.

## Einrichtung auf GitHub

Unter **Settings → Secrets and variables → Actions** anlegen:

### Secrets (erforderlich)

| Name            | Beschreibung             |
| --------------- | ------------------------ |
| `SMTP_HOST`     | SMTP-Server              |
| `SMTP_PORT`     | SMTP-Port (Standard: 587) |
| `SMTP_USER`     | SMTP-Benutzername        |
| `SMTP_PASSWORD` | SMTP-Passwort            |

### Variablen (optional)

| Name           | Standard                                        | Beschreibung                                  |
| -------------- | ----------------------------------------------- | --------------------------------------------- |
| `MAIL_TO`      | `Aktivitas <ac@avfrisia.de>`                    | Empfänger, mehrere durch Komma getrennt       |
| `MAIL_FROM`    | `Consenior der AV Frisia <xx@avfrisia.de>`      | Absender                                      |
| `CALENDAR_URL` | Export-URL des Internen Bereichs                | URL des iCal-Feeds                            |

## Lokal ausführen

Empfohlen ist [`uv`](https://docs.astral.sh/uv/), um die Python-Pakete zu installieren bzw. auszuführen:

```
export SMTP_HOST=...
export SMTP_PORT=587
export SMTP_USER=...
export SMTP_PASSWORD=...
uv run .
```

## Mit Docker

Der Container führt die Wochenmail einmalig aus:

```
docker compose run --rm --build mailer
```

Dafür die SMTP-Zugangsdaten in einer `.env`-Datei hinterlegen (siehe Variablen oben).

Der bisherige Dauerbetrieb mit `docker compose up --detach` ist nicht mehr nötig und sollte gestoppt werden.
