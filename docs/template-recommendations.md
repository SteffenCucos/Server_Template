# Template Recommendations

This document tracks the next steps for making the scaffold a stronger reusable server template.

## Current direction

The template now has a useful baseline architecture:

```text
Endpoint
  -> Service
    -> DAO
      -> Repository[TEntity]
        -> MongoRepository | PostgresRepository | SQLiteRepository
```

It also has normalized role models, action-first access keys, a path matcher, and a store keyed by user and role.

## Recommended access key shape

```text
action/path_to_object
```

Examples:

```text
read/users/*
write/users/*
delete/users/*
manage/org/acme/project/**
```

The first segment is the action. The rest is the object path.

## Highest-priority gaps

### 1. Add role and grant management APIs

The models exist, but the scaffold needs APIs or service methods to manage them cleanly.

Useful capabilities:

```text
create role
create access key
attach access key to role
attach role to user
remove role from user
remove access key from role
```

These operations should live behind services instead of routes mutating DAOs directly.

### 2. Wire store invalidation into mutations

The role tree store supports targeted invalidation, but mutation paths still need to call it.

Rules:

```text
user-role assignment changed -> invalidate that user's role list
role grant changed           -> invalidate that role's compiled tree
access key changed           -> invalidate affected role trees
role name changed            -> no access cache invalidation needed
```

Store contract:

```text
missing entry  -> load from persistence and store the result
present entry  -> treat as authoritative for the current check
```

### 3. Validate access key format

Add a reusable validation helper for access keys.

Recommended rules:

```text
must be action/path_to_object
must have at least two path segments
first segment is the action
allowed wildcards are * and **
** should only appear at the end
raw regex should not be accepted
```

A helper like `PermissionKey.validate(...)` would keep validation consistent across services, APIs, seed scripts, and tests.

### 4. Add bootstrap roles

A fresh generated app needs a starting access setup.

Recommended options:

```text
dev-mode seed routine
CLI command for creating an initial admin
generated bootstrap script
```

A minimal seed could create:

```text
admin role
basic user role
admin role with broad manage grants
```

### 5. Keep route decorators, but make them metadata-only

Route-level requirements should stay beside the route because they are route metadata.

Preferred route shape:

```python
@router.get("/{user_id}")
@requires_permission("read/users/{user_id}")
def get_user(user_id: str, user_service: UserServiceDep) -> User:
    ...
```

The decorator should only attach metadata to the endpoint. It should not create repositories, DAOs, or services.

A FastAPI route class or dependency should read the metadata during the request and use injected services to enforce it.

Recommended split:

```text
decorator              -> declares route requirement
custom route/dependency -> enforces requirement
AuthorizationService    -> checks cached role trees
repositories/DAOs       -> managed by FastAPI dependency lifecycle
```

This keeps the route declarative while avoiding manual persistence setup inside decorators.

### 6. Add contextual policies

Role grants answer broad capability questions:

```text
Can this user read users/*?
```

Policies answer contextual questions:

```text
Can this user read this exact user?
Can this team lead read this team member?
Can this org admin manage this project?
```

Do not encode all contextual ownership rules into access strings. Keep them in a policy layer.

### 7. Improve Postgres querying

The generic Postgres repository is useful for scaffolding, but it needs stronger querying before serious usage.

Recommended improvements:

```text
JSONB predicate support
indexes for common lookup fields
or generated concrete tables for first-class entities
```

### 8. Add migrations

The template needs a schema lifecycle story.

Options:

```text
Alembic for SQL backends
backend-specific bootstrap scripts
repository auto-create only for dev/test
```

For a production-leaning template, Alembic should be the default SQL path.

### 9. Improve README examples

The README should show the full happy path:

```text
create user
create role
create access key
attach access key to role
attach role to user
protect route
call route successfully
```

It should also document:

```text
action/path_to_object format
* wildcard
** deep wildcard
store behavior
how to seed an admin
how to choose Mongo, SQLite, or Postgres
```

### 10. Expand CI

CI should run both:

```text
template unit tests
generated scaffold API tests
```

Generated scaffold tests are useful, but they do not replace unit tests for template internals.

## Suggested implementation order

```text
1. Add access key validation
2. Add role/grant service methods and endpoints
3. Wire role tree store invalidation into mutations
4. Add bootstrap admin or dev seed path
5. Convert route decorators to metadata-only decorators with FastAPI-backed enforcement
6. Update README with action/path_to_object examples
7. Improve session handling basics
8. Improve Postgres predicates and indexes
9. Add migrations
10. Add policy layer for contextual checks
```

## Summary

The template has a good foundation: backend-neutral repositories, DAOs, services, normalized access models, action-first keys, and compiled tree matching.

The next step is to make the access workflow usable end-to-end through validation, management APIs, invalidation, bootstrap data, and declarative route metadata backed by FastAPI's lifecycle.
