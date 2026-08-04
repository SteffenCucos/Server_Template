# Auth DI Plan

Plan for moving route authorization checks into the dependency-injection lifecycle while keeping the existing route-level annotations.

## Goal

Keep route code declarative and preserve the current API:

```python
@router.get("/{user_id}")
@authenticated()
@check_permission("read/users/{user_id}")
def get_user(...):
    ...
```

The decorators should declare requirements only. FastAPI should enforce them using injected services.

## Current problem

The current permission decorator constructs persistence and service objects manually during the request.

That makes authorization a side path instead of part of the normal request graph.

Problems:

```text
manual repository creation inside decorator
manual DAO creation inside decorator
manual AuthorizationService creation inside decorator
harder request lifecycle cleanup
harder test setup
harder cache injection
hidden dependency graph
```

## Target design

```text
route decorator        -> metadata only
custom route class     -> notices metadata during route registration
FastAPI dependency     -> enforces requirement during request
AuthorizationService   -> checks access using cached role trees
DAOs/repositories      -> injected through normal dependency lifecycle
```

## Proposed files

```text
server/api/auth/route_permissions.py
server/api/auth/dependencies.py
server/api/auth/route.py
```

The existing public annotation files remain:

```text
server/api/decorators/authenticated.py
server/api/decorators/check_permissions.py
```

## Step 1: Make existing decorators metadata-only

Responsibilities:

```text
authenticated
check_permission
get_auth_required
get_permission_requirement
```

The decorators should only attach metadata to the endpoint function.

They should not:

```text
open repositories
construct DAOs
construct services
read environment settings
perform permission checks
```

Suggested metadata shape:

```text
PermissionRequirement
  permission: str
```

## Step 2: Add enforcement dependencies

Create `dependencies.py`.

Responsibilities:

```text
require_current_user
resolve route permission templates using path params
call AuthorizationService
raise Unauthorized when no user exists
raise Forbidden when the user lacks the required permission
```

The dependency should receive `AuthorizationService` through the normal service dependency provider.

This keeps repository and cache lifetimes in one place.

## Step 3: Add custom route class

Create `route.py`.

The route class should inspect endpoint metadata during route registration.

Behavior:

```text
no metadata          -> public route
authenticated        -> attach current-user dependency
check_permission     -> attach permission-enforcement dependency
```

The point is that route functions stay clean while enforcement is still automatic.

## Step 4: Wire the custom route into Router

Update the project router abstraction so it uses the auth-aware route class by default.

Target:

```text
all generated routers automatically understand auth metadata
no route has to manually add Depends(...) for authorization
public routes remain public unless metadata exists
```

## Step 5: Keep existing route syntax

Permission-protected route:

```python
@router.get("/{user_id}")
@check_permission("read/users/{user_id}")
def get_user(...):
    ...
```

Authentication-only route:

```python
@router.get("/me")
@authenticated()
def get_me(...):
    ...
```

`check_permission(...)` implies authentication, so both decorators are not required on permission-protected routes.

## Step 6: Remove manual auth persistence wiring

After the new path works, delete the old path where `check_permission` creates repositories and DAOs manually.

The replacement should use:

```text
RequestContext or current-user dependency
AuthorizationService dependency
TreeStore dependency or shared service-level store
DAO/repository providers
```

## Step 7: Tests

Unit tests for metadata decorators:

```text
authenticated marks endpoint as auth-required
check_permission stores its permission template
check_permission also marks authentication as required
```

Route tests:

```text
public route has no auth enforcement
authenticated route rejects missing current user
check_permission route rejects missing current user
check_permission route denies missing grant
check_permission route allows matching grant
path params fill permission templates correctly
```

Regression tests:

```text
permission decorator does not open repositories
permission decorator does not instantiate DAOs
permission decorator does not instantiate AuthorizationService
```

## Migration order

```text
PR 1: metadata behavior and tests for existing decorators
PR 2: enforcement dependency and tests
PR 3: custom route class and router wiring
PR 4: migrate request-context creation into DI
PR 5: remove manual repository construction from decorators
PR 6: README examples and generated scaffold docs
```

## Acceptance criteria

```text
existing authenticated and check_permission names remain the public API
route permissions remain visible beside the route function
actual checks run through FastAPI dependency lifecycle
AuthorizationService is injected, not manually created by the decorator
TreeStore can be shared through normal service wiring
public routes stay public by default
auth-only and permission routes are tested separately
```

## Non-goals

This change does not add alternative annotation names, multiple-permission modes, the full RBAC admin API, ownership policies, password hashing, or session expiry. Those should remain separate workstreams.
