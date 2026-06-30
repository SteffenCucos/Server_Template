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
├── db/
├── server_template/
├── requirements.txt
├── pyproject.toml
└── README.md
```

## How to use this template manually

1. Clone or copy the repository.
2. Rename the application/package to match the new service.
3. Add domain models.
4. Add endpoint modules.
5. Wire database interfaces or external integrations.
6. Add tests before using it as a production service.

## Status

Template / starter project.

## License

No license has been selected yet.
