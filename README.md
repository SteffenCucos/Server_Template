# Server Template

A FastAPI server template with pre-built application structure, backend-neutral persistence, and a CLI scaffolder.

Use this repository as a starting point for small API services that need a clean baseline layout instead of starting from an empty FastAPI project.

## Features

- FastAPI application structure.
- Organized endpoint modules.
- Centralized exception handling pattern.
- CLI scaffolder that clones this template into a new app folder.
- Entity-rooted DB model convention with `_id`, `_created_date`, and `_updated_date` on DB-backed models.
- Backend-neutral repository contract with Mongo, Postgres, and SQLite implementations.
- Entity DAOs that wrap repositories directly and keep shared entity lifecycle rules in one place.
- FastAPI-native dependency providers for request-scoped DAOs and services.

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

## Persistence architecture

The template separates domain persistence behavior from concrete database backends:

```text
Endpoint
  -> Service
    -> DAO
      -> Repository[TEntity]
        -> MongoRepository | PostgresRepository | SQLiteRepository
```

Every DB-backed domain model should inherit from `Entity()` or `IdEntity`, which gives it `_id`, `_created_date`, and `_updated_date`.

```python
from dataclasses import dataclass

from models.base.entity import Entity


@dataclass
class Project(Entity()):
    name: str
```

DAOs are the service-facing persistence layer. The generic `EntityDAO[TEntity]` wraps a backend-neutral `Repository[TEntity]` and owns shared entity lifecycle behavior such as ensuring IDs and updating timestamps before persistence.

```python
from db.entity_dao import EntityDAO
from db.repository import Repository


class ProjectDAO(EntityDAO[Project]):
    def __init__(self, repository: Repository[Project]):
        super().__init__(repository)

    def get_by_name(self, name: str) -> Project | None:
        return self.find_one({"name": name})
```

Concrete repository implementations live under `server/db/backends`. Database connection construction lives under `server/db/connection`, repository selection lives under `server/db/repository_creation`, and FastAPI database wiring lives under `server/db/dependency_wiring`.

Endpoint, service, and DAO code should not use `pymongo`, `psycopg`, SQLAlchemy, collection, cursor, or transaction/session types directly.

## FastAPI dependency injection

Prefer injecting services into endpoints. Services depend on DAOs, and DAOs depend on repositories. Keep `Depends(...)` visible at the point where each dependency is requested instead of hiding it behind type aliases.

```python
from typing import Annotated

from fastapi import Depends
from db.dependency_wiring import repository_dependency
from db.pserialize_entity_serializer import PSerializeEntitySerializer
from db.repository import Repository

get_project_repository = repository_dependency(
    resource_name="projects",
    serializer=PSerializeEntitySerializer(Project),
)


def get_project_dao(
    project_repository: Annotated[Repository[Project], Depends(get_project_repository)],
) -> ProjectDAO:
    return ProjectDAO(project_repository)
```

Then wire the service explicitly as well:

```python
def get_project_service(
    project_dao: Annotated[ProjectDAO, Depends(get_project_dao)],
) -> ProjectService:
    return ProjectService(project_dao)
```

Endpoints should also inline their dependency annotations:

```python
@router.get("/{project_id}")
def get_project(
    project_id: str,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
) -> Project:
    ...
```

The template includes ready-made `UserDAO`, `SessionDAO`, and service dependency providers for the starter user/session routes.

## Database backend selection

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

or:

```bash
APP_DB_BACKEND=sqlite
APP_DB_URI=sqlite:///my_app.db
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
│       ├── connection/
│       │   ├── mongo.py
│       │   ├── postgres.py
│       │   ├── settings.py
│       │   └── sqlite.py
│       ├── dependency_wiring/
│       │   └── repositories.py
│       ├── repository_creation/
│       │   └── factory.py
│       ├── config.py                 # compatibility shim
│       ├── dependencies.py           # compatibility shim
│       ├── entity_dao.py
│       ├── factory.py                # compatibility shim
│       ├── pserialize_entity_serializer.py
│       ├── repository.py
│       ├── session_dao.py
│       └── user_dao.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

## How to use this template manually

1. Clone or copy the repository.
2. Rename the application/package to match the new service.
3. Pick `APP_DB_BACKEND=mongo`, `postgres`, or `sqlite`.
4. Add domain models that inherit from `Entity()`.
5. Add domain DAOs that inherit from `EntityDAO[TEntity]`.
6. Add services that depend on DAOs, not concrete DB drivers.
7. Add endpoint modules that depend on services through FastAPI `Depends(...)` providers.
8. Add tests before using it as a production service.

## Status

Template / starter project.

## License

No license has been selected yet.
