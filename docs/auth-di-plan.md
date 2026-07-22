# Auth DI Plan

Plan for moving route authorization checks into the dependency-injection lifecycle while keeping route-level decorators as metadata.

## Goal

Keep route code declarative:

```python
@router.get("/{user_id}")
@requires_permission("read/users/{user_id}")
def get_user(...):
    ...
```

But move execution out of the decorator. The decorator should declare the requirement. FastAPI should enforce it using injected services.

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

Optional compatibility file:

```text
server/api/decorators/check_permissions.py
```

The compatibility file can re-export the new decorator or issue a deprecation path.

## Step 1: Add metadata decorators

Create `route_permissions.py`.

Responsibilities:

```text
requires_auth
requires_permission
requires_any_permission
requires_all_permissions
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
  permissions: tuple[str, ...]
  mode: any | all
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
requires_auth        -> attach current-user dependency
requires_permission  -> attach permission-enforcement dependency
```

The point is that route functions stay clean while enforcement is still automatic.

## Step 4: Wire the custom route into Router

Update the project router abstraction so it uses the auth-aware route class by default.

Target:

```text
all generated routers automatically understand permission metadata
no route has to manually add Depends(...) for authorization
public routes remain public unless metadata exists
```

## Step 5: Replace old decorator usage

New preferred usage:

```python
@router.get("/{user_id}")
@requires_permission("read/users/{user_id}")
def get_user(...):
    ...
```

For multiple acceptable permissions:

```python
@router.get("/{user_id}")
@requires_any_permission(
    "read/users/{user_id}",
    "manage/users/**",
)
def get_user(...):
    ...
```

For routes that only require login:

```python
@router.get("/me")
@requires_auth
def get_me(...):
    ...
```

## Step 6: Remove manual auth persistence wiring

After the new path works, delete or deprecate the old path where `check_permission` creates repositories and DAOs manually.

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
requires_auth marks endpoint as auth-required
requires_permission stores permission templates
requires_any_permission stores mode=any
requires_all_permission stores mode=all
```

Route tests:

```text
public route has no auth enforcement
requires_auth route rejects missing current user
requires_permission route rejects missing current user
requires_permission route denies missing grant
requires_permission route allows matching grant
path params fill permission templates correctly
any mode passes when one grant matches
all mode requires every grant to match
```

Regression tests:

```text
permission decorator does not open repositories
permission decorator does not instantiate DAOs
permission decorator does not instantiate AuthorizationService
```

## Migration order

```text
PR 1: metadata decorators and tests
PR 2: enforcement dependency and tests
PR 3: custom route class and router wiring
PR 4: migrate existing routes to requires_permission/requires_auth
PR 5: remove manual repository construction from old decorator path
PR 6: README examples and generated scaffold docs
```

## Acceptance criteria

```text
route permissions remain visible beside the route function
actual checks run through FastAPI dependency lifecycle
AuthorizationService is injected, not manually created by the decorator
TreeStore can be shared through normal service wiring
public routes stay public by default
auth-only and permission routes are tested separately
```

## Non-goals

This change does not implement the full RBAC admin API, ownership policies, password hashing, or session expiry. Those should remain separate workstreams.
