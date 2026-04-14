# Conference Abstract Management

This repository now contains two tracks:

- `conference_abstract/`: the original 2017 Pyramid application, preserved for reference.
- `modern_cam/`: a full Python 3.12 rebuild using Django, SQLite, Docker, and a new interface.

## Modern rebuild

The new app covers:

- submitter registration and secure password-based login
- draft abstract creation with multi-author support
- organizer dashboards for review and copy-edit assignment
- reviewer scoring workflow
- copy editor workflow with edited abstract storage
- public agenda/session management
- signed public links for presenter confirmation, prize choice, and poster upload

## Quick start with Docker

1. Copy the environment template.
2. Start the stack.
3. Open the site on port `8000`.

```bash
cp .env.example .env
docker compose up --build
```

The container entrypoint will:

- run database migrations
- collect static assets
- seed starter topics and a sample session

The Docker setup uses SQLite and persists the app state inside `modern_cam/`.

## Demo users

If you want demo organizer/reviewer/editor accounts in addition to the starter topics:

```bash
docker compose run --rm web python manage.py seed_demo_data --with-demo-users
```

That command creates these accounts with password `change-me-now`:

- `admin@example.org`
- `organizer@example.org`
- `reviewer@example.org`
- `editor@example.org`

## Local development without Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r modern_cam/requirements.txt
python modern_cam/manage.py migrate
python modern_cam/manage.py seed_demo_data --with-demo-users
python modern_cam/manage.py runserver
```

## Important notes

- The new app uses SQLite everywhere.
- The SQLite database lives at [modern_cam/db.sqlite3](/Users/sratnasi/repos/ConferenceAbstractManagement/modern_cam/db.sqlite3).
- Media uploads are stored in `modern_cam/media/`.
- The legacy code remains untouched so the rebuild can be compared against the original implementation during migration planning.

