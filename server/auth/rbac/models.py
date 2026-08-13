from __future__ import annotations

from dataclasses import dataclass

from models.base.entity import Entity
from models.base.id import Id


@dataclass
class Permission(Entity("key")):  # type: ignore[misc]
    key: str
    description: str | None = None


@dataclass
class Role(Entity("name")):  # type: ignore[misc]
    name: str
    description: str | None = None


@dataclass
class UserRole(Entity()):  # type: ignore[misc]
    user_id: Id
    role_id: Id


@dataclass
class RolePermission(Entity()):  # type: ignore[misc]
    role_id: Id
    permission_id: Id
