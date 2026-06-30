# Server Template

A FastAPI server template with pre-built folder structure for endpoints, exceptions, models, and database interfaces.

Use this repository as a starting point for small API services that need a clean baseline layout instead of starting from an empty FastAPI project.

## Features

- FastAPI application structure.
- Organized endpoint modules.
- Model and database interface folders.
- Centralized exception handling pattern.
- Dependency file for local setup.
- CLI scaffolder that clones this template into a new app folder.
- Backend-neutral repository and DAO database contracts with Mongo and Postgres implementations.
- FastAPI-native dependency providers for request-scoped repositories and services.

## Scaffold a new app

Install the CLI from GitHub:

```bash
pipx install git+https://github.com/SteffenCucos/Server_Template.git
```

Or install it into your current Python environment:

```bash
pip install git+https://github.com/SteffenCucos/Server_Template.git
```

Create a new app:

```bash
server-template new billing-api
```

This creates `./billing-api`, clones the template, removes the cloned `.git` directory, rewrites the package name, and removes the scaffolder files from the generated app.

Useful options:

```bash
server-template new billing-api --target-dir ./services/billing-api
server-template new billing-api --package-name billing_service
server-template new billing-api --keep-git
server-template new billing-api --keep-cli
server-template new billing-api --force
```

You can also run the CLI as a module from a checkout of this repo:

```bash
python -m server_template new billing-api
```

## Database backend abstraction

The template supports choosing between Mongo/NoSQL and Postgres/SQL without exposing `pymongo`, `psycopg`, SQLAlchemy, collection, cursor, session, or bulk-update types to endpoint/service/DAO code.

For repository-style code, depend on the neutral repository protocol under the template app package:

```python
from server.db import MappingSerializer, Repository, create_repository
from server.db.config import DatabaseSettings

settings = DatabaseSettings.from_env()
users: Repository[dict] = create_repository(
    settings=settings,
    resource_name="users",
    serializer=MappingSerializer(),
)

users.create({"id": "user-1", "email": "user@example.com"})
```

Prefer FastAPI dependency injection at the endpoint boundary. Existing typed aliases can be used directly:

```python
from server.db.dependencies import UserRepository

@router.get("/users")
def list_users(users: UserRepository):
    return users.list(limit=100)
```

For custom models, create a request-scoped repository dependency once and reuse it:

```python
from typing import Annotated

from fastapi import Depends
from server.db import Repository
from server.db.dependencies import PSerializeEntitySerializer, repository_dependency

ProjectRepository = Annotated[
    Repository[Project],
    Depends(repository_dependency(
        resource_name="projects",
        serializer=PSerializeEntitySerializer(Project),
    )),
]

@router.get("/projects")
def list_projects(projects: ProjectRepository):
    return projects.list(limit=100)
```

For existing DAO-style code, `BaseDAO` depends on a generic `Database` facade instead of a Mongo collection:

```python
from server.db.base_dao import BaseDAO
from server.db.config import DatabaseSettings

settings = DatabaseSettings.from_env()
users = BaseDAO(
    classType=User,
    resource_name="users",
    settings=settings,
)
```

`Database` maps the same primitive operations to Mongo or Postgres internally:

```python
db.save(record)
db.save_many(records)
db.update(DatabaseUpdate(entity_id="entity-id", values={"field": "value"}))
db.update_many(updates)
db.find_all()
db.find_one({"email": "user@example.com"})
db.close()
```

Select the backend with environment variables:

```bash
APP_DB_BACKEND=mongo
APP_DB_URI=mongodb://localhost:27017
APP_DB_NAME=my_app
```

or:

```bash
APP_DB_BACKEND=postgres
APP_DB_URI=postgresql://postgres:postgres@localhost:5432/my_app
APP_DB_NAME=my_app
```

The repository interface intentionally only exposes application entities and primitive Python values:

```python
repo.create(entity)
repo.get_by_id("entity-id")
repo.find_one({"email": "user@example.com"})
repo.list(limit=100, offset=0)
repo.update("entity-id", {"field": "value"})
repo.delete("entity-id")
repo.close()
```

Concrete backend classes live under `server.db.backends` and handle their own connections internally:

- `MongoRepository` connects to Mongo and maps public `id` to Mongo `_id` internally.
- `PostgresRepository` connects to Postgres and stores records as `id TEXT PRIMARY KEY` plus JSONB payload by default.

The DAO-facing `Database` facade also handles its own connections internally:

- Mongo maps DAO records to a collection and stores the configured id field as Mongo `_id`.
- Postgres maps DAO records to `id TEXT PRIMARY KEY` plus JSONB payload.

For domain models, implement `EntitySerializer[T]` so repositories can convert between your app objects and backend-neutral records.

## Setup this template repo locally

Install dependencies from the repository root:

```bash
pip install -r requirements.txt
```

Run the development server:

```bash
uvicorn main:app --reload
```

If the application entry point differs, replace `main:app` with the correct module path.

## Suggested project structure

```text
.
├── endpoints/
├── exceptions/
├── models/
├── server/
│   └── db/
│       ├── backends/
│       ├── base_dao.py
│       ├── config.py
│       ├── database.py
│       ├── dependencies.py
│       ├── factory.py
│       └── repository.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

## How to use this template manually

1. Clone or copy the repository.
2. Rename the application/package to match the new service.
3. Pick `APP_DB_BACKEND=mongo` or `APP_DB_BACKEND=postgres`.
4. Add domain models and serializers.
5. Add endpoint modules that depend on `Repository[T]`, `BaseDAO[T]`, or `Database`, not concrete DB drivers.
6. Prefer FastAPI `Depends(...)` providers for repositories and services.
7. Add tests before using it as a production service.

## Status

Template / starter project.

## License

No license has been selected yet.
