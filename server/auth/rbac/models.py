from __future__ import annotations

from dataclasses import dataclass

from models.base.entity import Entity
from models.base.id import Id


@dataclass
class Permission(Entity("key")):
    key: str
    description: str | None = None


@dataclass
class Role(Entity("name")):
    name: str
    description: str | None = None


@dataclass
class UserRole(Entity()):
    user_id: Id
    role_id: Id


@dataclass
class RolePermission(Entity()):
    role_id: Id
    permission_id: Id
